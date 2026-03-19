<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { burgerItemImageMap } from '../data/burgerImageCatalog';

const props = defineProps({
    selectedBun: {
        type: Object,
        default: null,
    },
    selectedPatty: {
        type: Object,
        default: null,
    },
    selectedToppings: {
        type: Array,
        default: () => [],
    },
    fallbackImageSrc: {
        type: String,
        default: '/images/Burger1.png',
    },
});

// Define the image sources and dimensions for each item type
// src: image source for the item
// imageHeight: sets how far down the image is displayed from the item above it
// stackOffset: adjust how much the item is covered by the item above it 

const itemStack = ref([]);
const stackCardElement = ref(null);
const stackWidth = ref(0);
const baseStackWidth = 352;
let resizeObserver = null;

const layoutScale = computed(() => {
    if (!stackWidth.value) {
        return 1;
    }

    return Math.min(stackWidth.value / baseStackWidth, 1);
});

const positionedItemStack = computed(() => {
    let currentY = 0;
    const totalItems = itemStack.value.length;
    const scale = layoutScale.value;

    return itemStack.value.map((item, index) => {
        const scaledHeight = item.imageHeight * scale;
        const positionedItem = {
            ...item,
            key: `${item.alt}-${index}`,
            top: (currentY - item.stackOffset) * scale,
            scaledHeight,
            zIndex: totalItems - index,
        };

        currentY += item.imageHeight;
        return positionedItem;
    });
});

const stackCanvasHeight = computed(() => {
    const scale = layoutScale.value;

    if (positionedItemStack.value.length === 0) {
        return Math.max(220 * scale, 180);
    }

    const lastItem = positionedItemStack.value[positionedItemStack.value.length - 1];
    return Math.max(lastItem.top + lastItem.scaledHeight + (50 * scale), Math.max(220 * scale, 180));
});

watch(
    () => [props.selectedBun, props.selectedPatty, props.selectedToppings],
    ([selectedBun, selectedPatty, selectedToppings]) => {
        const stack = [];

        if (selectedBun) {
            stack.push(getBunBottom(selectedBun.name));
        }

        // temp array for reversing the order of toppings so they stack correctly
        var reversedToppings = [];
        var toppingCount = 0;
        if (selectedToppings.length > 0) {
            for (const topping of selectedToppings) {
                for (toppingCount = 0; toppingCount < topping.quantity; toppingCount++) {
                    let item = getTopping(topping.name);
                    if (!item) continue;
                    item.isFlipped = toppingCount % 2 === 1;
                    reversedToppings.push(item);
                }
            }
            stack.push(...reversedToppings.reverse());
        }

        if (selectedPatty) {
            for (let i = 0; i < selectedPatty.quantity; i++) {
                stack.push(getPatty(selectedPatty.name));
            }
        }

        if (selectedBun) {
            stack.push(getBunTop(selectedBun.name));
        }

        itemStack.value = stack.filter(Boolean);
    },
    { immediate: true, deep: true }
);

function getBunTop(bun){
    if (!bun) return null;
    const bunImages = burgerItemImageMap.buns[bun];
    if (!bunImages) return null;
    return createStackItem(bunImages[0], `Image of ${bun} bun top`);
}

function getBunBottom(bun){
    if (!bun) return null;
    const bunImages = burgerItemImageMap.buns[bun];
    if (!bunImages) return null;
    return createStackItem(bunImages[1], `Image of ${bun} bun bottom`);
}

function getPatty(patty){
    if (!patty) return null;
    const pattyImage = burgerItemImageMap.patties[patty];
    if (!pattyImage) return null;
    return createStackItem(pattyImage, `Image of ${patty}`);
}

function getTopping(topping){
    if (!topping) return null;
    const toppingImage = burgerItemImageMap.toppings[topping];
    if (!toppingImage) return null;
    return createStackItem(toppingImage, `Image of ${topping}`);
}

function createStackItem(item, alt){
    return {
        src: item.src,
        imageHeight: item.imageHeight,
        stackOffset: item.stackOffset,
        isFlipped: false,
        alt,
    };
}

function syncStackWidth() {
    stackWidth.value = stackCardElement.value?.clientWidth ?? 0;
}

onMounted(() => {
    syncStackWidth();

    if (!stackCardElement.value || typeof ResizeObserver === 'undefined') {
        return;
    }

    resizeObserver = new ResizeObserver(() => {
        syncStackWidth();
    });
    resizeObserver.observe(stackCardElement.value);
});

onBeforeUnmount(() => {
    resizeObserver?.disconnect();
});

</script>

<template>
<div ref="stackCardElement" class="card burger-image-card">
    <div class="burger-stack" :style="{ height: `${stackCanvasHeight}px` }">
        <div
            v-for="item in positionedItemStack"
            :key="item.key"
            class="burger-item"
            :style="{ top: `${item.top}px`, zIndex: item.zIndex }"
        >
            <img
                :src="item.src"
                :alt="item.alt"
                class="burger-layer"
                :class="{ flipped: item.isFlipped }"
            />
        </div>

        <img
            v-if="positionedItemStack.length === 0"
            class="burger-fallback-image"
            :src="fallbackImageSrc"
            alt="Image of burger"
        />
    </div>
</div>
</template>

<style scoped>
.burger-image-card {
    padding: 1rem;
}

.burger-stack {
    position: relative;
    width: min(100%, 22rem);
    margin: 0 auto;
}

.burger-item {
    position: absolute;
    left: 50%;
    width: 100%;
    transform: translateX(-50%);
}

.burger-layer,
.burger-fallback-image {
    display: block;
    width: 100%;
    height: auto;
}
.burger-layer.flipped {
    transform: scaleX(-1);
}
</style>
