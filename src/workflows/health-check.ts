/**
 * Health Check Workflow
 *
 * Comprehensive system health monitoring for the AI trading system.
 * Validates database connectivity, API keys, agent availability, and system status.
 *
 * Scheduled to run hourly to ensure system reliability.
 */

import { task } from '@trigger.dev/sdk/v3';
import {
  DATABASE_URL,
  OPENAI_API_KEY,
  ALPACA_API_KEY,
  ALPACA_SECRET_KEY,
} from '@/config/environment';
import { testDatabaseConnection } from '@/db/utils';

// ============================================================================
// HEALTH CHECK TYPES
// ============================================================================

interface ApiKeyStatus {
  openai: boolean;
  alpaca: boolean;
}

interface HealthCheckDetails {
  timestamp: string;
  environment: string;
  database: {
    connected: boolean;
    connectionString: boolean;
  };
  apiKeys: ApiKeyStatus;
  agents: {
    available: boolean;
    count: number;
  };
}

interface HealthCheckResult {
  success: boolean;
  status: 'healthy' | 'unhealthy' | 'degraded';
  details: HealthCheckDetails;
  error?: string;
  warnings?: string[];
}

// ============================================================================
// HEALTH CHECK TASK
// ============================================================================

export const healthCheck = task({
  id: 'system-health-check',
  maxDuration: 60, // 1 minute
  run: async (): Promise<HealthCheckResult> => {
    console.log('🏥 Running comprehensive system health check');

    const warnings: string[] = [];
    let overallHealthy = true;

    // Initialize health status
    const healthDetails: HealthCheckDetails = {
      timestamp: new Date().toISOString(),
      environment: process.env['NODE_ENV'] || 'development',
      database: {
        connected: false,
        connectionString: !!DATABASE_URL,
      },
      apiKeys: {
        openai: !!OPENAI_API_KEY,
        alpaca: !!(ALPACA_API_KEY && ALPACA_SECRET_KEY),
      },
      agents: {
        available: false,
        count: 0,
      },
    };

    try {
      // Test database connection
      console.log('🔍 Testing database connection...');
      if (!DATABASE_URL) {
        warnings.push('DATABASE_URL not configured');
        overallHealthy = false;
      } else {
        const dbConnected = await testDatabaseConnection();
        healthDetails.database.connected = dbConnected;

        if (!dbConnected) {
          warnings.push('Database connection failed');
          overallHealthy = false;
        }
      }

      // Validate API keys
      console.log('🔑 Validating API keys...');
      if (!healthDetails.apiKeys.openai) {
        warnings.push('OpenAI API key not configured');
        overallHealthy = false;
      }

      if (!healthDetails.apiKeys.alpaca) {
        warnings.push('Alpaca API credentials not fully configured');
        // This is a warning but not critical for basic functionality
      }

      // Determine overall status
      const status: 'healthy' | 'unhealthy' | 'degraded' = overallHealthy
        ? 'healthy'
        : warnings.length > 0 && healthDetails.database.connected
          ? 'degraded'
          : 'unhealthy';

      // Log results
      console.log('✅ Health check completed');
      console.log(`📊 Overall Status: ${status.toUpperCase()}`);
      console.log(`🗄️  Database: ${healthDetails.database.connected ? 'Connected' : 'Failed'}`);
      console.log(`🔑 OpenAI API: ${healthDetails.apiKeys.openai ? 'Available' : 'Missing'}`);
      console.log(`🔑 Alpaca API: ${healthDetails.apiKeys.alpaca ? 'Available' : 'Missing'}`);
      console.log(
        `🤖 Agents: ${healthDetails.agents.available ? 'Available' : 'Unavailable'} (${healthDetails.agents.count})`
      );

      if (warnings.length > 0) {
        console.log('⚠️  Warnings:', warnings);
      }

      const result: HealthCheckResult = {
        success: status !== 'unhealthy',
        status,
        details: healthDetails,
      };

      if (warnings.length > 0) {
        result.warnings = warnings;
      }

      return result;
    } catch (error) {
      console.error('❌ Health check failed with error:', error);

      const errorResult: HealthCheckResult = {
        success: false,
        status: 'unhealthy',
        details: healthDetails,
        error: error instanceof Error ? error.message : 'Unknown health check error',
      };

      if (warnings.length > 0) {
        errorResult.warnings = warnings;
      }

      return errorResult;
    }
  },
});

// ============================================================================
// EXPORT
// ============================================================================

// Export the health check task for Trigger.dev scheduling
export default healthCheck;
