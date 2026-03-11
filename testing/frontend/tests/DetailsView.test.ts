import { beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';

import DetailsView from '../../../main/frontend/src/views/DetailsView.vue';

const { pushMock } = vi.hoisted(() => ({
    pushMock: vi.fn(),
}));

vi.mock('vue-router', () => ({
    useRouter: () => ({
        push: pushMock,
    }),
}));

describe('DetailsView', () => {
    beforeEach(() => {
        pushMock.mockReset();
    });

    it('renders details page and routes back to home', async () => {
        const wrapper = mount(DetailsView);

        expect(wrapper.text()).toContain('Details');

        await wrapper.get('button.secondary').trigger('click');

        expect(pushMock).toHaveBeenCalledWith({ name: 'home' });
    });
});