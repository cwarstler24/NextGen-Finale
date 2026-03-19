import {
    supportedBurgerBuns,
    supportedBurgerPatties,
    supportedBurgerToppings,
} from './burgerImageCatalog';
import customBurger from './customBurgers.js';

const CLASSIC_CHEESEBURGER_ID = 18;

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

const classicCheeseburger = customBurger.find((burger) => burger.id === CLASSIC_CHEESEBURGER_ID);

if (!classicCheeseburger) {
    throw new Error(`Classic Cheeseburger preset (id ${CLASSIC_CHEESEBURGER_ID}) is required for burger image fallbacks.`);
}

export const classicCheeseburgerImageProps = toBurgerImageProps(classicCheeseburger);
