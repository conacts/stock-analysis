import { count } from 'drizzle-orm';
import { db } from '@/db/connection';
import {
  agents,
  analysisResults,
  healthChecks,
  conversations,
  conversationMessages,
} from '@/db/schema';

export async function testDatabaseConnection(): Promise<boolean> {
  try {
    await db.select().from(agents).limit(1);
    return true;
  } catch {
    return false;
  }
}

export async function getTableCounts() {
  const [agentCount, analysisCount, healthCheckCount, conversationCount, messageCount] =
    await Promise.all([
      db.select({ count: count() }).from(agents),
      db.select({ count: count() }).from(analysisResults),
      db.select({ count: count() }).from(healthChecks),
      db.select({ count: count() }).from(conversations),
      db.select({ count: count() }).from(conversationMessages),
    ]);

  return {
    agents: agentCount[0]?.count || 0,
    analyses: analysisCount[0]?.count || 0,
    healthChecks: healthCheckCount[0]?.count || 0,
    conversations: conversationCount[0]?.count || 0,
    messages: messageCount[0]?.count || 0,
  };
}
