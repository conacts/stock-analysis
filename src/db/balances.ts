import { eq, desc } from 'drizzle-orm';
import { db } from '@/db/connection';
import { portfolioBalances, type PortfolioBalance, type PortfolioBalanceInsert } from '@/db/schema';

export async function getLatestBalance(portfolioId: number): Promise<PortfolioBalance | null> {
  const result = await db
    .select()
    .from(portfolioBalances)
    .where(eq(portfolioBalances.portfolioId, portfolioId))
    .orderBy(desc(portfolioBalances.recordedAt))
    .limit(1);
  return result[0] || null;
}

export async function recordBalance(data: PortfolioBalanceInsert): Promise<PortfolioBalance> {
  const result = await db.insert(portfolioBalances).values(data).returning();
  return result[0]!;
}
