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

const itemImageMap = {
    buns: {
        "Whole Wheat": {
            0: {
                "src": '/images/items/whole_wheat_bun_bottom.png',
                "height": 100,
            },
            1: {
                "src": '/images/items/whole_wheat_bun_top.png',
                "height": 80,
            },
        },
        "Sesame": {
            0: {
                "src": '/images/items/sesame_bun_bottom.png',
                "height": 100,
            },
            1: {
                "src": '/images/items/sesame_bun_top.png',
                "height": 80,
            },
        },
        "Brioche": {
            0: {
                "src": '/images/items/brioche_bun_bottom.png',
                "height": 100,
            },
            1: {
                "src": '/images/items/brioche_bun_top.png',
                "height": 80,
            },
        },
        "None": {
            0: {
                "src": '/images/items/blank_png.png',
                "height": 0,
            },
            1: {
                "src": '/images/items/blank_png.png',
                "height": 0,
            },
        },
    },
    patties: {
        "Beef": {
            "src": '/images/items/beef_patty.png',
            "height": 70,
        },
        "Chicken": {
            "src": '/images/items/chicken_patty.png',
            "height": 65,
        },
        "Veggie": {
            "src": '/images/items/veggie_patty.png',
            "height": 70,
        },
        "None": {
            "src": '/images/items/blank_png.png',
            "height": 0,
        },
    },
    toppings: {
        "Lettuce": {
            "src": '/images/items/lettuce.png',
            "height": 35,
        },
        "Tomato": {
            "src": '/images/items/tomato.png',
            "height": 20,
        },
        "Onion": {
            "src": '/images/items/onion.png',
            "height": 10,
        },
        "Pickles": {
            "src": '/images/items/pickels.png',
            "height": 10,
        },
        "Cheese": {
            "src": '/images/items/cheese.png',
            "height": 10,
        },
        "Bacon": {
            "src": '/images/items/bacon.png',
            "height": 30,
        },
        "Jalapeno": {
            "src": '/images/items/jalepeno.png',
            "height": 80,
        },
        "Mushroom": {
            "src": '/images/items/mushroom.png',
            "height": 50,
        },
        "Ketchup": {
            "src": '/images/items/ketchup.png',
            "height": 50,
        },
        "Mustard": {
            "src": '/images/items/mustard.png',
            "height": 50,
        },
        "Mayonnaise": {
            "src": '/images/items/mayonnaise.png',
            "height": 50,
        },
        "Avocado": {
            "src": '/images/items/avocado.png',
            "height": 15,
        },
        "None": {
            "src": '/images/items/blank_png.png',
            "height": 0,
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
            top: currentY,
            zIndex: totalItems - index,
        };

        currentY += item.height;
        return positionedItem;
    });
});

const stackCanvasHeight = computed(() => {
    if (positionedItemStack.value.length === 0) {
        return 320;
    }

    const lastItem = positionedItemStack.value[positionedItemStack.value.length - 1];
    return Math.max(lastItem.top + lastItem.height, 320);
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
                    reversedToppings.push(getTopping(topping.name));
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
    return {
        src: itemImageMap.buns[bun][0].src,
        height: itemImageMap.buns[bun][0].height,
        alt: `Image of ${bun} bun top`,
    };
}

function getBunBottom(bun){
    if (!bun) return null;
    return {
        src: itemImageMap.buns[bun][1].src,
        height: itemImageMap.buns[bun][1].height,
        alt: `Image of ${bun} bun bottom`,
    };
}

function getPatty(patty){
    if (!patty) return null;
    return {
        src: itemImageMap.patties[patty].src,
        height: itemImageMap.patties[patty].height,
        alt: `Image of ${patty}`,
    };
}

function getTopping(topping){
    if (!topping) return null;
    return {
        src: itemImageMap.toppings[topping].src,
        height: itemImageMap.toppings[topping].height,
        alt: `Image of ${topping}`,
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
</style>
