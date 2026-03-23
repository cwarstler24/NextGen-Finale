import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';

import ProductView from '../../../main/frontend/src/views/ProductView.vue';
import { fetchMock } from '../mocks/browserMocks';

const { addItemMock, currentRoute, pushMock } = vi.hoisted(() => ({
    addItemMock: vi.fn(),
    currentRoute: { value: { params: { product: 'Burger' } } },
    pushMock: vi.fn(),
}));

const burgerOptionsResponse = {
    buns: [
        { id: 101, name: 'Sesame', price: 1.0, quantity: 5 },
        { id: 102, name: 'Pretzel', price: 1.5, quantity: 5 },
    ],
    patties: [
        { id: 201, name: 'Beef', price: 2.5, quantity: 5 },
        { id: 202, name: 'Vegan', price: 3.0, quantity: 5 },
    ],
    toppings: [
        { id: 301, name: 'Lettuce', price: 1.5, quantity: 5 },
        { id: 302, name: 'Tomato', price: 1.0, quantity: 5 },
    ],
};

const friesOptionsResponse = {
    sizes: [
        { id: 401, name: 'Small', price: 0.5, quantity: 5 },
        { id: 403, name: 'Large', price: 2.0, quantity: 5 },
    ],
    types: [
        { id: 501, name: 'Shoestring', price: 0.0, quantity: 5 },
        { id: 503, name: 'Waffle', price: 0.5, quantity: 5 },
    ],
    seasonings: [
        { id: 601, name: 'Salt', price: 0.0, quantity: 5 },
        { id: 602, name: 'Cajun', price: 0.5, quantity: 5 },
        { id: 603, name: 'Garlic', price: 1.0, quantity: 5 },
    ],
};

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

async function waitForOptionsToLoad() {
    await Promise.resolve();
    await Promise.resolve();
    await nextTick();
}

describe('ProductView', () => {
    beforeEach(() => {
        addItemMock.mockReset();
        pushMock.mockReset();
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
                    json: async () => burgerOptionsResponse,
                });
            }

            if (requestUrl.includes('/Items/Fries')) {
                return Promise.resolve({
                    ok: true,
                    json: async () => friesOptionsResponse,
                });
            }

            return Promise.resolve({
                ok: false,
                status: 404,
                statusText: 'Not Found',
                json: async () => ({}),
            });
        });
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('updates burger selections and adds the customized item to the cart', async () => {
        const wrapper = mountProductView('Burger');
        await waitForOptionsToLoad();

        expect(wrapper.text()).toContain('Classic Cheeseburger');
        expect(wrapper.text()).toContain('$6.00');
        expect(wrapper.find('.burger-image-card').exists()).toBe(true);
        expect(wrapper.findAll('button.thumb')).toHaveLength(0);

        await wrapper.get('#buns-input').setValue('102');
        await wrapper.get('#patties-input').setValue('202');
        await wrapper.findAll('input[type="checkbox"]')[0].setValue(true);
        expect(wrapper.text()).toContain('$7.00');

        await wrapper.get('button.primary').trigger('click');

        expect(addItemMock).toHaveBeenCalledWith({
            id: 'burger',
            image: '',
            name: 'Classic Cheeseburger',
            options: [
                { id: '102', name: 'Bun', value: 'Pretzel' },
                {
                    id: '202',
                    name: 'Patty',
                    value: [{ id: '202', name: 'Vegan', quantity: 1 }],
                },
                {
                    id: [
                        { id: '301', quantity: 1 },
                        { id: '302', quantity: 1 },
                    ],
                    name: 'Toppings',
                    value: [
                        { id: '301', name: 'Lettuce', quantity: 1 },
                        { id: '302', name: 'Tomato', quantity: 1 },
                    ],
                },
            ],
            quantity: 1,
            unitPrice: 7,
        });
        expect(wrapper.text()).toContain('Classic Cheeseburger added to cart.');

        vi.advanceTimersByTime(3000);
        await nextTick();

        expect(wrapper.text()).not.toContain('Classic Cheeseburger added to cart.');
    });

    it('renders fries customization and routes back to the main page', async () => {
        const wrapper = mountProductView('Fries');
        await waitForOptionsToLoad();

        expect(wrapper.text()).toContain('Fries');
        expect(wrapper.text()).toContain('Crispy Fries');
        expect(wrapper.text()).toContain('$0.50');

        await wrapper.get('#sizes-input').setValue('403');
        await wrapper.get('#types-input').setValue('503');
        await wrapper.get('#seasonings-input').setValue('603');

        expect(wrapper.text()).toContain('$3.50');

        await wrapper.get('.product-breadcrumbs .hover').trigger('click');

        expect(pushMock).toHaveBeenCalledWith({ name: 'main' });
    });

    it('renders unknown products with fallback content and empty customization', async () => {
        const wrapper = mountProductView('Shake');

        expect(wrapper.text()).toContain('Unknown Product');
        expect(wrapper.text()).toContain('No description available.');
        expect(wrapper.text()).toContain('No customization options are available for this product.');
        expect(wrapper.get('img.product-hero').attributes('src')).toContain('/images/placeholder.png');
        expect(wrapper.findAll('button.thumb')).toHaveLength(0);
        expect(wrapper.text()).toContain('$0.00');

        await wrapper.get('button.primary').trigger('click');

        expect(addItemMock).not.toHaveBeenCalled();
        expect(wrapper.text()).toContain('Please select at least one option before adding to cart.');
    });

    it('clears pending feedback timers when replacing the message and unmounting', async () => {
        const clearTimeoutSpy = vi.spyOn(globalThis, 'clearTimeout');
        const wrapper = mountProductView('Burger');
        await waitForOptionsToLoad();

        await wrapper.get('button.primary').trigger('click');
        await wrapper.get('button.primary').trigger('click');

        expect(clearTimeoutSpy).toHaveBeenCalled();

        wrapper.unmount();

        expect(clearTimeoutSpy).toHaveBeenCalled();
        clearTimeoutSpy.mockRestore();
    });
});