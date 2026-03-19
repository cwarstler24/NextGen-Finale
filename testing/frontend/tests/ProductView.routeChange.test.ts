import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { fetchMock } from '../mocks/browserMocks';

async function loadProductViewWithRoute(product = 'Burger') {
    vi.resetModules();

    const { shallowRef, nextTick } = await import('vue');
    const routeRef = shallowRef({ params: { product } });
    const addItemMock = vi.fn();
    const pushMock = vi.fn();

    vi.doMock('vue-router', () => ({
        useRouter: () => ({
            currentRoute: routeRef,
            push: pushMock,
        }),
    }));
    vi.doMock('../../../main/frontend/src/composables/useCart', () => ({
        useCart: () => ({
            addItem: addItemMock,
        }),
    }));

    const { default: ProductView } = await import('../../../main/frontend/src/views/ProductView.vue');

    return {
        ProductView,
        addItemMock,
        nextTick,
        pushMock,
        routeRef,
    };
}

async function waitForOptionsToLoad(nextTick: () => Promise<void>) {
    await Promise.resolve();
    await Promise.resolve();
    await nextTick();
}

describe('ProductView route changes', () => {
    beforeEach(() => {
        vi.useFakeTimers();
        fetchMock.mockReset();
        fetchMock.mockImplementation((input: unknown) => {
            const requestUrl = typeof input === 'string'
                ? input
                : input instanceof URL
                    ? input.toString()
                    : (input as { url: string }).url;

            if (requestUrl.includes('/Items/Burger')) {
                return Promise.resolve({
                    ok: true,
                    json: async () => ({
                        buns: [{ id: 101, name: 'Sesame', price: 1, quantity: 5 }],
                        patties: [{ id: 201, name: 'Beef', price: 2.5, quantity: 5 }],
                        toppings: [],
                    }),
                });
            }

            if (requestUrl.includes('/Items/Fries')) {
                return Promise.resolve({
                    ok: true,
                    json: async () => ({
                        sizes: [{ id: 401, name: 'Small', price: 0.5, quantity: 5 }],
                        types: [{ id: 501, name: 'Shoestring', price: 0, quantity: 5 }],
                        seasonings: [{ id: 601, name: 'Salt', price: 0, quantity: 5 }],
                    }),
                });
            }

            return Promise.resolve({
                ok: false,
                status: 404,
                statusText: 'Not Found',
                json: async () => ({}),
            });
        });
    });

    afterEach(() => {
        vi.useRealTimers();
        vi.resetModules();
    });

    it('resets the selected image and feedback when the route product changes', async () => {
        const { ProductView, nextTick, routeRef } = await loadProductViewWithRoute();
        const wrapper = mount(ProductView, {
            global: {
                mocks: {
                    $route: {
                        params: { product: 'Burger' },
                    },
                },
            },
        });
        await waitForOptionsToLoad(nextTick);

        expect(wrapper.find('.burger-image-card').exists()).toBe(true);
        await wrapper.get('button.primary').trigger('click');
        await nextTick();

        expect(wrapper.text()).toContain('Classic Cheeseburger added to cart.');

        routeRef.value = { params: { product: 'Fries' } };
        await waitForOptionsToLoad(nextTick);
        await nextTick();

        expect(wrapper.get('img.product-hero').attributes('src')).toContain('/images/items/shoestring_fries.PNG');
        expect(wrapper.text()).not.toContain('added to cart.');

        wrapper.unmount();
    });
});