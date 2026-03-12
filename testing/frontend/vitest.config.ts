import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vitest/config';
import { resolve } from 'node:path';

export default defineConfig({
    plugins: [vue()],
    publicDir: resolve(__dirname, '../../main/frontend/public'),
    test: {
        environment: 'jsdom',
        include: ['testing/frontend/tests/**/*.test.{ts,js,tsx,jsx}'],
        setupFiles: ['testing/frontend/setupTests.ts'],
        globals: true,
        reporters: ['default'],
        coverage: {
            enabled: true,
            reporter: ['text', 'html'],
            include: ['main/frontend/src/**/*.{ts,js,vue}'],
        }
    },
});
