import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';

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

describe('ProductView route changes', () => {
    beforeEach(() => {
        vi.useFakeTimers();
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

        await wrapper.findAll('button.thumb')[2].trigger('click');
        await wrapper.get('button.primary').trigger('click');

        expect(wrapper.get('img.product-hero').attributes('src')).toContain('/images/Burger3.png');
        expect(wrapper.text()).toContain('Classic Burger added to cart.');

        routeRef.value = { params: { product: 'Fries' } };
        await nextTick();

        expect(wrapper.get('img.product-hero').attributes('src')).toContain('/images/Fries1.png');
        expect(wrapper.text()).not.toContain('added to cart.');

        wrapper.unmount();
    });
});