<script setup>
import { computed } from 'vue';

const props = defineProps({
    modelValue: {
        type: Object,
        default: () => ({}),
    },
    optionGroups: {
        type: Array,
        required: true,
    },
});

const emit = defineEmits(['update:modelValue']);

const bunGroup = computed(() => props.optionGroups.find((group) => group.key === 'buns') ?? null);
const pattyGroup = computed(() => props.optionGroups.find((group) => group.key === 'patties') ?? null);
const toppingsGroup = computed(() => props.optionGroups.find((group) => group.key === 'toppings') ?? null);

function clampQuantity(quantity, maxQuantity) {
    return Math.min(maxQuantity, Math.max(1, Number.parseInt(quantity, 10) || 1));
}

function normalizeOptionId(value) {
    if (value === null || value === undefined || value === '') {
        return null;
    }

    return String(value);
}

function getGroupItem(groupKey, itemId) {
    const normalizedItemId = normalizeOptionId(itemId);
    if (normalizedItemId === null) {
        return null;
    }

    const group = props.optionGroups.find((entry) => entry.key === groupKey);
    return group?.items.find((item) => normalizeOptionId(item.id) === normalizedItemId) ?? null;
}

function getMaxQuantity(groupKey, itemId) {
    return Math.max(1, Number.parseInt(getGroupItem(groupKey, itemId)?.quantity ?? 1, 10) || 1);
}

function updateSingleSelection(groupKey, value) {
    emit('update:modelValue', {
        ...props.modelValue,
        [groupKey]: normalizeOptionId(value),
    });
}

function getSingleQuantitySelection(groupKey) {
    const selection = props.modelValue[groupKey];
    if (!selection || typeof selection !== 'object' || Array.isArray(selection)) {
        return null;
    }

    return {
        id: String(selection.id ?? ''),
        quantity: Math.max(1, Number.parseInt(selection.quantity ?? 1, 10) || 1),
    };
}

function updateSingleQuantitySelection(groupKey, value) {
    const normalizedValue = normalizeOptionId(value);
    const selectedItem = getGroupItem(groupKey, normalizedValue);
    if (!selectedItem) {
        return;
    }

    const currentSelection = getSingleQuantitySelection(groupKey);
    const maxQuantity = getMaxQuantity(groupKey, normalizedValue);

    emit('update:modelValue', {
        ...props.modelValue,
        [groupKey]: {
            id: normalizedValue,
            quantity: Math.min(currentSelection?.quantity ?? 1, maxQuantity),
        },
    });
}

function updateSingleQuantity(groupKey, nextQuantity) {
    const currentSelection = getSingleQuantitySelection(groupKey);
    if (!currentSelection) {
        return;
    }

    emit('update:modelValue', {
        ...props.modelValue,
        [groupKey]: {
            ...currentSelection,
            quantity: clampQuantity(nextQuantity, getMaxQuantity(groupKey, currentSelection.id)),
        },
    });
}

function stepSingleQuantity(groupKey, delta) {
    const currentSelection = getSingleQuantitySelection(groupKey);
    if (!currentSelection) {
        return;
    }

    updateSingleQuantity(groupKey, currentSelection.quantity + delta);
}

function getMultiSelections(groupKey) {
    const selections = props.modelValue[groupKey];
    if (!Array.isArray(selections)) {
        return [];
    }

    return selections
        .filter((selection) => selection && typeof selection === 'object' && !Array.isArray(selection))
        .map((selection) => ({
            id: String(selection.id),
            quantity: Math.max(1, Number.parseInt(selection.quantity ?? 1, 10) || 1),
        }));
}

function isMultiSelected(groupKey, value) {
    const normalizedValue = normalizeOptionId(value);
    return normalizedValue !== null && getMultiSelections(groupKey)
        .some((selection) => selection.id === normalizedValue);
}

function getMultiQuantity(groupKey, value) {
    const normalizedValue = normalizeOptionId(value);
    if (normalizedValue === null) {
        return 1;
    }

    return getMultiSelections(groupKey).find((selection) => selection.id === normalizedValue)?.quantity ?? 1;
}

function toggleMultiSelection(groupKey, value, checked) {
    const normalizedValue = normalizeOptionId(value);
    if (normalizedValue === null) {
        return;
    }

    const currentSelections = getMultiSelections(groupKey);
    const nextSelections = checked
        ? currentSelections.some((selection) => selection.id === normalizedValue)
            ? currentSelections
            : [...currentSelections, { id: normalizedValue, quantity: 1 }]
        : currentSelections.filter((selection) => selection.id !== normalizedValue);

    emit('update:modelValue', {
        ...props.modelValue,
        [groupKey]: nextSelections,
    });
}

