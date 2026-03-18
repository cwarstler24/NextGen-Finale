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
    background: #ffffff;
}

.fries-options-header {
    display: grid;
    gap: 0.35rem;
}

.fries-options-header h3 {
    margin: 0;
    color: #0f172a;
}

.fries-options-header p {
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

.selection-summary {
    display: flex;
    justify-content: space-between;
    gap: 0.75rem;
    align-items: center;
    margin: 0;
    padding: 0.85rem 0.95rem;
    border-radius: 14px;
    background: #f8fafc;
    color: #475569;
}

.selection-summary strong {
    color: #0f172a;
}

.selection-price {
    color: #64748b;
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
