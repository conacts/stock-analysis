# 📅 Schedule Optimization Guide

Due to Trigger.dev's 10-schedule limit on the free tier, we need to optimize our scheduled tasks.

## 🎯 Current Situation

**Total Scheduled Tasks**: 12
**Trigger.dev Limit**: 10
**Need to Remove**: 2 tasks

## 📊 Task Priority Analysis

### **Essential Tasks (Keep - 8 tasks)**

1. **`enhancedDailyPortfolioAnalysis`** - Daily at 9:30 AM

    - Core AI-powered portfolio analysis
    - **Priority: CRITICAL**

2. **`portfolioRiskMonitor`** - Every 15 minutes

    - Real-time risk monitoring
    - **Priority: CRITICAL**

3. **`continuousStockPriceMonitoringScheduled`** - Every 5 minutes

    - Core price monitoring
    - **Priority: CRITICAL**

4. **`systemHealthCheckScheduled`** - Every 15 minutes

    - System health monitoring
    - **Priority: HIGH**

5. **`dailyHealthSummaryScheduled`** - Daily at 6 AM

    - Daily health reports
    - **Priority: HIGH**

6. **`endOfDayPortfolioSummaryScheduled`** - Daily at 4:30 PM

    - End-of-day summaries
    - **Priority: HIGH**

7. **`afterHoursPriceAlertSetupScheduled`** - Daily at 4 PM

    - After-hours alert setup
    - **Priority: MEDIUM**

8. **`preMarketAlertReviewScheduled`** - Daily at 8:30 AM
    - Pre-market review
    - **Priority: MEDIUM**

### **Candidates for Removal (2 tasks)**

9. **`simplifiedEnhancedAnalysis`** - Daily at 9 AM

    - **REMOVE**: Redundant with `enhancedDailyPortfolioAnalysis`
    - Same functionality, different implementation

10. **`dailyPortfolioAnalysisScheduled`** - Daily at 8 AM
    - **REMOVE**: Redundant with `enhancedDailyPortfolioAnalysis`
    - Older implementation, less features

### **Weekly Tasks (Keep but consolidate - 2 tasks)**

11. **`weeklyHealthAnalysisScheduled`** - Weekly on Sundays

    -   **KEEP**: Important for weekly health trends

12. **`weeklyPortfolioAnalysisScheduled`** - Weekly on Sundays

    -   **KEEP**: Important for weekly portfolio analysis

13. **`weeklyAlertCleanupScheduled`** - Weekly on Sundays
    -   **CONSOLIDATE**: Merge into `weeklyHealthAnalysisScheduled`

## 🔧 Optimization Strategy

### **Phase 1: Remove Redundant Tasks**

1. **Remove `simplifiedEnhancedAnalysis`**

    - Functionality covered by `enhancedDailyPortfolioAnalysis`
    - Same time slot (9 AM vs 9:30 AM)

2. **Remove `dailyPortfolioAnalysisScheduled`**
    - Older implementation
    - Enhanced version provides better features

### **Phase 2: Consolidate Weekly Tasks**

Merge `weeklyAlertCleanupScheduled` functionality into `weeklyHealthAnalysisScheduled`:

```typescript
export const weeklyHealthAnalysisScheduled = schedules.task({
    id: "weekly-health-analysis",
    cron: "0 10 * * 0", // Sundays at 10 AM
    run: async (payload) => {
        // Existing health analysis
        await performWeeklyHealthAnalysis();

        // Add alert cleanup functionality
        await performWeeklyAlertCleanup();
    },
});
```

## 📋 Final Schedule List (10 tasks)

### **Critical Operations (3 tasks)**

1. `enhancedDailyPortfolioAnalysis` - Daily 9:30 AM
2. `portfolioRiskMonitor` - Every 15 minutes
3. `continuousStockPriceMonitoringScheduled` - Every 5 minutes

### **Daily Operations (4 tasks)**

4. `systemHealthCheckScheduled` - Every 15 minutes
5. `dailyHealthSummaryScheduled` - Daily 6 AM
6. `endOfDayPortfolioSummaryScheduled` - Daily 4:30 PM
7. `afterHoursPriceAlertSetupScheduled` - Daily 4 PM
8. `preMarketAlertReviewScheduled` - Daily 8:30 AM

### **Weekly Operations (2 tasks)**

9. `weeklyHealthAnalysisScheduled` - Weekly Sundays (includes alert cleanup)
10. `weeklyPortfolioAnalysisScheduled` - Weekly Sundays

## 🚀 Implementation Steps

### **Step 1: Comment Out Redundant Tasks**

```typescript
// TEMPORARILY DISABLED - Redundant with enhancedDailyPortfolioAnalysis
// export const simplifiedEnhancedAnalysis = schedules.task({
//   id: "simplified-enhanced-analysis",
//   cron: "0 9 * * 1-5",
//   run: async (payload) => {
//     // ... implementation
//   },
// });

// TEMPORARILY DISABLED - Replaced by enhanced version
// export const dailyPortfolioAnalysisScheduled = schedules.task({
//   id: "daily-portfolio-analysis",
//   cron: "0 8 * * 1-5",
//   run: async (payload) => {
//     // ... implementation
//   },
// });
```

### **Step 2: Consolidate Weekly Tasks**

Merge alert cleanup into weekly health analysis.

### **Step 3: Test Development Mode**

```bash
npx trigger.dev@latest dev
```

Should now work with 10 or fewer schedules.

## 💰 Upgrade Recommendation

For a production AI trading system, consider upgrading to:

-   **Hobby Plan**: More schedules, better limits
-   **Pro Plan**: Production-grade features
-   **Enterprise**: Custom limits and support

## 🔄 Future Optimization

When you upgrade or need more schedules:

1. **Re-enable removed tasks**
2. **Add more granular monitoring**
3. **Implement user-specific schedules**
4. **Add more sophisticated analysis tasks**

---

**💡 Key Takeaway**: We can optimize from 12 to 10 schedules by removing redundant tasks while keeping all essential functionality. This gets us running immediately while we decide on upgrading.
