<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import BurgerOptionsComp from '../components/BurgerOptionsComp.vue';
import FriesOptionsComp from '../components/FriesOptionsComp.vue';
import { useCart } from '../composables/useCart';

const OPTION_GROUP_METADATA = {
    burger: {
        buns: { label: 'Bun', selectionMode: 'single' },
        patties: { label: 'Patty', selectionMode: 'single_quantity' },
        toppings: { label: 'Toppings', selectionMode: 'multiple' },
    },
    fries: {
        sizes: { label: 'Size', selectionMode: 'single' },
        types: { label: 'Type', selectionMode: 'single' },
        seasonings: { label: 'Seasoning', selectionMode: 'single' },
    },
};

const PRODUCT_OPTIONS_ENDPOINTS = {
    burger: 'http://localhost:8000/Items/Burger',
    fries: 'http://localhost:8000/Items/Fries',
};

const router = useRouter();
const { addItem } = useCart();

function isMultipleSelectionGroup(group) {
    return group.selectionMode === 'multiple';
}

function isSingleQuantitySelectionGroup(group) {
    return group.selectionMode === 'single_quantity';
}

function getDefaultSelection(group) {
    if (isMultipleSelectionGroup(group)) {
        return [];
    }

    const defaultItem = group.items.find((item) => item.quantity > 0) ?? group.items[0];
    if (!defaultItem) {
        return null;
    }

    if (isSingleQuantitySelectionGroup(group)) {
        return {
            id: defaultItem.id,
            quantity: 1,
        };
    }

    return defaultItem.id;
}

function getMultiSelections(selection) {
    if (!Array.isArray(selection)) {
        return [];
    }

    return selection
        .filter((entry) => entry && typeof entry === 'object' && !Array.isArray(entry))
        .map((entry) => ({
            id: String(entry.id),
            quantity: Math.max(1, Number.parseInt(entry.quantity ?? 1, 10) || 1),
        }))
        .sort((left, right) => left.id.localeCompare(right.id));
}

function getSingleQuantitySelection(selection) {
    if (!selection || typeof selection !== 'object' || Array.isArray(selection)) {
        return null;
    }

    return {
        id: String(selection.id ?? ''),
        quantity: Math.max(1, Number.parseInt(selection.quantity ?? 1, 10) || 1),
    };
}

function normalizeProductOptions(productKey, optionsByGroup) {
    const metadata = OPTION_GROUP_METADATA[productKey] ?? {};

    return Object.entries(optionsByGroup).map(([key, items]) => ({
        key,
        label: metadata[key]?.label ?? key,
        selectionMode: metadata[key]?.selectionMode ?? 'single',
        items: items.map((item) => ({
            ...item,
            id: String(item.id),
        })),
    }));
}

const product = computed(() => {
    return (router.currentRoute.value.params.product || '').toLowerCase();
});

const productImages = computed(() => {
    switch (product.value) {
        case 'burger':
            return ['/images/Burger1.png', '/images/Burger2.png', '/images/Burger3.png'];
        case 'fries':
            return ['/images/Fries1.png', '/images/Fries2.png', '/images/Fries3.png'];
        default:
            return ['/images/placeholder.png', '/images/placeholder.png', '/images/placeholder.png'];
    }
});

const productData = computed(() => {
    switch (product.value) {
        case 'burger':
            return {
                name: 'Classic Burger',
                description: 'A crave-worthy mix of crisp, golden bites with fresh toppings. Balanced, filling, and perfect for a quick lunch or family night in.',
                price: 0,
            };
        case 'fries':
            return {
                name: 'Crispy Fries',
                description: 'Golden, crispy fries seasoned to perfection. A deliciously satisfying side that pairs perfectly with any meal.',
                price: 0,
            };
        default:
            return {
                name: 'Unknown Product',
                description: 'No description available.',
                price: 0,
            };
    }
});

const rawProductOptions = ref({});

const customizationComponent = computed(() => {
    switch (product.value) {
        case 'burger':
            return BurgerOptionsComp;
        case 'fries':
            return FriesOptionsComp;
        default:
            return null;
    }
});

const optionGroups = computed(() => normalizeProductOptions(product.value, rawProductOptions.value));
const selectedOptions = ref({});
const selectedIndex = ref(0);
const cartFeedbackMessage = ref('');

let cartFeedbackTimeoutId = null;

function clearCartFeedbackTimeout() {
    if (cartFeedbackTimeoutId !== null) {
        clearTimeout(cartFeedbackTimeoutId);
        cartFeedbackTimeoutId = null;
    }
}

function showCartFeedback(message) {
    cartFeedbackMessage.value = message;
    clearCartFeedbackTimeout();
    cartFeedbackTimeoutId = window.setTimeout(() => {
        cartFeedbackMessage.value = '';
        cartFeedbackTimeoutId = null;
    }, 3000);
}

watch(
    optionGroups,
    (groups) => {
        selectedOptions.value = groups.reduce((nextSelections, group) => {
            nextSelections[group.key] = getDefaultSelection(group);
            return nextSelections;
        }, {});
    },
    { immediate: true }
);

watch(
    product,
    async (productKey, _previousProductKey, onCleanup) => {
        selectedIndex.value = 0;
        cartFeedbackMessage.value = '';
        clearCartFeedbackTimeout();
        rawProductOptions.value = {};

        const endpoint = PRODUCT_OPTIONS_ENDPOINTS[productKey];
        if (!endpoint) {
            return;
        }

        const abortController = new AbortController();
        onCleanup(() => abortController.abort());

        try {
            const response = await fetch(endpoint, { signal: abortController.signal });
            if (!response.ok) {
                throw new Error(`Failed to load ${productKey} options: ${response.status} ${response.statusText}`);
            }

            rawProductOptions.value = await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                return;
            }

            console.error(`Unable to fetch ${productKey} options`, error);
        }
    },
    { immediate: true }
);

