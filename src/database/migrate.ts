#!/usr/bin/env tsx
import { config } from 'dotenv';
import { readFileSync } from 'fs';
import { join } from 'path';
import { Client } from 'pg';

// Load environment variables from .env.local
config({ path: '.env.local' });

const DATABASE_URL = process.env['DATABASE_URL'];

if (!DATABASE_URL) {
  console.error('❌ DATABASE_URL not found in environment variables');
  console.error('Make sure you have DATABASE_URL set in your .env.local file');
  process.exit(1);
}

async function inspectDatabase() {
  const client = new Client({ connectionString: DATABASE_URL });

  try {
    console.log(`🔗 Connecting to database...`);
    await client.connect();

    console.log(`📊 Inspecting database tables...`);
    const result = await client.query(`
			SELECT table_name, column_name, data_type 
			FROM information_schema.columns 
			WHERE table_schema = 'public' 
			ORDER BY table_name, ordinal_position
		`);

    const tables: Record<string, Array<{ column: string; type: string }>> = {};

    for (const row of result.rows || []) {
      if (!tables[row.table_name]) {
        tables[row.table_name] = [];
      }
      tables[row.table_name].push({
        column: row.column_name,
        type: row.data_type,
      });
    }

    console.log('\n📋 Existing Tables:');
    for (const [tableName, columns] of Object.entries(tables)) {
      console.log(`\n  🗂️  ${tableName}:`);
      for (const col of columns) {
        console.log(`    - ${col.column} (${col.type})`);
      }
    }
  } catch (error) {
    console.error(`❌ Database inspection failed:`);
    console.error(error);
    process.exit(1);
  } finally {
    await client.end();
  }
}

async function runMigration(migrationFile: string) {
  const client = new Client({ connectionString: DATABASE_URL });

  try {
    console.log(`🔗 Connecting to database...`);
    await client.connect();

    console.log(`📄 Reading migration file: ${migrationFile}`);
    const migrationPath = join(__dirname, 'migrations', migrationFile);
    const migrationSQL = readFileSync(migrationPath, 'utf8');

    console.log(`🚀 Running migration: ${migrationFile}`);
    await client.query(migrationSQL);

    console.log(`✅ Migration completed successfully: ${migrationFile}`);
  } catch (error) {
    console.error(`❌ Migration failed: ${migrationFile}`);
    console.error(error);
    process.exit(1);
  } finally {
    await client.end();
  }
}

async function main() {
  const command = process.argv[2];

  if (command === 'inspect') {
    console.log(`🗄️  Database Inspector`);
    console.log(`📍 Database: ${DATABASE_URL!.replace(/\/\/.*@/, '//***@')}`); // Hide credentials
    console.log('');
    await inspectDatabase();
    return;
  }

  const migrationFile = command;

  if (!migrationFile) {
    console.error('❌ Please specify a migration file or "inspect"');
    console.error('Usage: npm run db:migrate <migration-file>');
    console.error('       npm run db:migrate inspect');
    console.error('Example: npm run db:migrate 004_enhanced_conversation_threads.sql');
    process.exit(1);
  }

  console.log(`🗄️  Database Migration Runner`);
  console.log(`📍 Database: ${DATABASE_URL!.replace(/\/\/.*@/, '//***@')}`); // Hide credentials
  console.log(`📁 Migration: ${migrationFile}`);
  console.log('');

  await runMigration(migrationFile);
}

if (require.main === module) {
  main().catch(console.error);
}
