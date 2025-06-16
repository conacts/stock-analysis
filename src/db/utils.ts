import { count } from 'drizzle-orm';
import { db } from '@/db/connection';
import { advisors, portfolios, transactions, analysisResults } from '@/db/schema';

export async function testDatabaseConnection(): Promise<boolean> {
  try {
    await db.select().from(advisors).limit(1);
    return true;
  } catch {
    return false;
  }
}

export async function getTableCounts() {
  const [advisorCount, portfolioCount, transactionCount, analysisCount] = await Promise.all([
    db.select({ count: count() }).from(advisors),
    db.select({ count: count() }).from(portfolios),
    db.select({ count: count() }).from(transactions),
    db.select({ count: count() }).from(analysisResults),
  ]);

  return {
    advisors: advisorCount[0]?.count || 0,
    portfolios: portfolioCount[0]?.count || 0,
    transactions: transactionCount[0]?.count || 0,
    analyses: analysisCount[0]?.count || 0,
  };
}
