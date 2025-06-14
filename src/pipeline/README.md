q# 🔄 Automated Research Pipeline

**Orchestrates the complete research workflow from screening to decision making with trigger-based automation**

## 📁 Module Structure

```
pipeline/
├── __init__.py              # Module initialization
├── research_engine.py       # ResearchEngine, StockScreener, ResearchTrigger classes
└── README.md               # This documentation
```

## 🎯 Overview

The `pipeline` module contains the automated research engine that orchestrates the complete stock research workflow. It handles stock screening, batch analysis, decision making, and trigger-based automation.

## 🏗️ Core Components

### 1. StockScreener Class

**Purpose:** Advanced stock screening and filtering capabilities

### 2. ResearchEngine Class

**Purpose:** Main orchestration engine for the research pipeline

### 3. ResearchTrigger Class

**Purpose:** Automated trigger system for scheduled research

## 📊 StockScreener Class

### Initialization

```python
from src.pipeline.research_engine import StockScreener

screener = StockScreener()
```

### Stock Universe Management

#### Available Universes

```python
def get_stock_universe(self, strategy: str = 'sp500') -> List[str]
```

**Supported Strategies:**

-   **`sp500`** - S&P 500 stocks (50 major stocks)
-   **`nasdaq100`** - NASDAQ 100 technology stocks (32 stocks)
-   **`growth`** - High-growth companies (32 stocks)
-   **`value`** - Undervalued opportunities (27 stocks)
-   **`mega_cap`** - >$500B market cap (8 stocks)
-   **`ai_stocks`** - AI-focused companies (24 stocks)

**Example:**

```python
# Get growth stock universe
growth_stocks = screener.get_stock_universe('growth')
print(f"Growth universe: {len(growth_stocks)} stocks")
# Output: ['NVDA', 'AMD', 'GOOGL', 'MSFT', 'AMZN', ...]
```

#### Universe Details

**S&P 500 Universe (50 stocks):**

```python
['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'BRK-B', 'META', 'TSLA',
 'UNH', 'JNJ', 'JPM', 'V', 'PG', 'HD', 'MA', 'ABBV', 'PFE', 'KO',
 'AVGO', 'COST', 'PEP', 'TMO', 'MRK', 'BAC', 'NFLX', 'CRM', 'DHR',
 'ABT', 'ORCL', 'VZ', 'ADBE', 'WMT', 'LLY', 'CSCO', 'ACN', 'NKE',
 'XOM', 'DIS', 'MDT', 'CVX', 'WFC', 'BMY', 'QCOM', 'NEE', 'TXN',
 'UPS', 'AMGN', 'HON', 'T', 'SBUX', 'LOW', 'RTX', 'INTU', 'PM']
```

**AI Stocks Universe (24 stocks):**

```python
['NVDA', 'AMD', 'GOOGL', 'MSFT', 'AMZN', 'META', 'CRM', 'ORCL',
 'PLTR', 'AI', 'SNOW', 'DDOG', 'CRWD', 'ZS', 'NET', 'SMCI',
 'AVGO', 'QCOM', 'INTC', 'MU', 'LRCX', 'KLAC', 'AMAT', 'MRVL']
```

### Advanced Filtering

#### Apply Filters

```python
def apply_filters(self, symbols: List[str], filters: Dict) -> List[str]
```

**Filter Parameters:**

-   `min_market_cap` - Minimum market capitalization
-   `max_market_cap` - Maximum market capitalization
-   `min_pe` - Minimum P/E ratio
-   `max_pe` - Maximum P/E ratio
-   `min_roe` - Minimum return on equity
-   `min_revenue_growth` - Minimum revenue growth rate
-   `sectors` - List of allowed sectors

**Example:**

```python
# Define growth stock filters
filters = {
    'min_revenue_growth': 0.15,  # 15% minimum growth
    'min_market_cap': 10e9,      # $10B minimum market cap
    'max_pe': 50,                # P/E ratio under 50
    'sectors': ['Technology', 'Healthcare']
}

# Apply filters to universe
growth_universe = screener.get_stock_universe('growth')
filtered_stocks = screener.apply_filters(growth_universe, filters)
print(f"Filtered from {len(growth_universe)} to {len(filtered_stocks)} stocks")
```

