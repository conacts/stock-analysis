#!/usr/bin/env bun
/**
 * Generate TypeScript types from Prisma schema
 * This ensures type consistency between Python models and TypeScript automation
 */

import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

interface PrismaModel {
	name: string;
	fields: PrismaField[];
}

interface PrismaField {
	name: string;
	type: string;
	optional: boolean;
	array: boolean;
}

function parsePrismaSchema(schemaContent: string): PrismaModel[] {
	const models: PrismaModel[] = [];
	const modelRegex = /model\s+(\w+)\s*{([^}]+)}/g;

	let match;
	while ((match = modelRegex.exec(schemaContent)) !== null) {
		const modelName = match[1];
		const modelBody = match[2];

		const fields = parseModelFields(modelBody);
		models.push({ name: modelName, fields });
	}

	return models;
}

function parseModelFields(modelBody: string): PrismaField[] {
	const fields: PrismaField[] = [];
	const lines = modelBody.split('\n');

	for (const line of lines) {
		const trimmed = line.trim();
		if (!trimmed || trimmed.startsWith('@@') || trimmed.startsWith('//')) {
			continue;
		}

		// Parse field definition: fieldName Type? @attributes
		const fieldMatch = trimmed.match(/^(\w+)\s+([^@\s]+)/);
		if (fieldMatch) {
			const fieldName = fieldMatch[1];
			const fieldType = fieldMatch[2];

			const optional = fieldType.includes('?');
			const array = fieldType.includes('[]');
			const cleanType = fieldType.replace(/[\?\[\]]/g, '');

			fields.push({
				name: fieldName,
				type: mapPrismaTypeToTS(cleanType),
				optional,
				array
			});
		}
	}

	return fields;
}

function mapPrismaTypeToTS(prismaType: string): string {
	const typeMap: Record<string, string> = {
		'Int': 'number',
		'String': 'string',
		'Boolean': 'boolean',
		'DateTime': 'Date',
		'Decimal': 'number',
		'Json': 'any',
		'Float': 'number'
	};

	return typeMap[prismaType] || prismaType;
}

function generateTypeScript(models: PrismaModel[]): string {
	let output = `// Auto-generated TypeScript types from Prisma schema
// DO NOT EDIT MANUALLY - Run 'bun run scripts/generate-types.ts' to regenerate

`;

	// Generate base model interfaces
	for (const model of models) {
		output += `export interface ${model.name} {\n`;

		for (const field of model.fields) {
			const optional = field.optional ? '?' : '';
			const array = field.array ? '[]' : '';
			output += `  ${field.name}${optional}: ${field.type}${array};\n`;
		}

		output += `}\n\n`;
	}

	// Generate payload types for automation
	output += `// Automation payload types\n`;
	output += `export interface StockAnalysisPayload {\n`;
	output += `  symbols?: string[];\n`;
	output += `  forceRun?: boolean;\n`;
	output += `  sector?: string;\n`;
	output += `  deepAnalysis?: boolean;\n`;
	output += `}\n\n`;

	output += `export interface PortfolioPayload {\n`;
	output += `  portfolioId?: number;\n`;
	output += `  action?: 'monitor' | 'rebalance' | 'snapshot';\n`;
	output += `}\n\n`;

	output += `export interface AlertPayload {\n`;
	output += `  type: 'stock' | 'portfolio' | 'system';\n`;
	output += `  symbol?: string;\n`;
	output += `  portfolioId?: number;\n`;
	output += `  threshold?: number;\n`;
	output += `  message?: string;\n`;
	output += `}\n\n`;

	// Generate result types
	output += `// Result types\n`;
	output += `export interface AnalysisResult {\n`;
	output += `  status: 'completed' | 'failed' | 'skipped';\n`;
	output += `  timestamp: string;\n`;
	output += `  date: string;\n`;
	output += `  stocksAnalyzed: number;\n`;
	output += `  topPicks?: Array<{\n`;
	output += `    symbol: string;\n`;
	output += `    score: string;\n`;
	output += `    rating: string;\n`;
	output += `  }>;\n`;
	output += `  data?: any;\n`;
	output += `  error?: string;\n`;
	output += `}\n\n`;

	output += `export interface PortfolioResult {\n`;
	output += `  status: 'completed' | 'failed' | 'skipped';\n`;
	output += `  timestamp: string;\n`;
	output += `  portfolioId?: number;\n`;
	output += `  totalValue?: number;\n`;
	output += `  dayChange?: number;\n`;
	output += `  dayChangePct?: number;\n`;
	output += `  positionsCount?: number;\n`;
	output += `  error?: string;\n`;
	output += `}\n\n`;

	return output;
}

// Main execution
try {
	console.log('🔄 Generating TypeScript types from Prisma schema...');

	const schemaPath = join(process.cwd(), 'prisma', 'schema.prisma');
	const schemaContent = readFileSync(schemaPath, 'utf-8');

	const models = parsePrismaSchema(schemaContent);
	const typeScript = generateTypeScript(models);

	const outputPath = join(process.cwd(), 'src', 'automation', 'shared', 'generated-types.ts');
	writeFileSync(outputPath, typeScript);

	console.log(`✅ Generated ${models.length} model types`);
	console.log(`📁 Output: ${outputPath}`);

} catch (error) {
	console.error('❌ Failed to generate types:', error);
	process.exit(1);
}
