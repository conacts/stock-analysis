/**
 * Agent Configuration
 *
 * Configuration settings for OpenAI agents.
 * Type safety ensures valid configurations.
 */

export interface AgentConfig {
  model: string;
  temperature: number;
}

export const agentConfig = {
  defaults: {
    model: 'gpt-4o',
    temperature: 0.1,
  } as AgentConfig,

  marketAnalyst: {
    model: 'gpt-4o',
    temperature: 0.1,
  } as AgentConfig,
} as const;