## 🚀 ResearchEngine Class

### Initialization

```python
from src.pipeline.research_engine import ResearchEngine

engine = ResearchEngine()
# Or with custom database path
engine = ResearchEngine("custom/path/analysis.db")
```

### Main Research Pipeline

#### Run Daily Research

```python
async def run_daily_research(self, strategy: str = 'growth', max_stocks: int = 50) -> Dict
```

**Complete 8-Step Research Process:**

1. **Get Stock Universe** - Load stocks based on strategy
2. **Apply Filters** - Screen stocks using strategy-specific filters
3. **Limit for Performance** - Cap analysis for reasonable execution time
4. **Analyze Stocks** - Run comprehensive analysis on each stock
5. **Rank and Select** - Choose top picks based on composite scores
6. **Generate Reasoning** - Create investment thesis and decision logic
7. **Store Results** - Save analysis and decisions to database
8. **Generate Report** - Create comprehensive research report

**Example:**

```python
import asyncio

# Run growth strategy research
report = await engine.run_daily_research('growth', 25)

print(f"Strategy: {report['strategy']}")
print(f"Top picks: {len(report['top_picks'])}")
print(f"Average score: {report['summary']['avg_score']:.1f}")
```

### Research Pipeline Components

#### 1. Stock Analysis Batch Processing

```python
async def _analyze_stock_batch(self, symbols: List[str]) -> List[Dict]
```

**Features:**

-   **Asynchronous Processing** - Efficient batch analysis
-   **Error Handling** - Graceful failure handling for individual stocks
-   **Rate Limiting** - 0.1 second delay between API calls
-   **Progress Tracking** - Real-time progress logging

#### 2. Top Pick Selection

```python
def _select_top_picks(self, analysis_results: List[Dict], top_n: int = 5) -> List[Dict]
```

**Selection Criteria:**

-   **Quality Threshold** - Minimum score of 60/100
-   **Score-Based Ranking** - Sorted by composite score
-   **Top N Selection** - Returns best N stocks or all quality picks

#### 3. Decision Reasoning Generation

```python
def _generate_decision_reasoning(self, top_picks: List[Dict], strategy: str) -> Dict
```

**Reasoning Components:**

-   **Quantitative Summary** - Average scores, sector distribution
-   **Qualitative Insights** - Strength analysis, growth themes
-   **Risk Assessment** - Overall risk profile
-   **Strategy Alignment** - How picks align with chosen strategy

**Example Output:**

```python
{
    'reasoning': 'Selected 3 stocks using growth strategy. Average composite score: 72.4/100. Sectors represented: Technology, Healthcare. 2 stocks show strong revenue growth (>15%).',
    'selected_stocks': [
        {
            'symbol': 'NVDA',
            'score': 78.5,
            'rating': 'Buy',
            'sector': 'Technology',
            'key_strengths': ['Excellent ROE', 'Strong revenue growth'],
            'risk_level': 'Moderate'
        }
    ]
}
```

### Strategy-Specific Filters

#### Predefined Filter Sets

```python
def _get_strategy_filters(self, strategy: str) -> Optional[Dict]
```

**Growth Strategy Filters:**

```python
'growth': {
    'min_revenue_growth': 0.10,  # 10% minimum growth
    'min_market_cap': 1e9        # $1B minimum market cap
}
```

**Value Strategy Filters:**

```python
'value': {
    'max_pe': 20,               # P/E under 20
    'min_roe': 0.10,           # ROE above 10%
    'min_market_cap': 5e9      # $5B minimum market cap
}
```

**Quality Strategy Filters:**

```python
'quality': {
    'min_roe': 0.15,           # ROE above 15%
    'max_debt_to_equity': 0.5, # Low debt levels
    'min_market_cap': 10e9     # $10B minimum market cap
}
```

### Research Report Generation

#### Comprehensive Report Structure

```python
def _generate_research_report(self, top_picks: List[Dict], decision_summary: Dict, strategy: str) -> Dict
```

**Report Components:**

**Summary Section:**

