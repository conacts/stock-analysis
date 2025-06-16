import { and, eq } from 'drizzle-orm';
import { db } from '@/db/connection';
import { advisors, type Advisor, type AdvisorInsert } from '@/db/schema';

export async function getAllAdvisors(filters?: { status?: string }): Promise<Advisor[]> {
  const conditions = [];
  if (filters?.status) conditions.push(eq(advisors.status, filters.status));

  return await db
    .select()
    .from(advisors)
    .where(and(...conditions));
}

export async function getAdvisorById(id: number): Promise<Advisor | null> {
  const result = await db.select().from(advisors).where(eq(advisors.id, id));
  return result[0] || null;
}

export async function createAdvisor(data: AdvisorInsert): Promise<Advisor> {
  const result = await db.insert(advisors).values(data).returning();
  return result[0]!;
}

export async function updateAdvisor(
  id: number,
  data: Partial<AdvisorInsert>
): Promise<Advisor | null> {
  const result = await db
    .update(advisors)
    .set({ ...data, updatedAt: new Date() })
    .where(eq(advisors.id, id))
    .returning();
  return result[0] || null;
}

export async function softDeleteAdvisor(id: number): Promise<Advisor | null> {
  return await updateAdvisor(id, { status: 'inactive' });
}
