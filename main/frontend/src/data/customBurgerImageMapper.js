const SUPPORTED_BUNS = new Set(['Whole Wheat', 'Sesame', 'Brioche', 'None']);
const SUPPORTED_PATTIES = new Set(['Beef', 'Chicken', 'Veggie', 'None']);
const SUPPORTED_TOPPINGS = new Set([
    'Lettuce',
    'Tomato',
    'Onion',
    'Pickles',
    'Cheese',
    'Bacon',
    'Jalapenos',
    'Mushrooms',
    'Ketchup',
    'Mustard',
    'Mayonnaise',
    'Avocado',
    'None',
]);

function normalizeQuantity(value) {
    return Math.max(1, Number.parseInt(value ?? 1, 10) || 1);
}

export function toBurgerImageProps(burger) {
    const bunName = SUPPORTED_BUNS.has(burger?.bun) ? burger.bun : 'None';
    const pattyName = SUPPORTED_PATTIES.has(burger?.patty) ? burger.patty : 'None';

    return {
        selectedBun: { name: bunName },
        selectedPatty: {
            name: pattyName,
            quantity: 1,
        },
        selectedToppings: Array.isArray(burger?.toppings)
            ? burger.toppings
                .filter((topping) => SUPPORTED_TOPPINGS.has(topping?.type))
                .map((topping) => ({
                    name: topping.type,
                    quantity: normalizeQuantity(topping.qty),
                }))
            : [],
    };
}
