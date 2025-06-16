import { config } from 'dotenv';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

config();

const connectionString = process.env['DATABASE_URL'];

if (!connectionString) {
  throw new Error('DATABASE_URL environment variable is required');
}

// Create the connection
const client = postgres(connectionString);

// Create the database instance with schema
export const db = drizzle(client, { schema });

// Export types for convenience
export type Database = typeof db;
export { schema };

// Clean shutdown function
export async function closeConnection() {
  await client.end();
}
