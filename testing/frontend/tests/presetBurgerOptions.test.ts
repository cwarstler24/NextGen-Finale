import { describe, expect, it } from 'vitest';

import {
    buildBurgerCartOptions,
    buildBurgerSelectionsFromPreset,
    calculateBurgerSelectionsUnitPrice,
    normalizeBurgerOptionGroups,
} from '../../../main/frontend/src/data/presetBurgerOptions';

function createNormalizedGroups() {
    return normalizeBurgerOptionGroups({
        buns: [
            { id: 101, name: 'Sesame', price: 1, quantity: 0 },
            { id: 102, name: 'Brioche', price: 2, quantity: 5 },
        ],
        patties: [
            { id: 201, name: 'Beef', price: 3, quantity: 5 },
            { id: 202, name: 'Veggie', price: 4, quantity: 0 },
        ],
        toppings: [
            { id: 301, name: 'Lettuce', price: 0.5, quantity: 2 },
            { id: 302, name: 'Tomato', price: 0.25, quantity: 5 },
        ],
    });
}

describe('presetBurgerOptions', () => {
    it('normalizes burger option groups with labels, modes, and string ids', () => {
        const groups = createNormalizedGroups();

        expect(groups.map((group) => group.key)).toEqual(['buns', 'patties', 'toppings']);
        expect(groups.map((group) => group.label)).toEqual(['Bun', 'Patty', 'Toppings']);
        expect(groups.map((group) => group.selectionMode)).toEqual(['single', 'single_quantity', 'multiple']);
        expect(groups[0].items[0].id).toBe('101');
        expect(groups[1].items[0].id).toBe('201');
        expect(groups[2].items[0].id).toBe('301');
    });

    it('builds selections from a preset and reports unavailable/adjusted ingredients', () => {
        const groups = createNormalizedGroups();

        const result = buildBurgerSelectionsFromPreset(groups, {
            bun: 'Sesame',
            patty: 'Chicken',
            toppings: [
                { type: 'Lettuce', qty: 4 },
                { type: 'Onion', qty: 1 },
                { type: 'Tomato', qty: 2 },
                { type: 'Tomato', qty: 2 },
            ],
        });

        expect(result.selections).toEqual({
            buns: '102',
            patties: { id: '201', quantity: 1 },
            toppings: [
                { id: '301', quantity: 2 },
                { id: '302', quantity: 2 },
                { id: '302', quantity: 2 },
            ],
        });
        expect(result.unavailableIngredients).toEqual(['Sesame', 'Chicken', 'Onion']);
        expect(result.unavailableCoreSelections).toEqual(['Sesame', 'Chicken']);
        expect(result.adjustedIngredients).toEqual(['Lettuce x2']);
    });

    it('calculates unit price across single, single_quantity, and multiple groups', () => {
        const groups = createNormalizedGroups();
        const selections = {
            buns: '102',
            patties: { id: 201, quantity: 2 },
            toppings: [
                { id: 301, quantity: 3 },
                { id: 999, quantity: 7 },
                null,
                ['invalid'],
            ],
        };

        const unitPrice = calculateBurgerSelectionsUnitPrice(groups, selections);

        expect(unitPrice).toBe(9.5);
    });

    it('builds cart options and excludes unknown multiple selections', () => {
        const groups = createNormalizedGroups();

        const options = buildBurgerCartOptions(groups, {
            buns: '102',
            patties: { id: '201', quantity: 3 },
            toppings: [
                { id: '302', quantity: 2 },
                { id: '404', quantity: 2 },
            ],
        });

        expect(options).toEqual([
            {
                id: '102',
                name: 'Bun',
                value: 'Brioche',
            },
            {
                id: '201',
                name: 'Patty',
                value: [{ id: '201', name: 'Beef', quantity: 3 }],
            },
            {
                id: [{ id: '302', quantity: 2 }],
                name: 'Toppings',
                value: [{ id: '302', name: 'Tomato', quantity: 2 }],
            },
        ]);
    });

    it('returns null-valued cart options when selections cannot map to items', () => {
        const groups = createNormalizedGroups();

        const options = buildBurgerCartOptions(groups, {
            buns: null,
            patties: ['invalid-shape'],
            toppings: 'not-an-array',
        });

        expect(options).toEqual([
            {
                id: null,
                name: 'Bun',
                value: null,
            },
            {
                id: null,
                name: 'Patty',
                value: null,
            },
            {
                id: [],
                name: 'Toppings',
                value: [],
            },
        ]);
    });
});
