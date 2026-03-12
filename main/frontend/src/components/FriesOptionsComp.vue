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
    return Array.isArray(selections) ? selections : [];
}

function toggleMultiSelection(groupKey, value, checked) {
    const currentSelections = getMultiSelections(groupKey);
    const nextSelections = checked
        ? [...new Set([...currentSelections, value])]
        : currentSelections.filter((selection) => selection !== value);

    emit('update:modelValue', {
        ...props.modelValue,
        [groupKey]: nextSelections,
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
            <label
                v-for="item in group.items"
                :key="item.id"
                class="checkbox-option"
            >
                <input
                    type="checkbox"
                    :value="item.id"
                    :checked="getMultiSelections(group.key).includes(item.id)"
                    :disabled="item.quantity <= 0"
                    @change="toggleMultiSelection(group.key, item.id, $event.target.checked)"
                />
                <span>{{ item.name }}{{ formatPrice(item.price) }}</span>
            </label>
        </div>
    </template>
</div>
</template>

<style src="../styles/ProductView.css" scoped></style>
