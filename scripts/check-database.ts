#!/usr/bin/env tsx

import { config } from 'dotenv';
import { isDatabaseConfigured, closeConnection } from '../src/db/connection';
import { testDatabaseConnection, getTableCounts } from '../src/db/utils';

config({
  path: '.env.local',
});

async function checkDatabase() {
  console.log('🔍 Checking database connectivity...');

  // Check if database is configured
  if (!isDatabaseConfigured()) {
    console.log('❌ No DATABASE_URL configured');
    process.exit(1);
  }

  try {
    // Test basic connectivity
    const isConnected = await testDatabaseConnection();
    if (!isConnected) {
      console.log('❌ Database connection failed');
      process.exit(1);
    }

    console.log('✅ Database connection successful');

    // Check table counts
    try {
      const counts = await getTableCounts();
      console.log('📊 Table counts:');
      console.log(`  - Agents: ${counts.agents}`);
      console.log(`  - Analysis Results: ${counts.analyses}`);
      console.log(`  - Health Checks: ${counts.healthChecks}`);
      console.log('✅ Database schema is accessible');
    } catch (error) {
      console.log(
        '⚠️  Database schema check failed:',
        error instanceof Error ? error.message : error
      );
      console.log('   This might indicate missing migrations or schema issues');
    }
  } catch (error) {
    console.error('❌ Database check failed:', error instanceof Error ? error.message : error);
    process.exit(1);
  } finally {
    await closeConnection();
  }
}

// Only run if called directly
if (require.main === module) {
  checkDatabase().catch(error => {
    console.error('❌ Unexpected error:', error);
    process.exit(1);
  });
}

export { checkDatabase };
