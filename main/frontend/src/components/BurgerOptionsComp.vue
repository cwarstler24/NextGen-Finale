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
        ? [...currentSelections, { id: value, quantity: 1 }]
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
                quantity: Math.max(1, Number.parseInt(nextQuantity, 10) || 1),
            };
        }),
    });
}

function formatPrice(price) {
    return price > 0 ? ` + $${price.toFixed(2)}` : '';
}
</script>

<template>
<h3>Customize your order</h3>
<div name="options" class="option-grid">
    <template v-for="group in optionGroups" :key="group.key">
        <label :for="`${group.key}-input`">{{ group.label }}</label>

        <select
            v-if="group.selectionMode === 'single'"
            :id="`${group.key}-input`"
            :value="modelValue[group.key] ?? ''"
            @change="updateSingleSelection(group.key, $event.target.value)"
        >
            <option
                v-for="item in group.items"
                :key="item.id"
                :value="item.id"
                :disabled="item.quantity <= 0"
            >
                {{ item.name }}{{ formatPrice(item.price) }}
            </option>
        </select>

        <div v-else class="checkbox-group" :name="group.key">
            <div
                v-for="item in group.items"
                :key="item.id"
                class="checkbox-option-row"
            >
                <label class="checkbox-option">
                    <input
                        type="checkbox"
                        :value="item.id"
                        :checked="isMultiSelected(group.key, item.id)"
                        :disabled="item.quantity <= 0"
                        @change="toggleMultiSelection(group.key, item.id, $event.target.checked)"
                    />
                    <span>{{ item.name }}{{ formatPrice(item.price) }}</span>
                </label>
                <input
                    class="option-quantity-input"
                    type="number"
                    min="1"
                    :max="item.quantity"
                    :value="getMultiQuantity(group.key, item.id)"
                    :disabled="!isMultiSelected(group.key, item.id) || item.quantity <= 0"
                    @input="updateMultiQuantity(group.key, item.id, $event.target.value)"
                />
            </div>
        </div>
    </template>
</div>
</template>

<style src="../styles/ProductView.css" scoped></style>
