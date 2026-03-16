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

function getGroupItem(groupKey, itemId) {
    const group = props.optionGroups.find((entry) => entry.key === groupKey);
    return group?.items.find((item) => item.id === itemId) ?? null;
}

function getMaxQuantity(groupKey, itemId) {
    return Math.max(1, Number.parseInt(getGroupItem(groupKey, itemId)?.quantity ?? 1, 10) || 1);
}

function updateSingleSelection(groupKey, value) {
    emit('update:modelValue', {
        ...props.modelValue,
        [groupKey]: value,
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
    const selectedItem = getGroupItem(groupKey, value);
    if (!selectedItem) {
        return;
    }

    const currentSelection = getSingleQuantitySelection(groupKey);
    const maxQuantity = getMaxQuantity(groupKey, value);

    emit('update:modelValue', {
        ...props.modelValue,
        [groupKey]: {
            id: value,
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
    return getMultiSelections(groupKey).some((selection) => selection.id === value);
}

function getMultiQuantity(groupKey, value) {
    return getMultiSelections(groupKey).find((selection) => selection.id === value)?.quantity ?? 1;
}

function toggleMultiSelection(groupKey, value, checked) {
    const currentSelections = getMultiSelections(groupKey);
    const nextSelections = checked
        ? currentSelections.some((selection) => selection.id === value)
            ? currentSelections
            : [...currentSelections, { id: value, quantity: 1 }]
        : currentSelections.filter((selection) => selection.id !== value);

    emit('update:modelValue', {
        ...props.modelValue,
        [groupKey]: nextSelections,
    });
}

function updateMultiQuantity(groupKey, value, nextQuantity) {
    emit('update:modelValue', {
        ...props.modelValue,
        [groupKey]: getMultiSelections(groupKey).map((selection) => {
            if (selection.id !== value) {
                return selection;
            }

            return {
                ...selection,
                quantity: clampQuantity(nextQuantity, getMaxQuantity(groupKey, value)),
            };
        }),
    });
}

function stepMultiQuantity(groupKey, value, delta) {
    updateMultiQuantity(groupKey, value, getMultiQuantity(groupKey, value) + delta);
}

function formatPrice(price) {
    return price > 0 ? `+$${price.toFixed(2)}` : 'Included';
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
    background: #ffffff;
}

.burger-options-header {
    display: grid;
    gap: 0.35rem;
}

.burger-options-header h3 {
    margin: 0;
    color: #0f172a;
}

.burger-options-header p {
    margin: 0;
    color: #64748b;
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
    border-bottom: 1px solid #e2e8f0;
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
    color: #0f172a;
}

.option-helper {
    color: #64748b;
    font-size: 0.85rem;
}

.option-select {
    width: 100%;
    min-height: 44px;
    padding: 0.8rem 0.95rem;
    border-radius: 12px;
    border: 1px solid #cbd5e1;
    background: #ffffff;
    font: inherit;
    color: #0f172a;
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
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    background: #ffffff;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.checkbox-option-row.is-selected {
    border-color: #38bdf8;
    background: #f0f9ff;
    box-shadow: 0 10px 25px rgba(56, 189, 248, 0.12);
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
    accent-color: #0ea5e9;
}

.option-copy {
    display: grid;
    gap: 0.15rem;
}

.option-name {
    font-weight: 600;
    color: #0f172a;
}

.option-price {
    color: #64748b;
    font-size: 0.9rem;
}

.quantity-stepper {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.3rem;
    border-radius: 999px;
    border: 1px solid #cbd5e1;
    background: #ffffff;
    box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.04);
}

.stepper-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    border: none;
    border-radius: 999px;
    background: #e2e8f0;
    color: #0f172a;
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
    color: #0f172a;
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
