import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';

import BurgerOptionsComp from '../../../main/frontend/src/components/BurgerOptionsComp.vue';
import FriesOptionsComp from '../../../main/frontend/src/components/FriesOptionsComp.vue';

describe('BurgerOptionsComp', () => {
    it('emits bun and topping selection changes using the current selection model', async () => {
        const wrapper = mount(BurgerOptionsComp, {
            props: {
                modelValue: {
                    buns: '101',
                    patties: { id: '201', quantity: 1 },
                    toppings: 'not-an-array',
                },
                optionGroups: [
                    {
                        items: [
                            { id: '101', name: 'Regular', price: 0, quantity: 1 },
                            { id: '102', name: 'Pretzel', price: 1.5, quantity: 0 },
                        ],
                        key: 'buns',
                        label: 'Bun',
                        selectionMode: 'single',
                    },
                    {
                        items: [
                            { id: '201', name: 'Single', price: 2.5, quantity: 2 },
                            { id: '202', name: 'Double', price: 4, quantity: 1 },
                        ],
                        key: 'patties',
                        label: 'Patty',
                        selectionMode: 'single_quantity',
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

        const bunOptions = wrapper.get('#buns-input').findAll('option');
        expect(bunOptions[0].text()).toBe('Regular · Included');
        expect(bunOptions[1].text()).toBe('Pretzel · +$1.50');
        expect(bunOptions[1].attributes('disabled')).toBeDefined();

        await wrapper.get('#buns-input').setValue('102');
        await wrapper.findAll('input[type="checkbox"]')[0].setValue(true);

        let emissions = wrapper.emitted('update:modelValue');
        expect(emissions?.[0]?.[0]).toEqual({
            buns: '102',
            patties: { id: '201', quantity: 1 },
            toppings: 'not-an-array',
        });
        expect(emissions?.[1]?.[0]).toEqual({
            buns: '101',
            patties: { id: '201', quantity: 1 },
            toppings: [{ id: '301', quantity: 1 }],
        });

        await wrapper.setProps({
            modelValue: {
                buns: '101',
                patties: { id: '201', quantity: 1 },
                toppings: [
                    { id: '301', quantity: 1 },
                    { id: '302', quantity: 1 },
                ],
            },
        });
        await wrapper.findAll('input[type="checkbox"]')[1].setValue(false);

        emissions = wrapper.emitted('update:modelValue');
        expect(emissions?.[2]?.[0]).toEqual({
            buns: '101',
            patties: { id: '201', quantity: 1 },
            toppings: [{ id: '301', quantity: 1 }],
        });
    });
});

describe('FriesOptionsComp', () => {
    it('renders selected summaries and emits single-selection updates', async () => {
        const wrapper = mount(FriesOptionsComp, {
            props: {
                modelValue: {
                    sizes: '401',
                    types: '501',
                    seasonings: '601',
                },
                optionGroups: [
                    {
                        items: [
                            { id: '401', name: 'Regular', price: 0, quantity: 1 },
                            { id: '402', name: 'Large', price: 1.5, quantity: 0 },
                        ],
                        key: 'sizes',
                        label: 'Size',
                        selectionMode: 'single',
                    },
                    {
                        items: [
                            { id: '501', name: 'Shoestring', price: 0, quantity: 1 },
                            { id: '502', name: 'Waffle', price: 0.5, quantity: 1 },
                        ],
                        key: 'types',
                        label: 'Type',
                        selectionMode: 'single',
                    },
                    {
                        items: [
                            { id: '601', name: 'Salt', price: 0, quantity: 1 },
                            { id: '602', name: 'Garlic', price: 0.5, quantity: 1 },
                        ],
                        key: 'seasonings',
                        label: 'Seasoning',
                        selectionMode: 'single',
                    },
                ],
            },
        });

        const sizeOptions = wrapper.get('#sizes-input').findAll('option');
        expect(sizeOptions[0].text()).toBe('Regular · Included');
        expect(sizeOptions[1].text()).toBe('Large · +$1.50');
        expect(sizeOptions[1].attributes('disabled')).toBeDefined();
        expect(wrapper.text()).toContain('Selected: Regular');
        expect(wrapper.text()).toContain('Selected: Shoestring');

        await wrapper.get('#types-input').setValue('502');

        const emissions = wrapper.emitted('update:modelValue');
        expect(emissions?.[0]?.[0]).toEqual({
            sizes: '401',
            types: '502',
            seasonings: '601',
        });
    });
});