/**
 * Error Types
 *
 * This file defines custom error classes for the trading system.
 */

// ============================================================================
// ERROR TYPES
// ============================================================================

export class AgentError extends Error {
  constructor(
    message: string,
    public agentId: string,
    public errorCode: string,
    public context?: Record<string, any>
  ) {
    super(message);
    this.name = 'AgentError';
  }
}

export class DataError extends Error {
  constructor(
    message: string,
    public dataSource: string,
    public errorCode: string
  ) {
    super(message);
    this.name = 'DataError';
  }
}

export class WorkflowError extends Error {
  constructor(
    message: string,
    public workflowId: string,
    public stepId?: string
  ) {
    super(message);
    this.name = 'WorkflowError';
  }
}
