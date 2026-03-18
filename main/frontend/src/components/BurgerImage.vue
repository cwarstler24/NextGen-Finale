<script setup>
import { computed, ref, watch } from 'vue';

const props = defineProps({
    imageSrc: {
        type: String,
        required: true,
    },
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
});

// Define the image sources and dimensions for each item type
// src: image source for the item
// imageHeight: sets how far down the image is displayed from the item above it
// stackOffset: adjust how much the item is covered by the item above it 
const itemImageMap = {
    buns: {
        "Whole Wheat": {
            0: {
                "src": '/images/items/whole_wheat_bun_bottom.png',
                "imageHeight": 50,
                "stackOffset": 15,
            },
            1: {
                "src": '/images/items/whole_wheat_bun_top.png',
                "imageHeight": 100,
                "stackOffset": 0,
            },
        },
        "Sesame": {
            0: {
                "src": '/images/items/sesame_bun_bottom.png',
                "imageHeight": 40,
                "stackOffset": 0,
            },
            1: {
                "src": '/images/items/sesame_bun_top.png',
                "imageHeight": 80,
                "stackOffset": -10,
            },
        },
        "Brioche": {
            0: {
                "src": '/images/items/brioche_bun_bottom.png',
                "imageHeight": 50,
                "stackOffset": 15,
            },
            1: {
                "src": '/images/items/brioche_bun_top.png',
                "imageHeight": 130,
                "stackOffset": 0,
            },
        },
        "None": {
            0: {
                "src": '/images/items/blank_png.png',
                "imageHeight": 0,
                "stackOffset": 0,
            },
            1: {
                "src": '/images/items/blank_png.png',
                "imageHeight": 0,
                "stackOffset": 0,
            },
        },
    },
    patties: {
        "Beef": {
            "src": '/images/items/beef_patty.png',
            "imageHeight": 70,
            "stackOffset": 0,
        },
        "Chicken": {
            "src": '/images/items/chicken_patty.png',
            "imageHeight": 55,
            "stackOffset": 5,
        },
        "Veggie": {
            "src": '/images/items/veggie_patty.png',
            "imageHeight": 70,
            "stackOffset": 0,
        },
        "None": {
            "src": '/images/items/blank_png.png',
            "imageHeight": 0,
            "stackOffset": 0,
        },
    },
    toppings: {
        "Lettuce": {
            "src": '/images/items/lettuce.png',
            "imageHeight": 65,
            "stackOffset": 10,
        },
        "Tomato": {
            "src": '/images/items/tomato.png',
            "imageHeight": 10,
            "stackOffset": -10,
        },
        "Onion": {
            "src": '/images/items/onion.png',
            "imageHeight": 10,
            "stackOffset": -15,
        },
        "Pickles": {
            "src": '/images/items/pickels.png',
            "imageHeight": 15,
            "stackOffset": -15,
        },
        "Cheese": {
            "src": '/images/items/cheese.png',
            "imageHeight": 5,
            "stackOffset": 5,
        },
        "Bacon": {
            "src": '/images/items/bacon.png',
            "imageHeight": 20,
            "stackOffset": 10,
        },
        "Jalapenos": {
            "src": '/images/items/jalepeno.png',
            "imageHeight": 20,
            "stackOffset": 0,
        },
        "Mushrooms": {
            "src": '/images/items/mushroom.png',
            "imageHeight": 10,
            "stackOffset": 0,
        },
        "Ketchup": {
            "src": '/images/items/ketchup.png',
            "imageHeight": 5,
            "stackOffset": 0,
        },
        "Mustard": {
            "src": '/images/items/mustard.png',
            "imageHeight": 5,
            "stackOffset": 0,
        },
        "Mayonnaise": {
            "src": '/images/items/mayonnaise.png',
            "imageHeight": 5,
            "stackOffset": 0,
        },
        "Avocado": {
            "src": '/images/items/avocado.png',
            "imageHeight": 0,
            "stackOffset": 5,
        },
        "None": {
            "src": '/images/items/blank_png.png',
            "imageHeight": 0,
            "stackOffset": 0,
        },
    },
};

const itemStack = ref([]);

const positionedItemStack = computed(() => {
    let currentY = 0;
    const totalItems = itemStack.value.length;

    return itemStack.value.map((item, index) => {
        const positionedItem = {
            ...item,
            key: `${item.alt}-${index}`,
            top: currentY - item.stackOffset,
            zIndex: totalItems - index,
        };

        currentY += item.imageHeight;
        return positionedItem;
    });
});

const stackCanvasHeight = computed(() => {
    if (positionedItemStack.value.length === 0) {
        return 320;
    }

    const lastItem = positionedItemStack.value[positionedItemStack.value.length - 1];
    return Math.max(lastItem.top + lastItem.imageHeight + 50, 320);
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
    return createStackItem(itemImageMap.buns[bun][0], `Image of ${bun} bun top`);
}

function getBunBottom(bun){
    if (!bun) return null;
    return createStackItem(itemImageMap.buns[bun][1], `Image of ${bun} bun bottom`);
}

function getPatty(patty){
    if (!patty) return null;
    return createStackItem(itemImageMap.patties[patty], `Image of ${patty}`);
}

function getTopping(topping){
    if (!topping) return null;
    return createStackItem(itemImageMap.toppings[topping], `Image of ${topping}`);
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

</script>

<template>
<div class="card">
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
            :src="imageSrc"
            alt="Image of burger"
        />
    </div>
</div>
</template>

<style scoped>
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
