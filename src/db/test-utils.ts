/**
 * Database Testing Utilities
 *
 * Provides test database setup, cleanup, and utilities for proper test isolation.
 * Uses test-specific database or test schema to avoid affecting production data.
 */

import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { migrate } from 'drizzle-orm/postgres-js/migrator';
import * as schema from './schema';
import { sql } from 'drizzle-orm';

let testDb: ReturnType<typeof drizzle> | null = null;
let testClient: postgres.Sql | null = null;

/**
 * Initialize test database connection
 */
export async function initTestDb(): Promise<ReturnType<typeof drizzle>> {
  if (testDb) return testDb;

  const testDatabaseUrl = process.env.TEST_DATABASE_URL || process.env.DATABASE_URL;

  if (!testDatabaseUrl) {
    throw new Error(
      'TEST_DATABASE_URL or DATABASE_URL environment variable is required for testing'
    );
  }

  // Create test client with test-specific configuration
  testClient = postgres(testDatabaseUrl, {
    max: 1, // Single connection for tests
    idle_timeout: 20,
    connect_timeout: 60,
  });

  testDb = drizzle(testClient, { schema });

  return testDb;
}

/**
 * Setup test database schema and run migrations
 */
export async function setupTestDb(): Promise<void> {
  if (!testDb) {
    await initTestDb();
  }

  try {
    // Run migrations to ensure schema is up to date
    await migrate(testDb!, { migrationsFolder: './src/db/migrations' });
    console.log('✅ Test database migrations completed');
  } catch (error) {
    console.warn('⚠️ Migration failed (may already be applied):', error);
  }
}

/**
 * Clean up test database - removes all data but keeps schema
 */
export async function cleanTestDb(): Promise<void> {
  if (!testDb) return;

  try {
    // Clean up in reverse dependency order
    await testDb.delete(schema.marketOpenContexts);
    await testDb.delete(schema.researchData);
    await testDb.delete(schema.researchSessions);
    await testDb.delete(schema.conversationMessages);
    await testDb.delete(schema.conversations);
    await testDb.delete(schema.analysisResults);
    await testDb.delete(schema.healthChecks);
    await testDb.delete(schema.agents);

    console.log('🧹 Test database cleaned');
  } catch (error) {
    console.error('❌ Failed to clean test database:', error);
    throw error;
  }
}

/**
 * Close test database connection
 */
export async function closeTestDb(): Promise<void> {
  if (testClient) {
    await testClient.end();
    testClient = null;
    testDb = null;
    console.log('🔌 Test database connection closed');
  }
}

/**
 * Create test agent for testing
 */
export async function createTestAgent(name: string = 'TestAgent') {
  if (!testDb) {
    await initTestDb();
  }

  const [agent] = await testDb!
    .insert(schema.agents)
    .values({
      name,
      instructions: 'Test agent for unit testing',
      model: 'gpt-4o',
      riskTolerance: 'medium',
      tradingStyle: 'moderate',
    })
    .returning();

  return agent!;
}

/**
 * Create test research session
 */
export async function createTestResearchSession(
  agentId: number,
  sessionType: schema.SessionType = 'market_open'
) {
  if (!testDb) {
    await initTestDb();
  }

  const [session] = await testDb!
    .insert(schema.researchSessions)
    .values({
      agentId,
      sessionType,
      status: 'in_progress',
    })
    .returning();

  return session!;
}

/**
 * Create test research data
 */
export async function createTestResearchData(
  sessionId: number,
  researchType: schema.ResearchType,
  extractedData: any
) {
  if (!testDb) {
    await initTestDb();
  }

  const [data] = await testDb!
    .insert(schema.researchData)
    .values({
      sessionId,
      researchType,
      extractedData,
      confidence: 85,
      sentiment: 'neutral',
      impact: 'medium',
    })
    .returning();

  return data!;
}

/**
 * Get test database instance (for use in tests)
 */
export function getTestDb() {
  if (!testDb) {
    throw new Error('Test database not initialized. Call initTestDb() first.');
  }
  return testDb;
}

/**
 * Test helper to check if database connection is working
 */
export async function testDbConnection(): Promise<boolean> {
  try {
    if (!testDb) {
      await initTestDb();
    }

    await testDb!.execute(sql`SELECT 1`);
    return true;
  } catch (error) {
    console.error('Database connection test failed:', error);
    return false;
  }
}

/**
 * Create a complete test environment setup
 */
export async function setupTestEnvironment() {
  await setupTestDb();
  await cleanTestDb();

  // Create default test agent
  const agent = await createTestAgent('TestEnvironmentAgent');

  return {
    db: getTestDb(),
    agent,
    cleanup: async () => {
      await cleanTestDb();
      await closeTestDb();
    },
  };
}
