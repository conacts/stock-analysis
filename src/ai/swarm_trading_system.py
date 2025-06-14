"""
Lightweight Swarm Trading System
A custom multi-agent trading system without heavy ML dependencies
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from src.db.swarm_db import SwarmDatabase
from src.llm.deepseek_analyzer import DeepSeekAnalyzer
from src.models.swarm_models import SwarmConversation, TradingDecision

logger = logging.getLogger(__name__)


class LLMWrapper:
    """Wrapper to make DeepSeekAnalyzer compatible with our agent system"""

    def __init__(self, analyzer: DeepSeekAnalyzer):
        self.analyzer = analyzer

    def generate_response(self, prompt: str) -> str:
        """Generate response using DeepSeek analyzer"""
        try:
            # Use the analyzer's API call method directly
            response = self.analyzer._make_api_call(messages=[{"role": "user", "content": prompt}], temperature=0.7, max_tokens=1000)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"


@dataclass
class Agent:
    """Lightweight agent implementation"""

    name: str
    system_prompt: str
    llm: Any
    tools: List[Callable] = None

    def __post_init__(self):
        if self.tools is None:
            self.tools = []


class AgentRearrange:
    """Lightweight agent orchestration system"""

    def __init__(self, agents: List[Agent], max_loops: int = 3):
        self.agents = {agent.name: agent for agent in agents}
        self.max_loops = max_loops
        self.conversation_history = []

    def run(self, task: str, agent_name: str = None) -> Dict[str, Any]:
        """Execute task with agent coordination"""
        try:
            # Start with specified agent or first agent
            current_agent_name = agent_name or list(self.agents.keys())[0]

            responses = []
            turns_used = 0

            for turn in range(self.max_loops):
                turns_used += 1
                current_agent = self.agents[current_agent_name]

                # Create context for the agent
                context = self._build_context(task, responses)

                # Get response from current agent
                response = self._get_agent_response(current_agent, context)
                responses.append({"agent": current_agent_name, "message": response, "turn": turn + 1})

                # Determine next agent or if we're done
                next_agent = self._determine_next_agent(current_agent_name, response, turn)

                if next_agent is None or next_agent == current_agent_name:
                    # Task complete or staying with same agent
                    break

                current_agent_name = next_agent

            return {"agent_responses": responses, "final_agent": current_agent_name, "turns_used": turns_used, "success": True}

        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            return {"agent_responses": [{"agent": "system", "message": f"Error: {str(e)}"}], "final_agent": "system", "turns_used": 1, "success": False}

    def _build_context(self, task: str, responses: List[Dict]) -> str:
        """Build context string for agent"""
        context = f"Task: {task}\n\n"

        if responses:
            context += "Previous agent responses:\n"
            for resp in responses:
                context += f"- {resp['agent']}: {resp['message']}\n"
            context += "\n"

        return context

    def _get_agent_response(self, agent: Agent, context: str) -> str:
        """Get response from an agent"""
        try:
            # Combine system prompt with context
            full_prompt = f"{agent.system_prompt}\n\n{context}"

            # Use the agent's LLM to generate response
            response = agent.llm.generate_response(full_prompt)
            return response

        except Exception as e:
            logger.error(f"Error getting response from agent {agent.name}: {e}")
            return f"Agent {agent.name} encountered an error: {str(e)}"

    def _determine_next_agent(self, current_agent: str, response: str, turn: int) -> Optional[str]:
        """Determine which agent should respond next"""
        # Simple routing logic based on agent names and response content
        agent_names = list(self.agents.keys())

        # If we're at max turns, stop
        if turn >= self.max_loops - 1:
            return None

        # Simple round-robin with some intelligence
        if "analysis" in response.lower() and current_agent != "risk_manager":
            return "risk_manager"
        elif "risk" in response.lower() and current_agent != "trader":
            return "trader"
        elif "trade" in response.lower() and current_agent != "portfolio_manager":
            return "portfolio_manager"

        # Default: move to next agent in list
        try:
            current_idx = agent_names.index(current_agent)
            next_idx = (current_idx + 1) % len(agent_names)
            return agent_names[next_idx]
        except (ValueError, IndexError):
            return None


class SwarmTradingSystem:
    """Lightweight multi-agent trading system"""

    def __init__(self, db: SwarmDatabase, deepseek_analyzer: DeepSeekAnalyzer = None):
        self.db = db
        self.deepseek_analyzer = deepseek_analyzer or DeepSeekAnalyzer()
        self.llm_client = LLMWrapper(self.deepseek_analyzer)
        self.swarm = self._create_swarm()
        logger.info("SwarmTradingSystem initialized with lightweight agents")

    def _create_swarm(self) -> AgentRearrange:
        """Create the multi-agent swarm"""

        # Market Analyst Agent
        market_analyst = Agent(
            name="market_analyst",
            system_prompt="""You are a Market Analyst AI. Your role is to:
1. Analyze market conditions and trends
2. Evaluate individual stocks and sectors
3. Provide data-driven insights about market opportunities
4. Consider macroeconomic factors affecting markets

Provide clear, concise analysis with specific recommendations.""",
            llm=self.llm_client,
        )

        # Risk Manager Agent
        risk_manager = Agent(
            name="risk_manager",
            system_prompt="""You are a Risk Manager AI. Your role is to:
