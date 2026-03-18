<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';

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
const itemImageMap = {
    buns: {
        "Whole Wheat": {
            0: {
                "src": '/images/items/whole_wheat_bun_bottom.png',
                "imageHeight": 50,
                "stackOffset": 5,
            },
            1: {
                "src": '/images/items/whole_wheat_bun_top.png',
                "imageHeight": 105,
                "stackOffset": 0,
            },
        },
        "Sesame": {
            0: {
                "src": '/images/items/sesame_bun_bottom.png',
                "imageHeight": 40,
                "stackOffset": -15,
            },
            1: {
                "src": '/images/items/sesame_bun_top.png',
                "imageHeight": 90,
                "stackOffset": -10,
            },
        },
        "Brioche": {
            0: {
                "src": '/images/items/brioche_bun_bottom.png',
                "imageHeight": 70,
                "stackOffset": 5,
            },
            1: {
                "src": '/images/items/brioche_bun_top.png',
                "imageHeight": 100,
                "stackOffset": 0,
            },
        },
        "Pretzel": {
            0: {
                "src": '/images/items/pretzle_bun_bottom.png',
                "imageHeight": 80,
                "stackOffset": 5,
            },
            1: {
                "src": '/images/items/pretzle_bun_top.png',
                "imageHeight": 135,
                "stackOffset": 0,
            },
        },
        "Dirt": {
            0: {
                "src": '/images/items/dirt_bun_bottom.png',
                "imageHeight": 90,
                "stackOffset": 0,
            },
            1: {
                "src": '/images/items/dirt_bun_top.png',
                "imageHeight": 80,
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
            "imageHeight": 50,
            "stackOffset": 0,
        },
        "Chicken": {
            "src": '/images/items/chicken_patty.png',
            "imageHeight": 45,
            "stackOffset": 10,
        },
        "Veggie": {
            "src": '/images/items/veggie_patty.png',
            "imageHeight": 60,
            "stackOffset": 5,
        },
        "Fish": {
            "src": '/images/items/fish_patty.png',
            "imageHeight": 45,
            "stackOffset": 0,
        },
        "Smash": {
            "src": '/images/items/smash_patty.png',
            "imageHeight": 20,
            "stackOffset": 0,
        },
        "Dirt": {
            "src": '/images/items/dirt_patty.png',
            "imageHeight": 55,
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
            "imageHeight": 45,
            "stackOffset": 10,
        },
        "Tomato": {
            "src": '/images/items/tomato.png',
            "imageHeight": 10,
            "stackOffset": -5,
        },
        "Onion": {
            "src": '/images/items/onion.png',
            "imageHeight": 10,
            "stackOffset": -10,
        },
        "Pickles": {
            "src": '/images/items/pickels.png',
            "imageHeight": 5,
            "stackOffset": -15,
        },
        "Cheese": {
            "src": '/images/items/cheese.png',
            "imageHeight": 5,
            "stackOffset": 5,
        },
        "Bacon": {
            "src": '/images/items/bacon.png',
            "imageHeight": 15,
            "stackOffset": 15,
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
        "Barbecue": {
            "src": '/images/items/barbecue.png',
            "imageHeight": 5,
            "stackOffset": 0,
        },
        "Blue Cheese": {
            "src": '/images/items/blue_cheese.png',
            "imageHeight": 5,
            "stackOffset": 5,
        },
        "Cheeze Wiz": {
            "src": '/images/items/cheez_wiz.png',
            "imageHeight": 5,
            "stackOffset": 0,
        },
        "Colby Jack": {
            "src": '/images/items/colby_jack.png',
            "imageHeight": 5,
            "stackOffset": 5,
        },
        "Crispy Onions": {
            "src": '/images/items/crispy_onions.png',
            "imageHeight": 10,
            "stackOffset": 40,
        },
        "Egg": {
            "src": '/images/items/egg.png',
            "imageHeight": 20,
            "stackOffset": 5,
        },
        "Honey": {
            "src": '/images/items/honey.png',
            "imageHeight": 5,
            "stackOffset": 0,
        },
        "Jalapeno Jelly": {
            "src": '/images/items/jalepeno_jelly.png',
            "imageHeight": 10,
            "stackOffset": 0,
        },
        "Mac and Cheese": {
            "src": '/images/items/mac_and_cheese.png',
            "imageHeight": 25,
            "stackOffset": 10,
        },
        "Peanut Butter": {
            "src": '/images/items/peanut_butter.png',
            "imageHeight": 5,
            "stackOffset": 0,
        },
        "Ranch": {
            "src": '/images/items/ranch.png',
            "imageHeight": 5,
            "stackOffset": 0,
        },
        "Special Slime Sauce": {
            "src": '/images/items/special_slime_sauce.png',
            "imageHeight": 5,
            "stackOffset": 0,
        },
        "Swiss Cheese": {
            "src": '/images/items/swiss_cheese.png',
            "imageHeight": 5,
            "stackOffset": 5,
        },
        "Tarter Sauce": {
            "src": '/images/items/tartar_sauce.png',
            "imageHeight": 5,
            "stackOffset": 0,
        },
        "None": {
            "src": '/images/items/blank_png.png',
            "imageHeight": 0,
            "stackOffset": 0,
        },
    },
};

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
    const bunImages = itemImageMap.buns[bun];
    if (!bunImages) return null;
    return createStackItem(bunImages[0], `Image of ${bun} bun top`);
}

function getBunBottom(bun){
    if (!bun) return null;
    const bunImages = itemImageMap.buns[bun];
    if (!bunImages) return null;
    return createStackItem(bunImages[1], `Image of ${bun} bun bottom`);
}

function getPatty(patty){
    if (!patty) return null;
    const pattyImage = itemImageMap.patties[patty];
    if (!pattyImage) return null;
    return createStackItem(pattyImage, `Image of ${patty}`);
}

function getTopping(topping){
    if (!topping) return null;
    const toppingImage = itemImageMap.toppings[topping];
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
