import { config } from 'dotenv';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

config();

const connectionString = process.env['DATABASE_URL'];

// Lazy connection - only create when needed
let client: postgres.Sql | null = null;
let database: ReturnType<typeof drizzle> | null = null;

function getConnection() {
	if (!connectionString) {
		throw new Error('DATABASE_URL environment variable is required');
	}

	if (!client) {
		client = postgres(connectionString);
		database = drizzle(client, { schema });
	}

	return database!;
}

// Create the database instance with schema
export const db = new Proxy({} as ReturnType<typeof drizzle>, {
	get(_, prop) {
		const connection = getConnection();
		return connection[prop as keyof typeof connection];
	}
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
