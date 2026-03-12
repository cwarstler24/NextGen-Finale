import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';

import ProductView from '../../../main/frontend/src/views/ProductView.vue';

const { addItemMock, currentRoute, pushMock } = vi.hoisted(() => ({
    addItemMock: vi.fn(),
    currentRoute: { value: { params: { product: 'Burger' } } },
    pushMock: vi.fn(),
}));

vi.mock('vue-router', () => ({
    useRouter: () => ({
        currentRoute,
        push: pushMock,
    }),
}));

vi.mock('../../../main/frontend/src/composables/useCart', () => ({
    useCart: () => ({
        addItem: addItemMock,
    }),
}));

function mountProductView(product = 'Burger') {
    currentRoute.value = { params: { product } };

    return mount(ProductView, {
        global: {
            mocks: {
                $route: {
                    params: { product },
                },
            },
        },
    });
}

describe('ProductView', () => {
    beforeEach(() => {
        addItemMock.mockReset();
        pushMock.mockReset();
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('updates burger selections and adds the customized item to the cart', async () => {
        const wrapper = mountProductView('Burger');

        expect(wrapper.text()).toContain('Classic Burger');
        expect(wrapper.text()).toContain('$4.00');

        await wrapper.get('#buns-input').setValue('102');
        await wrapper.get('#patties-input').setValue('202');
        await wrapper.findAll('input[type="checkbox"]')[0].setValue(true);
        await wrapper.findAll('button.thumb')[2].trigger('click');

        expect(wrapper.get('img.product-hero').attributes('src')).toContain('/images/Burger3.png');
        expect(wrapper.text()).toContain('$6.00');

        await wrapper.get('button.primary').trigger('click');

        expect(addItemMock).toHaveBeenCalledWith({
            id: 'burger',
            image: '/images/Burger1.png',
            name: 'Classic Burger',
            options: [
                { id: '102', name: 'Bun', value: 'Pretzel' },
                { id: '202', name: 'Patty', value: 'Vegan' },
                { id: ['301'], name: 'Toppings', value: ['Lettuce'] },
            ],
            quantity: 1,
            unitPrice: 6,
        });
        expect(wrapper.text()).toContain('Classic Burger added to cart.');

        vi.advanceTimersByTime(3000);
        await nextTick();

        expect(wrapper.text()).not.toContain('Classic Burger added to cart.');
    });

    it('renders fries customization and routes back to the main page', async () => {
        const wrapper = mountProductView('Fries');

        expect(wrapper.text()).toContain('Fries');
        expect(wrapper.text()).toContain('Crispy Fries');
        expect(wrapper.text()).toContain('$0.50');

        await wrapper.get('#sizes-input').setValue('403');
        await wrapper.get('#types-input').setValue('503');

        const seasoningCheckboxes = wrapper.findAll('input[type="checkbox"]');
        await seasoningCheckboxes[1].setValue(true);
        await seasoningCheckboxes[2].setValue(true);

        expect(wrapper.text()).toContain('$4.00');

        await wrapper.get('.product-breadcrumbs .hover').trigger('click');

        expect(pushMock).toHaveBeenCalledWith({ name: 'main' });
    });

    it('renders unknown products with fallback content and empty customization', async () => {
        const wrapper = mountProductView('Shake');

        expect(wrapper.text()).toContain('Shake');
        expect(wrapper.text()).toContain('Unknown Product');
        expect(wrapper.text()).toContain('No description available.');
        expect(wrapper.text()).toContain('No customization options are available for this product.');
        expect(wrapper.get('img.product-hero').attributes('src')).toContain('/images/placeholder.png');
        expect(wrapper.findAll('button.thumb')).toHaveLength(3);
        expect(wrapper.text()).toContain('$0.00');

        await wrapper.get('button.primary').trigger('click');

        expect(addItemMock).toHaveBeenCalledWith({
            id: 'shake',
            image: '/images/placeholder.png',
            name: 'Unknown Product',
            options: [],
            quantity: 1,
            unitPrice: 0,
        });
    });

    it('clears pending feedback timers when replacing the message and unmounting', async () => {
        const clearTimeoutSpy = vi.spyOn(globalThis, 'clearTimeout');
        const wrapper = mountProductView('Burger');

        await wrapper.get('button.primary').trigger('click');
        await wrapper.get('button.primary').trigger('click');

        expect(clearTimeoutSpy).toHaveBeenCalled();

        wrapper.unmount();

        expect(clearTimeoutSpy).toHaveBeenCalled();
        clearTimeoutSpy.mockRestore();
    });
});