function updateMultiQuantity(groupKey, value, nextQuantity) {
    const normalizedValue = normalizeOptionId(value);
    if (normalizedValue === null) {
        return;
    }

    emit('update:modelValue', {
        ...props.modelValue,
        [groupKey]: getMultiSelections(groupKey).map((selection) => {
            if (selection.id !== normalizedValue) {
                return selection;
            }

            return {
                ...selection,
                quantity: clampQuantity(nextQuantity, getMaxQuantity(groupKey, normalizedValue)),
            };
        }),
    });
}

function stepMultiQuantity(groupKey, value, delta) {
    updateMultiQuantity(groupKey, value, getMultiQuantity(groupKey, value) + delta);
}

function formatPrice(price) {
    const normalizedPrice = Number(price);
    return normalizedPrice > 0 ? `+$${normalizedPrice.toFixed(2)}` : 'Included';
}
</script>

<template>
<section class="burger-options-panel" aria-label="Burger customization options">
    <div class="burger-options-header">
        <h3>Customize your order</h3>
        <p>Choose your bun, stack your patties, and add toppings your way.</p>
    </div>

    <div name="options" class="option-grid">
        <div v-if="bunGroup" class="option-section">
            <label class="option-label" for="buns-input">{{ bunGroup.label }}</label>
            <select
                id="buns-input"
                class="option-select"
                :value="modelValue.buns ?? ''"
                @change="updateSingleSelection('buns', $event.target.value)"
            >
                <option
                    v-for="item in bunGroup.items"
                    :key="item.id"
                    :value="item.id"
                    :disabled="item.quantity <= 0"
                >
                    {{ item.name }} · {{ formatPrice(item.price) }}
                </option>
            </select>
        </div>

        <div v-if="pattyGroup" class="option-section">
            <div class="option-heading-row">
                <label class="option-label" for="patties-input">{{ pattyGroup.label }}</label>
            </div>
            <div class="selection-card">
                <select
                    id="patties-input"
                    class="option-select"
                    :value="getSingleQuantitySelection('patties')?.id ?? ''"
                    @change="updateSingleQuantitySelection('patties', $event.target.value)"
                >
                    <option
                        v-for="item in pattyGroup.items"
                        :key="item.id"
                        :value="item.id"
                        :disabled="item.quantity <= 0"
                    >
                        {{ item.name }} · {{ formatPrice(item.price) }}
                    </option>
                </select>
                <div
                    v-if="getSingleQuantitySelection('patties')"
                    class="quantity-stepper"
                    aria-label="Patty quantity"
                >
                    <button
                        type="button"
                        class="stepper-button"
                        :disabled="getSingleQuantitySelection('patties')?.quantity <= 1"
                        aria-label="Decrease patty quantity"
                        @click="stepSingleQuantity('patties', -1)"
                    >
                        -
                    </button>
                    <span class="quantity-pill">{{ getSingleQuantitySelection('patties')?.quantity }}</span>
                    <button
                        type="button"
                        class="stepper-button"
                        :disabled="getSingleQuantitySelection('patties')?.quantity >= getMaxQuantity('patties', getSingleQuantitySelection('patties')?.id)"
                        aria-label="Increase patty quantity"
                        @click="stepSingleQuantity('patties', 1)"
                    >
                        +
                    </button>
                </div>
            </div>
        </div>

        <div v-if="toppingsGroup" class="option-section">
            <div class="option-heading-row">
                <label class="option-label">{{ toppingsGroup.label }}</label>
            </div>
            <div class="checkbox-group" name="toppings">
                <div
                    v-for="item in toppingsGroup.items"
                    :key="item.id"
                    class="checkbox-option-row"
                    :class="{ 'is-selected': isMultiSelected('toppings', item.id), 'is-disabled': item.quantity <= 0 }"
                >
                    <label class="checkbox-option">
                        <input
                            type="checkbox"
                            :value="item.id"
                            :checked="isMultiSelected('toppings', item.id)"
                            :disabled="item.quantity <= 0"
                            @change="toggleMultiSelection('toppings', item.id, $event.target.checked)"
                        />
                        <span class="option-copy">
                            <span class="option-name">{{ item.name }}</span>
                            <span class="option-price">{{ formatPrice(item.price) }}</span>
                        </span>
                    </label>
                    <div
                        v-if="isMultiSelected('toppings', item.id) && item.quantity > 0"
                        class="quantity-stepper"
                        :aria-label="`${item.name} quantity`"
                    >
                        <button
                            type="button"
                            class="stepper-button"
                            :disabled="getMultiQuantity('toppings', item.id) <= 1"
                            :aria-label="`Decrease ${item.name} quantity`"
                            @click="stepMultiQuantity('toppings', item.id, -1)"
                        >
                            -
                        </button>
                        <span class="quantity-pill">{{ getMultiQuantity('toppings', item.id) }}</span>
                        <button
                            type="button"
                            class="stepper-button"
                            :disabled="getMultiQuantity('toppings', item.id) >= getMaxQuantity('toppings', item.id)"
                            :aria-label="`Increase ${item.name} quantity`"
                            @click="stepMultiQuantity('toppings', item.id, 1)"
                        >
                            +
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
</template>

