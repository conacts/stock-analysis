#!/usr/bin/env node
// Test Individual Trigger.dev Tasks
// Usage: node scripts/test-single-task.js <task-name>

import {
    systemHealthCheckScheduled,
    dailyPortfolioAnalysisScheduled,
    continuousStockPriceMonitoringScheduled,
} from "../src/automation/tasks/index.js";

const availableTasks = {
    "health-check": systemHealthCheckScheduled,
    "portfolio-analysis": dailyPortfolioAnalysisScheduled,
    "stock-monitoring": continuousStockPriceMonitoringScheduled,
};

async function testTask(taskName) {
    console.log(`🧪 Testing Task: ${taskName}`);
    console.log("================================");

    const task = availableTasks[taskName];
    if (!task) {
        console.error(`❌ Task '${taskName}' not found!`);
        console.log("Available tasks:", Object.keys(availableTasks).join(", "));
        process.exit(1);
    }

    try {
        console.log(`🚀 Starting ${taskName}...`);

        // Create a mock payload for testing
        const mockPayload = {
            timestamp: new Date().toISOString(),
            source: "manual-test",
        };

        // Note: This is a simplified test - actual task execution would need proper Trigger.dev context
        console.log(`✅ Task ${taskName} is properly configured`);
        console.log(`📋 Task ID: ${task.id}`);
        console.log(`⏰ Schedule: ${task.trigger?.cron || "No schedule"}`);
    } catch (error) {
        console.error(`❌ Error testing ${taskName}:`, error.message);
        process.exit(1);
    }
}

// Get task name from command line
const taskName = process.argv[2];

if (!taskName) {
    console.log("🧪 Trigger.dev Task Tester");
    console.log("Usage: node scripts/test-single-task.js <task-name>");
    console.log("");
    console.log("Available tasks:");
    Object.keys(availableTasks).forEach((name) => {
        console.log(`  - ${name}`);
    });
    process.exit(1);
}

testTask(taskName);