1. Assess portfolio risk and exposure
2. Evaluate position sizing and diversification
3. Monitor risk metrics and compliance
4. Recommend risk mitigation strategies

Always prioritize capital preservation and risk-adjusted returns.""",
            llm=self.llm_client,
        )

        # Trader Agent
        trader = Agent(
            name="trader",
            system_prompt="""You are a Trader AI. Your role is to:
1. Execute trading decisions based on analysis
2. Determine optimal entry and exit points
3. Manage order execution and timing
4. Monitor market liquidity and execution costs

Focus on practical execution of trading strategies.""",
            llm=self.llm_client,
        )

        # Portfolio Manager Agent
        portfolio_manager = Agent(
            name="portfolio_manager",
            system_prompt="""You are a Portfolio Manager AI. Your role is to:
1. Oversee overall portfolio strategy and allocation
2. Balance risk and return objectives
3. Coordinate between different agents
4. Make final investment decisions

Ensure all decisions align with portfolio objectives and constraints.""",
            llm=self.llm_client,
        )

        agents = [market_analyst, risk_manager, trader, portfolio_manager]
        return AgentRearrange(agents=agents, max_loops=4)

    async def analyze_portfolio(self, portfolio_id: str, user_message: str) -> Dict[str, Any]:
        """Analyze portfolio using multi-agent system"""
        try:
            # Get or create portfolio configuration
            config = self.db.get_portfolio_config(portfolio_id)
            if not config:
                # Create default portfolio config
                config = self.db.get_default_portfolio_config(portfolio_id)
                self.db.save_portfolio_config(config)
                logger.info(f"Created default portfolio config for {portfolio_id}")

            # Create analysis task
            task = f"""
Portfolio Analysis Request:
Portfolio: {config.name} (ID: {portfolio_id})
Symbols: {', '.join(config.symbols)}
Risk Tolerance: {config.risk_tolerance}
User Message: {user_message}

Please provide a comprehensive analysis and recommendations.
"""

            # Run swarm analysis
            result = self.swarm.run(task, agent_name="market_analyst")

            # Save conversation
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            conversation = SwarmConversation(portfolio_id=portfolio_id, conversation_id=conversation_id, user_message=user_message, agent_responses=result["agent_responses"], final_agent=result["final_agent"], turns_used=result["turns_used"], success=result["success"])

            self.db.save_conversation(conversation)

            return {"conversation_id": conversation_id, "analysis": result, "portfolio_config": {"portfolio_id": config.portfolio_id, "name": config.name, "symbols": config.symbols, "risk_tolerance": config.risk_tolerance}}

        except Exception as e:
            logger.error(f"Error in portfolio analysis: {e}")
            # Return a graceful error response
            return {"conversation_id": f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}", "analysis": {"success": False, "agent_responses": [{"agent": "system", "message": f"Error: {str(e)}"}], "final_agent": "system", "turns_used": 0}, "portfolio_config": None}

    async def make_trading_decision(self, conversation_id: str, portfolio_id: str) -> Optional[TradingDecision]:
        """Extract trading decision from conversation"""
        try:
            # Get conversation history
            conversations = self.db.get_conversation_history(portfolio_id, limit=1)
            if not conversations or conversations[0].conversation_id != conversation_id:
                raise ValueError(f"Conversation {conversation_id} not found")

            conversation = conversations[0]

            # Extract trading decision from final agent response
            final_response = None
            for response in conversation.agent_responses:
                if response["agent"] == conversation.final_agent:
                    final_response = response["message"]
                    break

            if not final_response:
                return None

            # Simple decision extraction (in production, this would be more sophisticated)
            decision = self._extract_decision_from_response(final_response, conversation_id, portfolio_id)

            if decision:
                self.db.save_trading_decision(decision)

            return decision

        except Exception as e:
            logger.error(f"Error making trading decision: {e}")
            return None

    def _extract_decision_from_response(self, response: str, conversation_id: str, portfolio_id: str) -> Optional[TradingDecision]:
        """Extract trading decision from agent response"""
        try:
            # Simple keyword-based extraction
            response_lower = response.lower()

            if "buy" in response_lower:
                decision_type = "buy"
            elif "sell" in response_lower:
                decision_type = "sell"
            elif "hold" in response_lower:
                decision_type = "hold"
            else:
                return None

            # Extract symbol (simplified)
            symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
            symbol = None
            for sym in symbols:
                if sym.lower() in response_lower:
                    symbol = sym
                    break

            if not symbol:
                symbol = "UNKNOWN"

            return TradingDecision(
                conversation_id=conversation_id,
                portfolio_id=portfolio_id,
                decision_type=decision_type,
                symbol=symbol,
                quantity=10.0,  # Default quantity
                price=0.0,  # Would be filled by market data
                reasoning=response[:500],  # Truncate reasoning
                confidence_score=0.7,  # Default confidence
            )

        except Exception as e:
            logger.error(f"Error extracting decision: {e}")
            return None


# Factory function for easy initialization
def create_swarm_trading_system(db: SwarmDatabase, deepseek_analyzer: DeepSeekAnalyzer = None) -> SwarmTradingSystem:
    """Create and return a SwarmTradingSystem instance"""
    return SwarmTradingSystem(db=db, deepseek_analyzer=deepseek_analyzer)
