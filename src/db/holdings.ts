import { and, eq } from 'drizzle-orm';
import { db } from '@/db/connection';
import { portfolioHoldings, type PortfolioHolding, type PortfolioHoldingInsert } from '@/db/schema';

export async function getHoldingsByPortfolio(portfolioId: number): Promise<PortfolioHolding[]> {
  return await db
    .select()
    .from(portfolioHoldings)
    .where(eq(portfolioHoldings.portfolioId, portfolioId));
}

export async function upsertHolding(data: PortfolioHoldingInsert): Promise<PortfolioHolding> {
  const existing = await db
    .select()
    .from(portfolioHoldings)
    .where(
      and(
        eq(portfolioHoldings.portfolioId, data.portfolioId),
        eq(portfolioHoldings.symbol, data.symbol)
      )
    );

  if (existing[0]) {
    const result = await db
      .update(portfolioHoldings)
      .set({ ...data, updatedAt: new Date() })
      .where(
        and(
          eq(portfolioHoldings.portfolioId, data.portfolioId),
          eq(portfolioHoldings.symbol, data.symbol)
        )
      )
      .returning();
    return result[0]!;
  } else {
    const result = await db.insert(portfolioHoldings).values(data).returning();
    return result[0]!;
  }
}
