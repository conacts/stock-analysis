CREATE TABLE "agents" (
	"id" serial PRIMARY KEY NOT NULL,
	"name" varchar(100) NOT NULL,
	"instructions" text NOT NULL,
	"model" varchar(50) DEFAULT 'gpt-4o',
	"created_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "analysis_results" (
	"id" serial PRIMARY KEY NOT NULL,
	"agent_id" integer,
	"analysis_type" varchar(50) NOT NULL,
	"symbol" varchar(20),
	"result" text,
	"success" boolean DEFAULT true,
	"created_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "health_checks" (
	"id" serial PRIMARY KEY NOT NULL,
	"status" varchar(20) NOT NULL,
	"details" text,
	"created_at" timestamp DEFAULT now()
);
--> statement-breakpoint
ALTER TABLE "analysis_results" ADD CONSTRAINT "analysis_results_agent_id_agents_id_fk" FOREIGN KEY ("agent_id") REFERENCES "public"."agents"("id") ON DELETE no action ON UPDATE no action;