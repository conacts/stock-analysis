import { eq, desc } from 'drizzle-orm';
import { db } from '@/db/connection';
import { analysisResults, type AnalysisResult, type AnalysisResultInsert } from '@/db/schema';

export async function getAnalysisByPortfolio(
  portfolioId: number,
  limit = 50
): Promise<AnalysisResult[]> {
  return await db
    .select()
    .from(analysisResults)
    .where(eq(analysisResults.portfolioId, portfolioId))
    .orderBy(desc(analysisResults.createdAt))
    .limit(limit);
}

export async function createAnalysis(data: AnalysisResultInsert): Promise<AnalysisResult> {
  const result = await db.insert(analysisResults).values(data).returning();
  return result[0]!;
}
