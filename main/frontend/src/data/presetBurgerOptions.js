function isMultipleSelectionGroup(group) {
    return group.selectionMode === 'multiple';
}

function isSingleQuantitySelectionGroup(group) {
    return group.selectionMode === 'single_quantity';
}

function getDefaultSelection(group) {
    if (isMultipleSelectionGroup(group)) {
        return [];
    }

    const defaultItem = group.items.find((item) => item.quantity > 0) ?? group.items[0];
    if (!defaultItem) {
        return null;
    }

    if (isSingleQuantitySelectionGroup(group)) {
        return {
            id: defaultItem.id,
            quantity: 1,
        };
    }

    return defaultItem.id;
}

function getDefaultSelections(groups) {
    return groups.reduce((nextSelections, group) => {
        nextSelections[group.key] = getDefaultSelection(group);
        return nextSelections;
    }, {});
}

function getMultiSelections(selection) {
    if (!Array.isArray(selection)) {
        return [];
    }

    return selection
        .filter((entry) => entry && typeof entry === 'object' && !Array.isArray(entry))
        .map((entry) => ({
            id: String(entry.id),
            quantity: Math.max(1, Number.parseInt(entry.quantity ?? 1, 10) || 1),
        }))
        .sort((left, right) => left.id.localeCompare(right.id));
}

function getSingleQuantitySelection(selection) {
    if (!selection || typeof selection !== 'object' || Array.isArray(selection)) {
        return null;
    }

    return {
        id: String(selection.id ?? ''),
        quantity: Math.max(1, Number.parseInt(selection.quantity ?? 1, 10) || 1),
    };
}

function normalizeOptionName(value) {
    return String(value ?? '').trim().toLowerCase();
}

function findGroupItem(group, selectionId) {
    const normalizedSelectionId = selectionId === null || selectionId === undefined
        ? null
        : String(selectionId);

    if (!group || normalizedSelectionId === null) {
        return null;
    }

    return group.items.find((item) => item.id === normalizedSelectionId) ?? null;
}

function findAvailableGroupItemByName(group, itemName) {
    const normalizedItemName = normalizeOptionName(itemName);
    if (!group || normalizedItemName === '') {
        return null;
    }

    return group.items.find((item) => (
        normalizeOptionName(item.name) === normalizedItemName
        && Number.parseInt(item.quantity ?? 0, 10) > 0
    )) ?? null;
}

function getOptionItemPrice(item) {
    const price = Number(item?.price);
    return Number.isFinite(price) ? price : 0;
}

export function normalizeBurgerOptionGroups(optionsByGroup) {
    return Object.entries(optionsByGroup).map(([key, items]) => ({
        key,
        label: key === 'buns' ? 'Bun' : key === 'patties' ? 'Patty' : 'Toppings',
        selectionMode: key === 'toppings' ? 'multiple' : key === 'patties' ? 'single_quantity' : 'single',
        items: items.map((item) => ({
            ...item,
            id: String(item.id),
        })),
    }));
}

export function buildBurgerSelectionsFromPreset(groups, presetBurger) {
    const nextSelections = getDefaultSelections(groups);
    const unavailableIngredients = [];
    const unavailableCoreSelections = [];
    const adjustedIngredients = [];

    const bunGroup = groups.find((group) => group.key === 'buns');
    const pattyGroup = groups.find((group) => group.key === 'patties');
    const toppingsGroup = groups.find((group) => group.key === 'toppings');

    const bunItem = findAvailableGroupItemByName(bunGroup, presetBurger.bun);
    if (bunItem) {
        nextSelections.buns = bunItem.id;
    } else if (presetBurger.bun) {
        unavailableIngredients.push(presetBurger.bun);
        unavailableCoreSelections.push(presetBurger.bun);
    }

    const pattyItem = findAvailableGroupItemByName(pattyGroup, presetBurger.patty);
    if (pattyItem) {
        nextSelections.patties = {
            id: pattyItem.id,
            quantity: 1,
        };
    } else if (presetBurger.patty) {
        unavailableIngredients.push(presetBurger.patty);
        unavailableCoreSelections.push(presetBurger.patty);
    }

    nextSelections.toppings = [];
    for (const topping of presetBurger.toppings ?? []) {
        const toppingItem = findAvailableGroupItemByName(toppingsGroup, topping.type);
        if (!toppingItem) {
            unavailableIngredients.push(topping.type);
            continue;
        }

        const requestedQuantity = Math.max(1, Number.parseInt(topping.qty ?? 1, 10) || 1);
        const availableQuantity = Math.max(1, Number.parseInt(toppingItem.quantity ?? 1, 10) || 1);
        const appliedQuantity = Math.min(requestedQuantity, availableQuantity);

        nextSelections.toppings.push({
            id: toppingItem.id,
            quantity: appliedQuantity,
        });

        if (appliedQuantity < requestedQuantity) {
            adjustedIngredients.push(`${toppingItem.name} x${appliedQuantity}`);
        }
    }

    return {
        selections: nextSelections,
        unavailableIngredients: [...new Set(unavailableIngredients)],
        unavailableCoreSelections: [...new Set(unavailableCoreSelections)],
        adjustedIngredients,
    };
}

export function calculateBurgerSelectionsUnitPrice(groups, selections) {
    return groups.reduce((runningTotal, group) => {
        if (isMultipleSelectionGroup(group)) {
            return runningTotal + getMultiSelections(selections[group.key]).reduce((groupTotal, selection) => {
                const selectedItem = findGroupItem(group, selection.id);
                return groupTotal + (getOptionItemPrice(selectedItem) * selection.quantity);
            }, 0);
        }

        if (isSingleQuantitySelectionGroup(group)) {
            const selection = getSingleQuantitySelection(selections[group.key]);
            const selectedItem = findGroupItem(group, selection?.id);
            return runningTotal + (getOptionItemPrice(selectedItem) * (selection?.quantity ?? 1));
        }

        const selectedItem = findGroupItem(group, selections[group.key]);
        return runningTotal + getOptionItemPrice(selectedItem);
    }, 0);
}

export function buildBurgerCartOptions(groups, selections) {
    return groups.map((group) => {
        if (isMultipleSelectionGroup(group)) {
            const selectedItemsById = new Map(group.items.map((item) => [item.id, item]));
            const structuredSelections = getMultiSelections(selections[group.key])
                .map((selection) => {
                    const selectedItem = selectedItemsById.get(selection.id);
                    if (!selectedItem) {
                        return null;
                    }

                    return {
                        id: selectedItem.id,
                        name: selectedItem.name,
                        quantity: selection.quantity,
                    };
                })
                .filter(Boolean);

            return {
                id: structuredSelections.map((selection) => ({
                    id: selection.id,
                    quantity: selection.quantity,
                })),
                name: group.label,
                value: structuredSelections.map((selection) => ({
                    id: selection.id,
                    name: selection.name,
                    quantity: selection.quantity,
                })),
            };
        }

        if (isSingleQuantitySelectionGroup(group)) {
            const selection = getSingleQuantitySelection(selections[group.key]);
            const selectedItem = findGroupItem(group, selection?.id);

            return {
                id: selectedItem?.id ?? null,
                name: group.label,
                value: selectedItem
                    ? [{
                        id: selectedItem.id,
                        name: selectedItem.name,
                        quantity: selection?.quantity ?? 1,
                    }]
                    : null,
            };
        }

        const selectedItem = findGroupItem(group, selections[group.key]);

        return {
            id: selectedItem?.id ?? null,
            name: group.label,
            value: selectedItem?.name ?? null,
        };
    });
}
