// Environment variable validation for Trigger.dev tasks
// This ensures all required environment variables are present before tasks execute

export interface RequiredEnvVars {
  PYTHON_API_URL: string;
  API_TOKEN: string;
  DEEPSEEK_API_KEY?: string; // Optional for some tasks
  DATABASE_URL?: string; // Optional if using external API
}

export class EnvironmentValidationError extends Error {
  constructor(missingVars: string[]) {
    super(`Missing required environment variables: ${missingVars.join(', ')}`);
    this.name = 'EnvironmentValidationError';
  }
}

/**
 * Validates that all required environment variables are present
 * Throws EnvironmentValidationError if any are missing
 */
export function validateRequiredEnvVars(requiredVars: (keyof RequiredEnvVars)[] = ['PYTHON_API_URL', 'API_TOKEN']): RequiredEnvVars {
  const missingVars: string[] = [];
  const envVars: Partial<RequiredEnvVars> = {};

  for (const varName of requiredVars) {
    const value = process.env[varName];
    if (!value || value.trim() === '') {
      missingVars.push(varName);
    } else {
      envVars[varName] = value;
    }
  }

  if (missingVars.length > 0) {
    throw new EnvironmentValidationError(missingVars);
  }

  return envVars as RequiredEnvVars;
}

/**
 * Validates environment variables and returns them with proper typing
 * Use this at the start of each task that requires API access
 */
export function getValidatedEnv(requiredVars?: (keyof RequiredEnvVars)[]): RequiredEnvVars {
  try {
    return validateRequiredEnvVars(requiredVars);
  } catch (error) {
    console.error('🚨 Environment Validation Failed:');
    console.error(error.message);
    console.error('');
    console.error('📋 Required Environment Variables:');
    console.error('  PYTHON_API_URL - URL of the Python API backend');
    console.error('  API_TOKEN - Authentication token for API access');
    console.error('  DEEPSEEK_API_KEY - DeepSeek API key (optional for some tasks)');
    console.error('  DATABASE_URL - Database connection string (optional if using external API)');
    console.error('');
    console.error('🔧 To fix this:');
    console.error('  1. Set the environment variables in your Trigger.dev project settings');
    console.error('  2. Redeploy the project');
    console.error('  3. Ensure your Python API is running and accessible');

    throw error;
  }
}

/**
 * Creates a properly configured fetch function with validated environment
 */
export function createApiClient(env: RequiredEnvVars) {
  return {
    get: async (endpoint: string) => {
      const url = `${env.PYTHON_API_URL}${endpoint}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${env.API_TOKEN}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${url}`);
      }

      return response.json();
    },

    post: async (endpoint: string, data?: any) => {
      const url = `${env.PYTHON_API_URL}${endpoint}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.API_TOKEN}`,
          'Content-Type': 'application/json'
        },
        body: data ? JSON.stringify(data) : undefined
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${url}`);
      }

      return response.json();
    }
  };
}

/**
 * Utility to check if environment is properly configured without throwing
 */
export function isEnvironmentConfigured(requiredVars?: (keyof RequiredEnvVars)[]): boolean {
  try {
    validateRequiredEnvVars(requiredVars);
    return true;
  } catch {
    return false;
  }
}

/**
 * Get environment status for health checks
 */
export function getEnvironmentStatus(): {
  configured: boolean;
  missingVars: string[];
  availableVars: string[];
} {
  const allVars: (keyof RequiredEnvVars)[] = ['PYTHON_API_URL', 'API_TOKEN', 'DEEPSEEK_API_KEY', 'DATABASE_URL'];
  const missingVars: string[] = [];
  const availableVars: string[] = [];

  for (const varName of allVars) {
    const value = process.env[varName];
    if (!value || value.trim() === '') {
      missingVars.push(varName);
    } else {
      availableVars.push(varName);
    }
  }

  return {
    configured: missingVars.length === 0 || (
      availableVars.includes('PYTHON_API_URL') &&
      availableVars.includes('API_TOKEN')
    ),
    missingVars,
    availableVars
  };
}