const totalPrice = computed(() => {
    const base = Number(productData.value.price) || 0;
    const optionTotal = optionGroups.value.reduce((runningTotal, group) => {
        if (isMultipleSelectionGroup(group)) {
            const multiSelections = getMultiSelections(selectedOptions.value[group.key]);

            return runningTotal + multiSelections.reduce((groupTotal, selection) => {
                const selectedItem = group.items.find((item) => item.id === selection.id);
                return groupTotal + ((selectedItem?.price ?? 0) * selection.quantity);
            }, 0);
        }

        if (isSingleQuantitySelectionGroup(group)) {
            const selection = getSingleQuantitySelection(selectedOptions.value[group.key]);
            const selectedItem = group.items.find((item) => item.id === selection?.id);
            return runningTotal + ((selectedItem?.price ?? 0) * (selection?.quantity ?? 1));
        }

        const selectedItem = group.items.find((item) => item.id === selectedOptions.value[group.key]);
        return runningTotal + (selectedItem?.price ?? 0);
    }, 0);

    return `${(base + optionTotal).toFixed(2)}`;
});

const selectThumbnail = (index) => {
    selectedIndex.value = index;
};

const goMainPage = () => {
    router.push({ name: 'main' });
};

const addToCart = () => {
    addItem({
        id: product.value,
        name: productData.value.name,
        image: productImages.value[0],
        unitPrice: Number(totalPrice.value),
        quantity: Number(document.getElementById('quantity').value) || 1,
        options: optionGroups.value.map((group) => {
            if (isMultipleSelectionGroup(group)) {
                const selectedItemsById = new Map(group.items.map((item) => [item.id, item]));
                const structuredSelections = getMultiSelections(selectedOptions.value[group.key])
                    .map((selection) => {
                        const selectedItem = selectedItemsById.get(selection.id);
                        if (!selectedItem) {
                            return null;
                        }

                        return {
                            id: selectedItem.id,
                            name: selectedItem.name,
                            quantity: selection.quantity,
                        };
                    })
                    .filter(Boolean);

                return {
                    id: structuredSelections.map((selection) => ({
                        id: selection.id,
                        quantity: selection.quantity,
                    })),
                    name: group.label,
                    value: structuredSelections.map((selection) => ({
                        id: selection.id,
                        name: selection.name,
                        quantity: selection.quantity,
                    })),
                };
            }

            if (isSingleQuantitySelectionGroup(group)) {
                const selection = getSingleQuantitySelection(selectedOptions.value[group.key]);
                const selectedItem = group.items.find((item) => item.id === selection?.id);

                return {
                    id: selectedItem?.id ?? null,
                    name: group.label,
                    value: selectedItem
                        ? [{
                            id: selectedItem.id,
                            name: selectedItem.name,
                            quantity: selection?.quantity ?? 1,
                        }]
                        : null,
                };
            }

            const selectedItem = group.items.find((item) => item.id === selectedOptions.value[group.key]);

            return {
                id: selectedItem?.id ?? null,
                name: group.label,
                value: selectedItem?.name ?? null,
            };
        }),
    });
    showCartFeedback(`${productData.value.name} added to cart.`);
};

onBeforeUnmount(() => {
    clearCartFeedbackTimeout();
});
</script>

<template>
<section class="page product-page">
    <div class="product-breadcrumbs">
        <span class="hover" @click="goMainPage">Home</span> / <span class="current">{{ $route.params.product }}</span>
    </div>

    <div class="product-grid">
        <div name="product-gallery" class="product-gallery card">
            <img name="product-image" class="product-hero" :src="productImages[selectedIndex]" alt="Product hero" />
            <div class="thumbnail-row">
                <button
                    v-for="(img, idx) in productImages"
                    :key="img"
                    class="thumb"
                    :class="{ 'is-active': idx === selectedIndex }"
                    type="button"
                    @click="selectThumbnail(idx)"
                >
                    <img :src="img" :alt="`Thumbnail ${idx + 1}`" />
                </button>
            </div>
        </div>

        <div class="product-info card">
            <div class="product-header">
                <div>
                    <h2>{{ productData.name }}</h2>
                    <p class="product-description">
                        {{ productData.description }}
                    </p>
                </div>
                <div class="price-tag">
                    <span class="price">${{ totalPrice }}</span>
                </div>
            </div>

            <div class="product-actions">
                <button class="primary" type="button" @click="addToCart">
                    Add to Cart
                </button>
                <label class="quantity-input-group" for="quantity">
                    <span>Qty</span>
                    <input id="quantity" class="quantity-input" type="number" min="1" value="1" />
                </label>
            </div>

            <div
                v-if="cartFeedbackMessage"
                class="cart-feedback"
                role="status"
                aria-live="polite"
            >
                {{ cartFeedbackMessage }}
            </div>
        </div>
    </div>

    <div class="details-grid" name="product-customization">
        <div class="customization card">
            <component
                :is="customizationComponent"
                v-if="customizationComponent"
                v-model="selectedOptions"
                :option-groups="optionGroups"
            />
            <template v-else>
                <h3>Customize your order</h3>
                <p>No customization options are available for this product.</p>
            </template>
        </div>
    </div>
</section>
</template>

<style src="../styles/ProductView.css" scoped></style>
