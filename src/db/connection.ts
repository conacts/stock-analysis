import { config } from 'dotenv';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

config({
  path: '.env.local',
});

const connectionString = process.env['DATABASE_URL'];

// Lazy connection - only create when needed
let client: postgres.Sql | null = null;
let database: ReturnType<typeof drizzle> | null = null;

function getConnection() {
  if (!connectionString) {
    throw new Error('DATABASE_URL environment variable is required');
  }

  if (!client) {
    // Configure connection based on environment
    const isLocal =
      connectionString.includes('localhost') || connectionString.includes('127.0.0.1');

    const config = isLocal
      ? {
          // Local PostgreSQL - no SSL needed
          connect_timeout: 10,
          idle_timeout: 20,
          max_lifetime: 60 * 30,
        }
      : {
          // Remote database (like Supabase) - SSL required
          ssl: 'require' as const,
          connect_timeout: 10,
          idle_timeout: 20,
          max_lifetime: 60 * 30,
        };

    client = postgres(connectionString, config);
    database = drizzle(client, { schema });
  }

  return database!;
}

// Create the database instance with schema
export const db = new Proxy({} as ReturnType<typeof drizzle>, {
  get(_, prop) {
    const connection = getConnection();
    return connection[prop as keyof typeof connection];
  },
});

// Export types for convenience
export type Database = typeof db;
export { schema };

// Clean shutdown function
export async function closeConnection() {
  if (client) {
    await client.end();
    client = null;
    database = null;
  }
}

// Check if database is configured
export function isDatabaseConfigured(): boolean {
  return !!connectionString;
}