<style src="../styles/ProductView.css" scoped></style>

<style scoped>
.burger-options-panel {
    display: grid;
    gap: 1.25rem;
    padding: 1.25rem;
    border-radius: 20px;
    background: linear-gradient(180deg, rgba(255, 252, 247, 0.92) 0%, rgba(248, 235, 220, 0.76) 100%);
}

.burger-options-header {
    display: grid;
    gap: 0.35rem;
}

.burger-options-header h3 {
    margin: 0;
    color: var(--color-heading);
}

.burger-options-header p {
    margin: 0;
    color: var(--color-text-soft);
    font-size: 0.95rem;
}

.option-grid {
    display: grid;
    gap: 1rem;
}

.option-section {
    display: grid;
    gap: 0.75rem;
    padding: 1rem 0;
    border-bottom: 1px solid rgba(113, 88, 71, 0.12);
}

.option-section:last-child {
    padding-bottom: 0;
    border-bottom: none;
}

.option-heading-row {
    display: flex;
    justify-content: space-between;
    gap: 0.75rem;
    align-items: baseline;
    flex-wrap: wrap;
}

.option-label {
    display: block;
    font-weight: 700;
    color: var(--color-heading);
}

.option-helper {
    color: var(--color-text-soft);
    font-size: 0.85rem;
}

.option-select {
    width: 100%;
    min-height: 44px;
    padding: 0.8rem 0.95rem;
    border-radius: 12px;
    border: 1px solid var(--color-border);
    background: rgba(255, 251, 245, 0.92);
    font: inherit;
    color: var(--color-heading);
    box-sizing: border-box;
}

.selection-card {
    display: flex;
    gap: 0.85rem;
    align-items: center;
    flex-wrap: wrap;
}

.checkbox-group {
    display: grid;
    gap: 0.75rem;
}

.checkbox-option-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 0.95rem;
    border: 1px solid rgba(113, 88, 71, 0.12);
    border-radius: 14px;
    background: rgba(255, 251, 245, 0.82);
    transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.checkbox-option-row.is-selected {
    border-color: rgba(201, 105, 44, 0.28);
    background: linear-gradient(180deg, rgba(255, 245, 233, 0.96) 0%, rgba(255, 250, 244, 0.9) 100%);
    box-shadow: 0 12px 24px rgba(169, 79, 31, 0.1);
}

.checkbox-option-row.is-disabled {
    opacity: 0.65;
}

.checkbox-option {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    flex: 1;
    min-width: 0;
}

.checkbox-option input {
    width: 1rem;
    height: 1rem;
    margin: 0;
    accent-color: var(--color-accent);
}

.option-copy {
    display: grid;
    gap: 0.15rem;
}

.option-name {
    font-weight: 600;
    color: var(--color-heading);
}

.option-price {
    color: var(--color-text-soft);
    font-size: 0.9rem;
}

.quantity-stepper {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.3rem;
    border-radius: 999px;
    border: 1px solid var(--color-border);
    background: rgba(255, 251, 245, 0.92);
    box-shadow: inset 0 1px 2px rgba(58, 31, 17, 0.05);
}

.stepper-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    border: none;
    border-radius: 999px;
    background: rgba(244, 231, 215, 0.9);
    color: var(--color-heading);
    font: inherit;
    font-size: 1.05rem;
    font-weight: 700;
    line-height: 1;
    padding: 0;
    cursor: pointer;
}

.stepper-button:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}

.quantity-pill {
    min-width: 2rem;
    text-align: center;
    font-weight: 700;
    color: var(--color-heading);
}

@media (max-width: 640px) {
    .checkbox-option-row,
    .selection-card {
        align-items: stretch;
        flex-direction: column;
    }

    .quantity-stepper {
        align-self: flex-end;
    }
}
</style>