-   Date and strategy
-   Total picks and average score
-   Sector representation
-   Investment reasoning

**Detailed Pick Analysis:**

-   Company information
-   Financial metrics
-   Upside potential calculation
-   Key strengths and risks
-   Allocation and time horizon

**Market Insights:**

-   Dominant sectors
-   Risk level assessment
-   Growth focus analysis
-   Market sentiment

**Recommended Actions:**

-   Immediate investment actions
-   Monitoring recommendations
-   Risk management suggestions

### LLM Integration

#### Generate LLM Prompt

```python
def generate_llm_prompt(self, research_report: Dict) -> str
```

**Creates structured prompt for language model analysis:**

-   Research report summary
-   Individual stock details
-   Key metrics and ratios
-   Requests for deeper insights

**Example Prompt Structure:**

```
Analyze this stock research report and provide deeper insights:

Date: 2024-01-15
Strategy: growth

Summary:
- Total picks: 3
- Average score: 72.4/100
- Sectors: Technology, Healthcare
- Reasoning: Selected 3 growth stocks with strong fundamentals...

Top Picks:
NVDA (NVIDIA Corporation):
- Score: 78.5/100, Rating: Buy
- Price: $142.94, Target: $172.00
- Upside: 20.3%
- Key metrics: PE 65.8, ROE 115.5%
- Strengths: Excellent ROE, Strong revenue growth

Please provide:
1. Market trend analysis based on these selections
2. Risk assessment and portfolio allocation suggestions
3. Timing considerations for entry/exit
4. Alternative stocks to consider
5. Overall investment thesis
```

## 🔔 ResearchTrigger Class

### Initialization

```python
from src.pipeline.research_engine import ResearchTrigger

trigger = ResearchTrigger(engine)
```

### Automated Triggers

#### Daily Research Trigger

```python
async def daily_trigger(self, strategy: str = 'growth')
```

**Purpose:** Automated daily research execution
**Features:**

-   **Scheduled Execution** - Can be run via cron or scheduler
-   **Error Handling** - Graceful failure handling
-   **Logging** - Comprehensive execution logging
-   **Result Validation** - Checks for successful completion

**Example:**

```python
# Run daily trigger
report = await trigger.daily_trigger('growth')

if report:
    print("✅ Daily research completed successfully")
    print(f"Found {len(report['top_picks'])} top picks")
else:
    print("❌ Daily research failed")
```

#### Future Trigger Types

```python
def market_hours_trigger(self):
    # Real-time market monitoring
    pass

def news_event_trigger(self, event_type: str):
    # News-based research triggers
    pass
```

## 🔧 Usage Examples

### Complete Research Workflow

```python
import asyncio
from src.pipeline.research_engine import ResearchEngine

async def daily_research_workflow():
    engine = ResearchEngine()

    # Run research for different strategies
    strategies = ['growth', 'value', 'ai_stocks']

    for strategy in strategies:
        print(f"\n🔍 Running {strategy} research...")

        report = await engine.run_daily_research(strategy, 20)

        if 'error' not in report:
            print(f"✅ {strategy}: {len(report['top_picks'])} picks")
            print(f"   Average score: {report['summary']['avg_score']:.1f}")

            # Generate LLM prompt for deeper analysis
            llm_prompt = engine.generate_llm_prompt(report)

            # Save prompt for external LLM analysis
            with open(f"output/{strategy}_prompt.txt", 'w') as f:
                f.write(llm_prompt)
        else:
            print(f"❌ {strategy} research failed: {report['error']}")

# Run the workflow
asyncio.run(daily_research_workflow())
```

### Custom Screening

