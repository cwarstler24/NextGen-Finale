import { beforeEach, describe, expect, it, vi } from 'vitest';

async function loadRouter() {
    return import('../../../main/frontend/src/router/index.js');
}

describe('router', () => {
    beforeEach(() => {
        vi.resetModules();
        window.history.replaceState({}, '', '/');
    });

    it('registers the expected named routes', async () => {
        const { default: router } = await loadRouter();

        expect(router.getRoutes().map((route) => route.name)).toEqual(
            expect.arrayContaining(['main', 'product', 'cart', 'burger-menu'])
        );

        const productRoute = router.resolve('/product/Burger');

        expect(productRoute.name).toBe('product');
        expect(productRoute.params.product).toBe('Burger');
    }, 15000);

    it('navigates to cart routes', async () => {
        const { default: router } = await loadRouter();

        await router.push('/cart');

        expect(router.currentRoute.value.name).toBe('cart');
        expect(router.currentRoute.value.fullPath).toBe('/cart');
    });
});