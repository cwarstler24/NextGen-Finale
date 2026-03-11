import { beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';

import MainView from '../../../main/frontend/src/views/MainView.vue';

const { pushMock } = vi.hoisted(() => ({
    pushMock: vi.fn(),
}));

vi.mock('vue-router', () => ({
    useRouter: () => ({
        push: pushMock,
    }),
}));

describe('MainView', () => {
    beforeEach(() => {
        pushMock.mockReset();
    });

    it('routes to each product page from main page cards', async () => {
        const wrapper = mount(MainView);
        const cards = wrapper.findAll('.product-card');

        expect(cards).toHaveLength(2);

        await cards[0].trigger('click');
        expect(pushMock).toHaveBeenNthCalledWith(1, {
            name: 'product',
            params: { product: 'Burger' },
        });

        await cards[1].trigger('click');
        expect(pushMock).toHaveBeenNthCalledWith(2, {
            name: 'product',
            params: { product: 'Fries' },
        });
    });
});