```python
from src.pipeline.research_engine import StockScreener, ResearchEngine

async def custom_screening_example():
    screener = StockScreener()
    engine = ResearchEngine()

    # Start with AI stocks universe
    ai_universe = screener.get_stock_universe('ai_stocks')

    # Apply custom filters for high-quality AI stocks
    quality_filters = {
        'min_market_cap': 50e9,    # $50B+ market cap
        'min_roe': 0.20,           # 20%+ ROE
        'max_pe': 30               # P/E under 30
    }

    filtered_stocks = screener.apply_filters(ai_universe, quality_filters)
    print(f"Filtered AI stocks: {filtered_stocks}")

    # Analyze the filtered stocks
    results = []
    for symbol in filtered_stocks:
        analysis = engine.analyzer.analyze_stock(symbol)
        if analysis and analysis['score']['composite_score'] >= 70:
            results.append(analysis)

    # Sort by score
    results.sort(key=lambda x: x['score']['composite_score'], reverse=True)

    print(f"\nTop Quality AI Stocks:")
    for result in results[:5]:
        print(f"{result['symbol']}: {result['score']['composite_score']:.1f}")

asyncio.run(custom_screening_example())
```

### Performance Monitoring

```python
async def monitor_recommendations():
    engine = ResearchEngine()

    # Get historical performance
    performance = engine.get_historical_performance()

    print("📈 Portfolio Performance:")
    print(f"Active positions: {performance.get('total_positions', 0)}")
    print(f"Average return: {performance.get('average_return', 0):.2f}%")

    # Update performance for active positions
    for position in performance.get('active_positions', []):
        symbol = position['symbol']
        # Get current price and update performance
        # This would integrate with real-time data source
        print(f"{symbol}: {position.get('return_pct', 0):+.2f}%")

asyncio.run(monitor_recommendations())
```

## 🎯 Key Features

### Automated Workflow

-   **End-to-End Pipeline** - Complete research automation
-   **Strategy-Based Analysis** - Multiple investment strategies
-   **Quality Filtering** - Ensures only quality picks
-   **Decision Tracking** - Comprehensive reasoning storage

### Scalable Architecture

-   **Asynchronous Processing** - Efficient batch operations
-   **Modular Design** - Easy to extend and modify
-   **Error Resilience** - Graceful handling of failures
-   **Performance Optimized** - Rate limiting and efficient queries

### Intelligence Integration

-   **LLM-Ready Outputs** - Structured prompts for AI analysis
-   **Rich Context** - Comprehensive data for decision making
-   **Historical Tracking** - Pattern analysis and learning
-   **Market Insights** - Sector and trend analysis

### Flexible Configuration

-   **Multiple Universes** - Various stock selection strategies
-   **Custom Filters** - Configurable screening criteria
-   **Adjustable Parameters** - Tunable for different use cases
-   **Strategy Templates** - Pre-built investment strategies

## 🔍 Data Flow

### Research Pipeline Flow

```
Trigger Activation
    ↓
Stock Universe Selection (Strategy-based)
    ↓
Filter Application (Quality screening)
    ↓
Batch Stock Analysis (Core analyzer)
    ↓
Top Pick Selection (Score-based ranking)
    ↓
Decision Reasoning (Investment thesis)
    ↓
Data Storage (SQLite persistence)
    ↓
Report Generation (Comprehensive output)
    ↓
LLM Prompt Creation (AI-ready analysis)
```

### Integration Points

-   **Core Analyzer** - Individual stock analysis
-   **Data Storage** - Persistent decision tracking
-   **External APIs** - Yahoo Finance data
-   **LLM Systems** - AI-powered insights
-   **Scheduling Systems** - Automated execution

## 🚀 Future Enhancements

### Advanced Screening

-   **Dynamic Universes** - Real-time universe updates
-   **ML-Based Filtering** - Machine learning screening
-   **Sector Rotation** - Dynamic sector allocation
-   **Risk-Adjusted Screening** - Volatility-based filtering

### Real-time Capabilities

-   **Live Data Integration** - Real-time price updates
-   **Intraday Analysis** - Multiple daily runs
-   **Event-Driven Triggers** - News and earnings triggers
-   **Market Condition Adaptation** - Dynamic strategy adjustment

### Enhanced Intelligence

-   **Predictive Analytics** - Future performance prediction
-   **Sentiment Integration** - Social media sentiment
-   **Alternative Data** - Satellite, credit card data
-   **Options Flow Analysis** - Derivatives market insights

### Platform Integration

-   **API Endpoints** - RESTful API for external access
-   **Webhook Support** - Real-time notifications
-   **Cloud Deployment** - Scalable cloud execution
-   **Mobile Integration** - Mobile app connectivity
