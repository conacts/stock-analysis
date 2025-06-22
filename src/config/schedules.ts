/**
 * Schedule Configuration
 *
 * Configuration for Trigger.dev scheduled tasks and cron jobs.
 * Type safety ensures valid configurations.
 */

export interface ScheduleConfig {
  cron: string;
  timezone: string;
  enabled: boolean;
}

export const scheduleConfig = {
  healthCheck: {
    cron: '0 * * * *',
    timezone: 'UTC',
    enabled: true,
  } as ScheduleConfig,
} as const;
