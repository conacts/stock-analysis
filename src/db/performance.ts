import { and, eq, desc } from 'drizzle-orm';
import { db } from '@/db/connection';
import { performance, type Performance, type PerformanceInsert } from '@/db/schema';

export async function getPerformanceByAdvisor(
  advisorId: number,
  portfolioId?: number
): Promise<Performance[]> {
  const conditions = [eq(performance.advisorId, advisorId)];
  if (portfolioId) conditions.push(eq(performance.portfolioId, portfolioId));

  return await db
    .select()
    .from(performance)
    .where(and(...conditions))
    .orderBy(desc(performance.periodStart));
}

export async function createPerformance(data: PerformanceInsert): Promise<Performance> {
  const result = await db.insert(performance).values(data).returning();
  return result[0]!;
}

export async function getLatestPerformanceByAdvisor(
  advisorId: number
): Promise<Performance | null> {
  const result = await db
    .select()
    .from(performance)
    .where(eq(performance.advisorId, advisorId))
    .orderBy(desc(performance.periodEnd))
    .limit(1);
  return result[0] || null;
}
