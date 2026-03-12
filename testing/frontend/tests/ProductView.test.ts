import { beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';

import ProductView from '../../../main/frontend/src/views/ProductView.vue';

const { pushMock } = vi.hoisted(() => ({
    pushMock: vi.fn(),
}));

vi.mock('vue-router', () => ({
    useRouter: () => ({
        push: pushMock,
    }),
}));

describe('ProductView', () => {
    beforeEach(() => {
        pushMock.mockReset();
    });

    it('shows selected product in breadcrumbs and supports back navigation', async () => {
        const wrapper = mount(ProductView, {
            global: {
                mocks: {
                    $route: {
                        params: { product: 'Burger' },
                    },
                },
            },
        });

        expect(wrapper.text()).toContain('Burger');

        await wrapper.get('button.secondary').trigger('click');

        expect(pushMock).toHaveBeenCalledWith({ name: 'home' });
    });
});