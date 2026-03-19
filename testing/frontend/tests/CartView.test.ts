import { beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';

import CartView from '../../../main/frontend/src/views/CartView.vue';

const { pushMock } = vi.hoisted(() => ({
    pushMock: vi.fn(),
}));

vi.mock('vue-router', () => ({
    useRouter: () => ({
        push: pushMock,
    }),
}));

type CartOptionValue = string | string[] | null;

type CartEntry = {
    image: string;
    lineTotal: number;
    name: string;
    options: Array<{ name: string; value: CartOptionValue }>;
    quantity: number;
    signature: string;
};

function createMockRef<T>(value: T) {
    return {
        __v_isRef: true,
        value,
    };
}

const { cartState, clearCartMock, removeItemMock } = vi.hoisted(() => ({
    cartState: {
        cartCount: createMockRef(0),
        cartEntries: createMockRef([] as CartEntry[]),
        cartTotal: createMockRef(0),
    },
    clearCartMock: vi.fn(),
    removeItemMock: vi.fn(),
}));

vi.mock('../../../main/frontend/src/composables/useCart', () => ({
    useCart: () => ({
        cartEntries: cartState.cartEntries,
        cartCount: cartState.cartCount,
        cartTotal: cartState.cartTotal,
        clearCart: clearCartMock,
        removeItem: removeItemMock,
    }),
}));

describe('CartView', () => {
    beforeEach(() => {
        cartState.cartCount.value = 0;
        cartState.cartEntries.value = [];
        cartState.cartTotal.value = 0;
        clearCartMock.mockReset();
        removeItemMock.mockReset();
        pushMock.mockReset();
    });

    it('shows the empty cart state when there are no items', () => {
        const wrapper = mount(CartView);

        expect(wrapper.text()).toContain('Your cart is currently empty.');
        expect(wrapper.find('.cart-layout').exists()).toBe(false);
        expect(wrapper.find('button.secondary').exists()).toBe(false);
    });

    it('renders cart items and supports removing, clearing, and purchasing', async () => {
        cartState.cartCount.value = 2;
        cartState.cartTotal.value = 9.5;
        cartState.cartEntries.value = [
            {
                image: '/images/Burger1.png',
                lineTotal: 9.5,
                name: 'Classic Burger',
                options: [
                    { name: 'Bun', value: 'Pretzel' },
                    { name: 'Seasoning', value: ['Cajun', 'Salt'] },
                    { name: 'Extras', value: null },
                ],
                quantity: 2,
                signature: 'burger-signature',
            },
        ];

        const wrapper = mount(CartView);

        expect(wrapper.text()).toContain('2 items ready for checkout.');
        expect(wrapper.text()).toContain('Classic Burger');
        expect(wrapper.text()).toContain('Quantity: 2');
        expect(wrapper.text()).toContain('Cajun, Salt');
        expect(wrapper.text()).toContain('None selected');
        expect(wrapper.text()).toContain('$9.50');

        await wrapper.get('button.remove-button').trigger('click');
        expect(removeItemMock).toHaveBeenCalledWith('burger-signature');

        await wrapper.get('.cart-summary button.secondary').trigger('click');
        expect(clearCartMock).toHaveBeenCalledTimes(1);

        await wrapper.get('button.purchase-button').trigger('click');
        expect(pushMock).toHaveBeenCalledWith({ name: 'checkout' });
        expect(clearCartMock).toHaveBeenCalledTimes(1);
    });

    it('renders singular checkout text and empty array options as none selected', () => {
        cartState.cartCount.value = 1;
        cartState.cartTotal.value = 4;
        cartState.cartEntries.value = [
            {
                image: '',
                lineTotal: 4,
                name: 'Crispy Fries',
                options: [
                    { name: 'Seasoning', value: [] },
                    { name: 'Type', value: 'Curly' },
                ],
                quantity: 1,
                signature: 'fries-signature',
            },
        ];

        const wrapper = mount(CartView);

        expect(wrapper.text()).toContain('1 item ready for checkout.');
        expect(wrapper.text()).toContain('None selected');
        expect(wrapper.text()).toContain('Curly');
        expect(wrapper.find('.cart-item-image').exists()).toBe(false);
    });
});