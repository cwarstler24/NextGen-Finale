import { beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';

import App from '../../../main/frontend/src/App.vue';

const { appState } = vi.hoisted(() => ({
    appState: {
        cartCount: 0,
    },
}));

vi.mock('../../../main/frontend/src/composables/useCart', () => ({
    useCart: () => ({
        cartCount: appState.cartCount,
    }),
}));

describe('App', () => {
    beforeEach(() => {
        appState.cartCount = 0;
    });

    it('renders the navigation shell and router outlet', () => {
        const wrapper = mount(App, {
            global: {
                stubs: {
                    RouterLink: {
                        props: ['to'],
                        template: '<a><slot /></a>',
                    },
                    RouterView: {
                        template: '<div class="router-view-stub">Current Route</div>',
                    },
                },
            },
        });

        expect(wrapper.text()).toContain('The Frying Saucer');
        expect(wrapper.text()).toContain('Burger');
        expect(wrapper.text()).toContain('Fries');
        expect(wrapper.text()).toContain('Cart');
        expect(wrapper.text()).toContain('Current Route');
        expect(wrapper.find('.cart-badge').exists()).toBe(false);
    });

    it('shows the cart badge when items are in the cart', () => {
        appState.cartCount = 3;

        const wrapper = mount(App, {
            global: {
                stubs: {
                    RouterLink: {
                        props: ['to'],
                        template: '<a><slot /></a>',
                    },
                    RouterView: true,
                },
            },
        });

        expect(wrapper.get('.cart-badge').text()).toBe('3');
    });
});