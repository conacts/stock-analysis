import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    // Global test setup
    globals: true,
    environment: 'node',

    // Test file patterns - co-located with source code
    include: ['src/**/*.test.ts', 'src/**/*.spec.ts'],
    exclude: ['node_modules', 'dist', '**/*.d.ts'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json'],
      reportsDirectory: 'coverage',
      include: ['src/**/*.ts'],
      exclude: [
        'src/**/*.d.ts',
        'src/**/*.test.ts',
        'src/**/*.spec.ts',
        'src/generated/**',
        'trigger/**',
      ],
      thresholds: {
        global: {
          branches: 85,
          functions: 85,
          lines: 85,
          statements: 85,
        },
      },
    },

    // Test categories via patterns
    testNamePattern: process.env.VITEST_NAME_PATTERN,

    // Timeout configuration
    testTimeout: 30000,
    hookTimeout: 30000,

    // Parallel execution
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
        maxThreads: 4,
        minThreads: 1,
      },
    },

    // Setup files
    setupFiles: ['setup.ts'],

    // Environment variables
    env: {
      NODE_ENV: 'test',
    },

    // Mock configuration
    mockReset: true,
    clearMocks: true,
    restoreMocks: true,

    // Reporter configuration - clean text output only
    reporters: ['verbose'],
  },

  // Path resolution
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },

  // Define test categories
  define: {
    __TEST_CATEGORIES__: {
      UNIT: 'unit',
      INTEGRATION: 'integration',
      LLM: 'llm',
      FAST: 'fast',
    },
  },
});
