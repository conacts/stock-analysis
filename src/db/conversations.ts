import { db } from '@/db/connection';
import {
  conversationThreads,
  threadMessages,
  advisorFunctionCalls,
  type ConversationThread,
  type ConversationThreadInsert,
  type ThreadMessage,
  type ThreadMessageInsert,
  type AdvisorFunctionCall,
  type AdvisorFunctionCallInsert,
} from '@/db/schema';

export async function createConversationThread(
  data: ConversationThreadInsert
): Promise<ConversationThread> {
  const result = await db.insert(conversationThreads).values(data).returning();
  return result[0]!;
}

export async function addThreadMessage(data: ThreadMessageInsert): Promise<ThreadMessage> {
  const result = await db.insert(threadMessages).values(data).returning();
  return result[0]!;
}

export async function recordAdvisorFunctionCall(
  data: AdvisorFunctionCallInsert
): Promise<AdvisorFunctionCall> {
  const result = await db.insert(advisorFunctionCalls).values(data).returning();
  return result[0]!;
}
