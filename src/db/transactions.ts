import { eq, desc } from 'drizzle-orm';
import { db } from '@/db/connection';
import { transactions, type Transaction, type TransactionInsert } from '@/db/schema';

export async function getTransactionsByPortfolio(
  portfolioId: number,
  limit = 100
): Promise<Transaction[]> {
  return await db
    .select()
    .from(transactions)
    .where(eq(transactions.portfolioId, portfolioId))
    .orderBy(desc(transactions.createdAt))
    .limit(limit);
}

export async function createTransaction(data: TransactionInsert): Promise<Transaction> {
  const result = await db.insert(transactions).values(data).returning();
  return result[0]!;
}

export async function markTransactionExecuted(
  id: number,
  executionNotes?: string
): Promise<Transaction | null> {
  const result = await db
    .update(transactions)
    .set({
      executionStatus: 'executed',
      executedAt: new Date(),
      executionNotes,
    })
    .where(eq(transactions.id, id))
    .returning();
  return result[0] || null;
}
