import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    include: ['testing/frontend/tests/**/*.test.{ts,js,tsx,jsx}'],
    globals: true,
    reporters: ['default'],
    coverage: {
      enabled: false
    }
  },
});
