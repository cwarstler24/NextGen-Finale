import { describe, expect, it } from 'vitest';

import { toBurgerImageProps } from '../../../main/frontend/src/data/customBurgerImageMapper';

describe('customBurgerImageMapper', () => {
    it('maps supported burger values into BurgerImage props', () => {
        const result = toBurgerImageProps({
            bun: 'Sesame',
            patty: 'Beef',
            toppings: [
                { type: 'Lettuce', qty: 2 },
                { type: 'Tomato', qty: '3' },
            ],
        });

        expect(result).toEqual({
            selectedBun: { name: 'Sesame' },
            selectedPatty: { name: 'Beef', quantity: 1 },
            selectedToppings: [
                { name: 'Lettuce', quantity: 2 },
                { name: 'Tomato', quantity: 3 },
            ],
        });
    });

    it('keeps catalog-supported values and filters unsupported toppings', () => {
        const result = toBurgerImageProps({
            bun: 'Pretzel',
            patty: 'Fish',
            toppings: [
                { type: 'Lettuce', qty: 0 },
                { type: 'Blue Cheese', qty: 2 },
                { type: 'None', qty: -10 },
            ],
        });

        expect(result.selectedBun).toEqual({ name: 'Pretzel' });
        expect(result.selectedPatty).toEqual({ name: 'Fish', quantity: 1 });
        expect(result.selectedToppings).toEqual([
            { name: 'Lettuce', quantity: 1 },
            { name: 'Blue Cheese', quantity: 2 },
            { name: 'None', quantity: 1 },
        ]);
    });

    it('handles missing burger input safely', () => {
        expect(toBurgerImageProps(undefined)).toEqual({
            selectedBun: { name: 'None' },
            selectedPatty: { name: 'None', quantity: 1 },
            selectedToppings: [],
        });
    });
});
