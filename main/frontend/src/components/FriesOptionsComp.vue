<script setup>
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

function updateSingleSelection(groupKey, value) {
    emit('update:modelValue', {
        ...props.modelValue,
        [groupKey]: value,
    });
}

function formatPrice(price) {
    return price > 0 ? `+$${price.toFixed(2)}` : 'Included';
}

function getSelectedItem(group) {
    return group.items.find((item) => item.id === props.modelValue[group.key]) ?? null;
}
</script>

<template>
<section class="fries-options-panel" aria-label="Fries customization options">
    <div class="fries-options-header">
        <h3>Customize your order</h3>
        <p>Pick one option from each section to build your perfect fries.</p>
    </div>

    <div name="options" class="option-grid">
        <div
            v-for="group in optionGroups"
            :key="group.key"
            class="option-section"
        >
            <div class="option-heading-row">
                <label class="option-label" :for="`${group.key}-input`">{{ group.label }}</label>
                <span class="option-helper">{{ getSelectedItem(group)?.name ?? 'Choose one' }}</span>
            </div>

            <select
                :id="`${group.key}-input`"
                class="option-select"
                :value="modelValue[group.key] ?? ''"
                @change="updateSingleSelection(group.key, $event.target.value)"
            >
                <option
                    v-for="item in group.items"
                    :key="item.id"
                    :value="item.id"
                    :disabled="item.quantity <= 0"
                >
                    {{ item.name }} · {{ formatPrice(item.price) }}
                </option>
            </select>

            <p
                v-if="getSelectedItem(group)"
                class="selection-summary"
            >
                Selected: <strong>{{ getSelectedItem(group)?.name }}</strong>
                <span class="selection-price">{{ formatPrice(getSelectedItem(group)?.price ?? 0) }}</span>
            </p>
        </div>
    </div>
</section>
</template>

<style src="../styles/ProductView.css" scoped></style>

<style scoped>
.fries-options-panel {
    display: grid;
    gap: 1.25rem;
    padding: 1.25rem;
    border-radius: 20px;
    background: linear-gradient(180deg, rgba(255, 252, 247, 0.92) 0%, rgba(248, 235, 220, 0.76) 100%);
}

.fries-options-header {
    display: grid;
    gap: 0.35rem;
}

.fries-options-header h3 {
    margin: 0;
    color: var(--color-heading);
}

.fries-options-header p {
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

.selection-summary {
    display: flex;
    justify-content: space-between;
    gap: 0.75rem;
    align-items: center;
    margin: 0;
    padding: 0.85rem 0.95rem;
    border-radius: 14px;
    background: rgba(244, 231, 215, 0.66);
    color: var(--color-text-soft);
}

.selection-summary strong {
    color: var(--color-heading);
}

.selection-price {
    color: var(--color-text-soft);
    font-size: 0.9rem;
    white-space: nowrap;
}

@media (max-width: 640px) {
    .selection-summary {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>
