<script setup>
const props = defineProps({
    modelValue: {
        type: Array,
        default: () => [],
    },
    productOptions: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits(['update:modelValue']);

function updateOption(index, value) {
    const nextValue = [...props.modelValue];
    nextValue[index] = value;
    emit('update:modelValue', nextValue);
}

function getOption3Selections() {
    const selections = props.modelValue[2];
    if (Array.isArray(selections)) {
        return selections;
    }

    return selections ? [selections] : [];
}

function toggleOption3(value, checked) {
    const nextValue = [...props.modelValue];
    const selections = getOption3Selections();

    nextValue[2] = checked
        ? [...selections, value]
        : selections.filter((selection) => selection !== value);

    emit('update:modelValue', nextValue);
}
</script>


<template>
<h3>Customize your order</h3>
<div name="options" class="option-grid">
    <label>{{ productOptions.optionNames[0] }}</label>
    <select :value="props.modelValue[0]" @change="updateOption(0, $event.target.value)">
        <option v-for="(opt, optIdx) in props.productOptions.option1" :key="opt" :value="opt">
            {{ opt }}<span v-if="props.productOptions.option1Price[optIdx] > 0"> ${{
                props.productOptions.option1Price[optIdx].toFixed(2) }}</span>
        </option>
    </select>
    <label>{{ productOptions.optionNames[1] }}</label>
    <select :value="props.modelValue[1]" @change="updateOption(1, $event.target.value)">
        <option v-for="(opt, optIdx) in props.productOptions.option2" :key="opt" :value="opt">
            {{ opt }}<span v-if="props.productOptions.option2Price[optIdx] > 0"> + ${{
                props.productOptions.option2Price[optIdx].toFixed(2) }}</span>
        </option>
    </select>
    <label>{{ productOptions.optionNames[2] }}</label>
    <div class="checkbox-group" name="option3">
        <label v-for="(opt, optIdx) in props.productOptions.option3" :key="opt" class="checkbox-option">
            <input type="checkbox" :checked="getOption3Selections().includes(opt)" @change="toggleOption3(opt, $event.target.checked)" />
            <span>
                {{ opt }}<span v-if="props.productOptions.option3Price[optIdx] > 0"> + ${{
                    props.productOptions.option3Price[optIdx].toFixed(2) }}</span>
            </span>
        </label>
    </div>
</div>
</template>

<style src="../styles/ProductView.css" scoped></style>