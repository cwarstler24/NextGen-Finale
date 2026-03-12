import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';

import BurgerOptionsComp from '../../../main/frontend/src/components/BurgerOptionsComp.vue';
import FriesOptionsComp from '../../../main/frontend/src/components/FriesOptionsComp.vue';

const componentCases = [
    ['BurgerOptionsComp', BurgerOptionsComp],
    ['FriesOptionsComp', FriesOptionsComp],
];

describe.each(componentCases)('%s', (_name, component) => {
    it('emits single and multiple selection changes, including fallback branches', async () => {
        const wrapper = mount(component, {
            props: {
                modelValue: {
                    bun: '101',
                    toppings: 'not-an-array',
                },
                optionGroups: [
                    {
                        items: [
                            { id: '101', name: 'Regular', price: 0, quantity: 1 },
                            { id: '102', name: 'Pretzel', price: 1.5, quantity: 0 },
                        ],
                        key: 'bun',
                        label: 'Bun',
                        selectionMode: 'single',
                    },
                    {
                        items: [
                            { id: '301', name: 'Lettuce', price: 0, quantity: 1 },
                            { id: '302', name: 'Tomato', price: 0.5, quantity: 1 },
                        ],
                        key: 'toppings',
                        label: 'Toppings',
                        selectionMode: 'multiple',
                    },
                ],
            },
        });

        expect(wrapper.text()).toContain('Regular');
        expect(wrapper.text()).not.toContain('Regular + $0.00');
        expect(wrapper.text()).toContain('Tomato + $0.50');
        expect(wrapper.findAll('option')[1].attributes('disabled')).toBeDefined();

        await wrapper.get('#bun-input').setValue('102');
        await wrapper.findAll('input[type="checkbox"]')[0].setValue(true);

        let emissions = wrapper.emitted('update:modelValue');
        expect(emissions?.[0]?.[0]).toEqual({ bun: '102', toppings: 'not-an-array' });
        expect(emissions?.[1]?.[0]).toEqual({ bun: '101', toppings: ['301'] });

        await wrapper.setProps({
            modelValue: {
                bun: '101',
                toppings: ['301', '302'],
            },
        });
        await wrapper.findAll('input[type="checkbox"]')[1].setValue(false);

        emissions = wrapper.emitted('update:modelValue');
        expect(emissions?.[2]?.[0]).toEqual({ bun: '101', toppings: ['301'] });
    });
});