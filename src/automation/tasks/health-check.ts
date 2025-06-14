import { task } from '@trigger.dev/sdk/v3';
import { db } from '../../database/connection';
import { DEEPSEEK_API_KEY, ALPACA_API_KEY, ALPACA_SECRET_KEY } from '../../utils/config';

export const healthCheck = task({
  id: 'health-check',
  maxDuration: 60, // 1 minute
  run: async () => {
    console.log('🏥 Running system health check');

    const healthStatus = {
      timestamp: new Date().toISOString(),
      database: false,
      environment: process.env['NODE_ENV'] || 'development',
      api_keys: {
        deepseek: !!DEEPSEEK_API_KEY,
        alpaca: !!ALPACA_API_KEY && !!ALPACA_SECRET_KEY,
      },
    };

    try {
      // Test database connection
      const dbTest = await db.testConnection();
      healthStatus.database = dbTest;

      console.log('✅ Health check completed');
      console.log(`📊 Database: ${dbTest ? 'Connected' : 'Failed'}`);
      console.log(`🔑 DeepSeek API: ${healthStatus.api_keys.deepseek ? 'Available' : 'Missing'}`);
      console.log(`🔑 Alpaca API: ${healthStatus.api_keys.alpaca ? 'Available' : 'Missing'}`);

      return {
        success: true,
        status: 'healthy',
        details: healthStatus,
      };
    } catch (error) {
      console.error('❌ Health check failed:', error);

      return {
        success: false,
        status: 'unhealthy',
        details: healthStatus,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  },
});
