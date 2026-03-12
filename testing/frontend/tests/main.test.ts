import { afterEach, describe, expect, it, vi } from 'vitest';

describe('frontend entrypoint', () => {
    afterEach(() => {
        vi.resetModules();
        vi.unmock('../../../main/frontend/src/App.vue');
        vi.unmock('../../../main/frontend/src/router');
        vi.unmock('vue');
    });

    it('creates the app, installs the router, and mounts it', async () => {
        const mountMock = vi.fn();
        const app = {
            mount: mountMock,
            use: vi.fn(() => app),
        };
        const createAppMock = vi.fn(() => app);
        const routerStub = { name: 'router-stub' };

        vi.doMock('vue', () => ({
            createApp: createAppMock,
        }));
        vi.doMock('../../../main/frontend/src/App.vue', () => ({
            default: { name: 'AppStub' },
        }));
        vi.doMock('../../../main/frontend/src/router', () => ({
            default: routerStub,
        }));

        await import('../../../main/frontend/src/main.js');

        expect(createAppMock).toHaveBeenCalled();
        expect(app.use).toHaveBeenCalledWith(routerStub);
        expect(mountMock).toHaveBeenCalledWith('#app');
    });
});