import {
    supportedBurgerBuns,
    supportedBurgerPatties,
    supportedBurgerToppings,
} from './burgerImageCatalog';

function normalizeQuantity(value) {
    return Math.max(1, Number.parseInt(value ?? 1, 10) || 1);
}

export function toBurgerImageProps(burger) {
    const bunName = supportedBurgerBuns.has(burger?.bun) ? burger.bun : 'None';
    const pattyName = supportedBurgerPatties.has(burger?.patty) ? burger.patty : 'None';

    return {
        selectedBun: { name: bunName },
        selectedPatty: {
            name: pattyName,
            quantity: 1,
        },
        selectedToppings: Array.isArray(burger?.toppings)
            ? burger.toppings
                .filter((topping) => supportedBurgerToppings.has(topping?.type))
                .map((topping) => ({
                    name: topping.type,
                    quantity: normalizeQuantity(topping.qty),
                }))
            : [],
    };
}
