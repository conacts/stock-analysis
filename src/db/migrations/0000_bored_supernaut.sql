CREATE TABLE "advisor_function_calls" (
	"id" serial PRIMARY KEY NOT NULL,
	"thread_message_id" integer NOT NULL,
	"function_name" varchar(100) NOT NULL,
	"parameters" jsonb NOT NULL,
	"result" jsonb,
	"status" varchar(20) DEFAULT 'pending',
	"error_message" text,
	"execution_time_ms" integer,
	"created_at" timestamp DEFAULT now(),
	"completed_at" timestamp
);
--> statement-breakpoint
CREATE TABLE "advisors" (
	"id" serial PRIMARY KEY NOT NULL,
	"name" varchar(100) NOT NULL,
	"system_prompt" text NOT NULL,
	"model" varchar(50) DEFAULT 'deepseek/r1',
	"temperature" real DEFAULT 0.1,
	"max_tokens" integer DEFAULT 2000,
	"status" varchar(20) DEFAULT 'active',
	"created_at" timestamp DEFAULT now(),
	"updated_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "analysis_results" (
	"id" serial PRIMARY KEY NOT NULL,
	"portfolio_id" integer NOT NULL,
	"advisor_id" integer NOT NULL,
	"analysis_type" varchar(50) NOT NULL,
	"symbol" varchar(20),
	"analysis_data" jsonb,
	"recommendations" jsonb,
	"status" varchar(20) DEFAULT 'completed',
	"created_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "conversation_threads" (
	"id" serial PRIMARY KEY NOT NULL,
	"portfolio_id" integer NOT NULL,
	"advisor_id" integer NOT NULL,
	"thread_type" varchar(20) NOT NULL,
	"title" varchar(200),
	"status" varchar(20) DEFAULT 'active',
	"parent_thread_id" integer,
	"trigger_execution_id" integer,
	"created_at" timestamp DEFAULT now(),
	"updated_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "market_triggers" (
	"id" serial PRIMARY KEY NOT NULL,
	"name" varchar(100) NOT NULL,
	"description" text,
	"trigger_type" varchar(20) NOT NULL,
	"trigger_config" jsonb NOT NULL,
	"target_type" varchar(20) NOT NULL,
	"target_id" integer,
	"advisor_id" integer NOT NULL,
	"is_active" boolean DEFAULT true,
	"created_at" timestamp DEFAULT now(),
	"updated_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "performance" (
	"id" serial PRIMARY KEY NOT NULL,
	"advisor_id" integer NOT NULL,
	"portfolio_id" integer NOT NULL,
	"period_start" date NOT NULL,
	"period_end" date NOT NULL,
	"total_trades" integer DEFAULT 0,
	"successful_trades" integer DEFAULT 0,
	"total_return" numeric(10, 4) DEFAULT '0',
	"sharpe_ratio" numeric(10, 4),
	"max_drawdown" numeric(10, 4),
	"win_rate" numeric(5, 4),
	"average_hold_time" interval,
	"created_at" timestamp DEFAULT now(),
	CONSTRAINT "performance_advisor_id_portfolio_id_period_start_period_end_unique" UNIQUE("advisor_id","portfolio_id","period_start","period_end")
);
--> statement-breakpoint
CREATE TABLE "portfolio_balances" (
	"id" serial PRIMARY KEY NOT NULL,
	"portfolio_id" integer NOT NULL,
	"cash_balance" numeric(15, 4) NOT NULL,
	"total_holdings_value" numeric(15, 4) NOT NULL,
	"total_portfolio_value" numeric(15, 4) NOT NULL,
	"recorded_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "portfolio_holdings" (
	"id" serial PRIMARY KEY NOT NULL,
	"portfolio_id" integer NOT NULL,
	"symbol" varchar(20) NOT NULL,
	"quantity" numeric(15, 6) NOT NULL,
	"average_cost" numeric(15, 4) NOT NULL,
	"current_price" numeric(15, 4),
	"last_price_update" timestamp,
	"created_at" timestamp DEFAULT now(),
	"updated_at" timestamp DEFAULT now(),
	CONSTRAINT "portfolio_holdings_portfolio_id_symbol_unique" UNIQUE("portfolio_id","symbol")
);
--> statement-breakpoint
CREATE TABLE "portfolios" (
	"id" serial PRIMARY KEY NOT NULL,
	"name" varchar(100) NOT NULL,
	"description" text,
	"advisor_id" integer,
	"status" varchar(20) DEFAULT 'active',
	"created_at" timestamp DEFAULT now(),
	"updated_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "thread_messages" (
	"id" serial PRIMARY KEY NOT NULL,
	"thread_id" integer NOT NULL,
	"message_type" varchar(20) NOT NULL,
	"content" text NOT NULL,
	"metadata" jsonb,
	"analysis_result_id" integer,
	"transaction_id" integer,
	"sequence_order" integer NOT NULL,
	"created_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "transactions" (
	"id" serial PRIMARY KEY NOT NULL,
	"portfolio_id" integer NOT NULL,
	"symbol" varchar(20) NOT NULL,
	"transaction_type" varchar(10) NOT NULL,
	"quantity" numeric(15, 6) NOT NULL,
	"price" numeric(15, 4) NOT NULL,
	"total_amount" numeric(15, 4) NOT NULL,
	"fees" numeric(15, 4) DEFAULT '0',
	"analysis_result_id" integer,
	"executed_by_advisor" boolean DEFAULT false,
	"execution_status" varchar(20) DEFAULT 'pending',
	"execution_notes" text,
	"created_at" timestamp DEFAULT now(),
	"executed_at" timestamp
);
--> statement-breakpoint
CREATE TABLE "trigger_executions" (
	"id" serial PRIMARY KEY NOT NULL,
	"trigger_id" integer NOT NULL,
	"execution_time" timestamp DEFAULT now(),
	"status" varchar(20) DEFAULT 'pending',
	"result_data" jsonb,
	"error_message" text,
	"analysis_result_id" integer,
	"created_at" timestamp DEFAULT now()
);
--> statement-breakpoint
ALTER TABLE "advisor_function_calls" ADD CONSTRAINT "advisor_function_calls_thread_message_id_thread_messages_id_fk" FOREIGN KEY ("thread_message_id") REFERENCES "public"."thread_messages"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_results" ADD CONSTRAINT "analysis_results_portfolio_id_portfolios_id_fk" FOREIGN KEY ("portfolio_id") REFERENCES "public"."portfolios"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "analysis_results" ADD CONSTRAINT "analysis_results_advisor_id_advisors_id_fk" FOREIGN KEY ("advisor_id") REFERENCES "public"."advisors"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "conversation_threads" ADD CONSTRAINT "conversation_threads_portfolio_id_portfolios_id_fk" FOREIGN KEY ("portfolio_id") REFERENCES "public"."portfolios"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "conversation_threads" ADD CONSTRAINT "conversation_threads_advisor_id_advisors_id_fk" FOREIGN KEY ("advisor_id") REFERENCES "public"."advisors"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "conversation_threads" ADD CONSTRAINT "conversation_threads_trigger_execution_id_trigger_executions_id_fk" FOREIGN KEY ("trigger_execution_id") REFERENCES "public"."trigger_executions"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "market_triggers" ADD CONSTRAINT "market_triggers_advisor_id_advisors_id_fk" FOREIGN KEY ("advisor_id") REFERENCES "public"."advisors"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "performance" ADD CONSTRAINT "performance_advisor_id_advisors_id_fk" FOREIGN KEY ("advisor_id") REFERENCES "public"."advisors"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "performance" ADD CONSTRAINT "performance_portfolio_id_portfolios_id_fk" FOREIGN KEY ("portfolio_id") REFERENCES "public"."portfolios"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "portfolio_balances" ADD CONSTRAINT "portfolio_balances_portfolio_id_portfolios_id_fk" FOREIGN KEY ("portfolio_id") REFERENCES "public"."portfolios"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "portfolio_holdings" ADD CONSTRAINT "portfolio_holdings_portfolio_id_portfolios_id_fk" FOREIGN KEY ("portfolio_id") REFERENCES "public"."portfolios"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "portfolios" ADD CONSTRAINT "portfolios_advisor_id_advisors_id_fk" FOREIGN KEY ("advisor_id") REFERENCES "public"."advisors"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "thread_messages" ADD CONSTRAINT "thread_messages_thread_id_conversation_threads_id_fk" FOREIGN KEY ("thread_id") REFERENCES "public"."conversation_threads"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "thread_messages" ADD CONSTRAINT "thread_messages_analysis_result_id_analysis_results_id_fk" FOREIGN KEY ("analysis_result_id") REFERENCES "public"."analysis_results"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "thread_messages" ADD CONSTRAINT "thread_messages_transaction_id_transactions_id_fk" FOREIGN KEY ("transaction_id") REFERENCES "public"."transactions"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "transactions" ADD CONSTRAINT "transactions_portfolio_id_portfolios_id_fk" FOREIGN KEY ("portfolio_id") REFERENCES "public"."portfolios"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "transactions" ADD CONSTRAINT "transactions_analysis_result_id_analysis_results_id_fk" FOREIGN KEY ("analysis_result_id") REFERENCES "public"."analysis_results"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "trigger_executions" ADD CONSTRAINT "trigger_executions_trigger_id_market_triggers_id_fk" FOREIGN KEY ("trigger_id") REFERENCES "public"."market_triggers"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "trigger_executions" ADD CONSTRAINT "trigger_executions_analysis_result_id_analysis_results_id_fk" FOREIGN KEY ("analysis_result_id") REFERENCES "public"."analysis_results"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "idx_advisor_function_calls_message_id" ON "advisor_function_calls" USING btree ("thread_message_id");--> statement-breakpoint
CREATE INDEX "idx_advisor_function_calls_status" ON "advisor_function_calls" USING btree ("status");--> statement-breakpoint
CREATE INDEX "idx_analysis_results_portfolio_id" ON "analysis_results" USING btree ("portfolio_id");--> statement-breakpoint
CREATE INDEX "idx_analysis_results_created_at" ON "analysis_results" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "idx_analysis_results_analysis_type" ON "analysis_results" USING btree ("analysis_type");--> statement-breakpoint
CREATE INDEX "idx_conversation_threads_portfolio_id" ON "conversation_threads" USING btree ("portfolio_id");--> statement-breakpoint
CREATE INDEX "idx_conversation_threads_advisor_id" ON "conversation_threads" USING btree ("advisor_id");--> statement-breakpoint
CREATE INDEX "idx_conversation_threads_status" ON "conversation_threads" USING btree ("status");--> statement-breakpoint
CREATE INDEX "idx_conversation_threads_created_at" ON "conversation_threads" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "idx_market_triggers_advisor_id" ON "market_triggers" USING btree ("advisor_id");--> statement-breakpoint
CREATE INDEX "idx_market_triggers_type" ON "market_triggers" USING btree ("trigger_type");--> statement-breakpoint
CREATE INDEX "idx_market_triggers_active" ON "market_triggers" USING btree ("is_active");--> statement-breakpoint
CREATE INDEX "idx_performance_advisor_id" ON "performance" USING btree ("advisor_id");--> statement-breakpoint
CREATE INDEX "idx_performance_portfolio_id" ON "performance" USING btree ("portfolio_id");--> statement-breakpoint
CREATE INDEX "idx_performance_period" ON "performance" USING btree ("period_start","period_end");--> statement-breakpoint
CREATE INDEX "idx_portfolio_balances_portfolio_id" ON "portfolio_balances" USING btree ("portfolio_id");--> statement-breakpoint
CREATE INDEX "idx_portfolio_balances_recorded_at" ON "portfolio_balances" USING btree ("recorded_at");--> statement-breakpoint
CREATE INDEX "idx_portfolio_holdings_portfolio_id" ON "portfolio_holdings" USING btree ("portfolio_id");--> statement-breakpoint
CREATE INDEX "idx_portfolio_holdings_symbol" ON "portfolio_holdings" USING btree ("symbol");--> statement-breakpoint
CREATE INDEX "idx_portfolios_status" ON "portfolios" USING btree ("status");--> statement-breakpoint
CREATE INDEX "idx_portfolios_advisor_id" ON "portfolios" USING btree ("advisor_id");--> statement-breakpoint
CREATE INDEX "idx_thread_messages_thread_id" ON "thread_messages" USING btree ("thread_id");--> statement-breakpoint
CREATE INDEX "idx_thread_messages_sequence" ON "thread_messages" USING btree ("thread_id","sequence_order");--> statement-breakpoint
CREATE INDEX "idx_transactions_portfolio_id" ON "transactions" USING btree ("portfolio_id");--> statement-breakpoint
CREATE INDEX "idx_transactions_symbol" ON "transactions" USING btree ("symbol");--> statement-breakpoint
CREATE INDEX "idx_transactions_created_at" ON "transactions" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "idx_trigger_executions_trigger_id" ON "trigger_executions" USING btree ("trigger_id");--> statement-breakpoint
CREATE INDEX "idx_trigger_executions_execution_time" ON "trigger_executions" USING btree ("execution_time");--> statement-breakpoint
CREATE INDEX "idx_trigger_executions_status" ON "trigger_executions" USING btree ("status");