import { and, eq } from 'drizzle-orm';
import { db } from '@/db/connection';
import { portfolios, type Portfolio, type PortfolioInsert } from '@/db/schema';

export async function getAllPortfolios(filters?: {
  status?: string;
  advisorId?: number;
}): Promise<Portfolio[]> {
  const conditions = [];
  if (filters?.status) conditions.push(eq(portfolios.status, filters.status));
  if (filters?.advisorId) conditions.push(eq(portfolios.advisorId, filters.advisorId));

  return await db
    .select()
    .from(portfolios)
    .where(and(...conditions));
}

export async function getPortfolioById(id: number): Promise<Portfolio | null> {
  const result = await db.select().from(portfolios).where(eq(portfolios.id, id));
  return result[0] || null;
}

export async function createPortfolio(data: PortfolioInsert): Promise<Portfolio> {
  const result = await db.insert(portfolios).values(data).returning();
  return result[0]!;
}

export async function updatePortfolio(
  id: number,
  data: Partial<PortfolioInsert>
): Promise<Portfolio | null> {
  const result = await db
    .update(portfolios)
    .set({ ...data, updatedAt: new Date() })
    .where(eq(portfolios.id, id))
    .returning();
  return result[0] || null;
}
