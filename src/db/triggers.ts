import { eq } from 'drizzle-orm';
import { db } from '@/db/connection';
import { marketTriggers, type MarketTrigger, type MarketTriggerInsert } from '@/db/schema';

export async function getActiveTriggers(): Promise<MarketTrigger[]> {
  return await db.select().from(marketTriggers).where(eq(marketTriggers.isActive, true));
}

export async function createTrigger(data: MarketTriggerInsert): Promise<MarketTrigger> {
  const result = await db.insert(marketTriggers).values(data).returning();
  return result[0]!;
}
