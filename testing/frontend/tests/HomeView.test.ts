import { beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';

import HomeView from '../../../main/frontend/src/views/HomeView.vue';

const { pushMock } = vi.hoisted(() => ({
    pushMock: vi.fn(),
}));

vi.mock('vue-router', () => ({
    useRouter: () => ({
        push: pushMock,
    }),
}));

describe('HomeView', () => {
    beforeEach(() => {
        pushMock.mockReset();
    });

    it('renders home page content and routes to details', async () => {
        const wrapper = mount(HomeView);

        expect(wrapper.text()).toContain('Main Menu');

        await wrapper.get('button.primary').trigger('click');

        expect(pushMock).toHaveBeenCalledWith({ name: 'details' });
    });
});