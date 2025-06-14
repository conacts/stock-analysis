import { Pool, PoolClient, QueryResultRow } from 'pg';
import { DATABASE_URL } from '../utils/config';
import { DatabaseResult, QueryOptions } from './models';

export class DatabaseConnection {
  private pool: Pool;
  private static instance: DatabaseConnection;

  private constructor() {
    this.pool = new Pool({
      connectionString: DATABASE_URL,
      max: 20, // Maximum number of clients in the pool
      idleTimeoutMillis: 30000, // Close idle clients after 30 seconds
      connectionTimeoutMillis: 2000, // Return an error after 2 seconds if connection could not be established
      maxUses: 7500, // Close (and replace) a connection after it has been used 7500 times
    });

    // Handle pool errors
    this.pool.on('error', err => {
      console.error('Unexpected error on idle client', err);
      process.exit(-1);
    });
  }

  public static getInstance(): DatabaseConnection {
    if (!DatabaseConnection.instance) {
      DatabaseConnection.instance = new DatabaseConnection();
    }
    return DatabaseConnection.instance;
  }

  public async query<T extends QueryResultRow = any>(
    text: string,
    params?: any[]
  ): Promise<DatabaseResult<T[]>> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(text, params);
      return {
        success: true,
        data: result.rows as T[],
        rowCount: result.rowCount || 0,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown database error',
      };
    } finally {
      client.release();
    }
  }

  public async queryOne<T extends QueryResultRow = any>(
    text: string,
    params?: any[]
  ): Promise<DatabaseResult<T | null>> {
    const result = await this.query<T>(text, params);
    if (!result.success) {
      return {
        success: false,
        error: result.error || 'Query failed',
      };
    }

    const data = result.data && result.data.length > 0 ? result.data[0] : null;
    return {
      success: true,
      data: data as T | null,
      rowCount: result.rowCount || 0,
    };
  }

  public async transaction<T>(
    callback: (client: PoolClient) => Promise<T>
  ): Promise<DatabaseResult<T>> {
    const client = await this.pool.connect();
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return {
        success: true,
        data: result,
      };
    } catch (error) {
      await client.query('ROLLBACK');
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Transaction failed',
      };
    } finally {
      client.release();
    }
  }

  public async testConnection(): Promise<boolean> {
    try {
      const result = await this.query('SELECT 1 as test');
      return result.success;
    } catch {
      return false;
    }
  }

  public async close(): Promise<void> {
    await this.pool.end();
  }

  // Helper method to build WHERE clauses
  public buildWhereClause(
    conditions: Record<string, any>,
    startIndex: number = 1
  ): { whereClause: string; values: any[] } {
    const keys = Object.keys(conditions);
    if (keys.length === 0) {
      return { whereClause: '', values: [] };
    }

    const clauses = keys.map((key, index) => `${key} = $${startIndex + index}`);
    const values = keys.map(key => conditions[key]);

    return {
      whereClause: `WHERE ${clauses.join(' AND ')}`,
      values,
    };
  }

  // Helper method to build ORDER BY clause
  public buildOrderClause(options?: QueryOptions): string {
    if (!options?.orderBy) {
      return '';
    }

    const direction = options.orderDirection || 'ASC';
    return `ORDER BY ${options.orderBy} ${direction}`;
  }

  // Helper method to build LIMIT/OFFSET clause
  public buildLimitClause(options?: QueryOptions): string {
    const clauses: string[] = [];

    if (options?.limit) {
      clauses.push(`LIMIT ${options.limit}`);
    }

    if (options?.offset) {
      clauses.push(`OFFSET ${options.offset}`);
    }

    return clauses.join(' ');
  }
}

// Export singleton instance
export const db = DatabaseConnection.getInstance();
