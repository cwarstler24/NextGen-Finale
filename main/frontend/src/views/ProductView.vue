<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import BurgerOptionsComp from '../components/BurgerOptionsComp.vue';
import FriesOptionsComp from '../components/FriesOptionsComp.vue';
import BurgerImage from '../components/BurgerImage.vue';
import { useCart } from '../composables/useCart';
import customBurger from '../data/customBurgers.js';
import { buildBurgerSelectionsFromPreset } from '../data/presetBurgerOptions.js';

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

function getDefaultSelections(groups) {
    return groups.reduce((nextSelections, group) => {
        nextSelections[group.key] = getDefaultSelection(group);
        return nextSelections;
    }, {});
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

function normalizeSelectionId(value) {
    if (value === null || value === undefined) {
        return null;
    }

    return String(value);
}

function getOptionItemPrice(item) {
    const price = Number(item?.price);
    return Number.isFinite(price) ? price : 0;
}

function findGroupItem(group, selectionId) {
    const normalizedSelectionId = normalizeSelectionId(selectionId);
    if (!group || normalizedSelectionId === null) {
        return null;
    }

    return group.items.find((item) => item.id === normalizedSelectionId) ?? null;
}

function formatList(values) {
    if (values.length <= 1) {
        return values[0] ?? '';
    }

    if (values.length === 2) {
        return `${values[0]} and ${values[1]}`;
    }

    return `${values.slice(0, -1).join(', ')}, and ${values[values.length - 1]}`;
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

const presetRouteParam = computed(() => router.currentRoute.value.params.presetId ?? null);
const presetBurgerId = computed(() => {
    if (presetRouteParam.value === null) {
        return null;
    }

    const parsedId = Number.parseInt(String(presetRouteParam.value), 10);
    return Number.isNaN(parsedId) ? null : parsedId;
});

const presetBurger = computed(() => {
    if (product.value !== 'burger' || presetBurgerId.value === null) {
        return null;
    }

    return customBurger.find((burger) => burger.id === presetBurgerId.value) ?? null;
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
            if (presetBurger.value) {
                return {
                    name: presetBurger.value.name,
                    description: presetBurger.value.description,
                    price: 0,
                };
            }

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
const optionsLoadState = ref('idle');
const optionsReloadToken = ref(0);

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
const quantity = ref(1);
const cartFeedbackMessage = ref('');
const presetLoadMessage = ref('');
const isPresetNoticeVisible = ref(false);
const isLoadingOptions = computed(() => optionsLoadState.value === 'loading');
const isOptionsUnavailable = computed(() => optionsLoadState.value === 'error');
const isOrderingDisabled = computed(() => {
    if (!customizationComponent.value) {
        return false;
    }

    return isLoadingOptions.value || isOptionsUnavailable.value || optionGroups.value.length === 0;
});

let cartFeedbackTimeoutId = null;
let presetNoticeTimeoutId = null;

function clearCartFeedbackTimeout() {
    if (cartFeedbackTimeoutId !== null) {
        clearTimeout(cartFeedbackTimeoutId);
        cartFeedbackTimeoutId = null;
    }
}

function clearPresetNoticeTimeout() {
    if (presetNoticeTimeoutId !== null) {
        clearTimeout(presetNoticeTimeoutId);
        presetNoticeTimeoutId = null;
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

function showPresetNotice() {
    if (!presetLoadMessage.value) {
        isPresetNoticeVisible.value = false;
        clearPresetNoticeTimeout();
        return;
    }

    isPresetNoticeVisible.value = true;
    clearPresetNoticeTimeout();
    presetNoticeTimeoutId = window.setTimeout(() => {
        isPresetNoticeVisible.value = false;
        presetNoticeTimeoutId = null;
    }, 5000);
}

function dismissPresetNotice() {
    isPresetNoticeVisible.value = false;
    clearPresetNoticeTimeout();
}

watch(
    [optionGroups, presetBurgerId],
    ([groups]) => {
        const defaultSelections = getDefaultSelections(groups);

        if (groups.length === 0) {
            selectedOptions.value = defaultSelections;
            presetLoadMessage.value = '';
            dismissPresetNotice();
            return;
        }

        if (product.value !== 'burger') {
            selectedOptions.value = defaultSelections;
            presetLoadMessage.value = '';
            dismissPresetNotice();
            return;
        }

        if (presetRouteParam.value !== null && presetBurger.value === null) {
            selectedOptions.value = defaultSelections;
            presetLoadMessage.value = 'We could not find that signature burger, so the standard burger builder is loaded instead.';
            showPresetNotice();
            return;
        }

        if (!presetBurger.value) {
            selectedOptions.value = defaultSelections;
            presetLoadMessage.value = '';
            dismissPresetNotice();
            return;
        }

        const {
            selections,
            unavailableIngredients,
            adjustedIngredients,
        } = buildBurgerSelectionsFromPreset(groups, presetBurger.value);

        selectedOptions.value = selections;

        const messageParts = ['Signature burger loaded.'];
        if (unavailableIngredients.length > 0) {
            messageParts.push(`Unavailable ingredients were skipped: ${formatList(unavailableIngredients)}.`);
        }
        if (adjustedIngredients.length > 0) {
            messageParts.push(`Limited stock reduced these quantities: ${formatList(adjustedIngredients)}.`);
        }
        if (unavailableIngredients.length === 0 && adjustedIngredients.length === 0) {
            messageParts.push('You can adjust any option before adding it to cart.');
        }

        presetLoadMessage.value = messageParts.join(' ');
        showPresetNotice();
    },
    { immediate: true }
);

function retryLoadingOptions() {
    optionsReloadToken.value += 1;
}

watch(
    [product, optionsReloadToken],
    async ([productKey], _previousValues, onCleanup) => {
        selectedIndex.value = 0;
        quantity.value = 1;
        cartFeedbackMessage.value = '';
        clearCartFeedbackTimeout();
        rawProductOptions.value = {};
        optionsLoadState.value = 'idle';

        const endpoint = PRODUCT_OPTIONS_ENDPOINTS[productKey];
        if (!endpoint) {
            return;
        }

        const abortController = new AbortController();
        onCleanup(() => abortController.abort());
        optionsLoadState.value = 'loading';

        try {
            const response = await fetch(endpoint, { signal: abortController.signal });
            if (!response.ok) {
                throw new Error(`Failed to load ${productKey} options: ${response.status} ${response.statusText}`);
            }

            rawProductOptions.value = await response.json();
            optionsLoadState.value = 'success';
        } catch (error) {
            if (error.name === 'AbortError') {
                return;
            }

            optionsLoadState.value = 'error';
            console.error(`Unable to fetch ${productKey} options`, error);
        }
    },
    { immediate: true }
);

const normalizedQuantity = computed(() => Math.max(1, Number.parseInt(quantity.value, 10) || 1));

function syncQuantityInput() {
    quantity.value = normalizedQuantity.value;
}

const unitPrice = computed(() => {
    const base = Number(productData.value.price) || 0;
    const optionTotal = optionGroups.value.reduce((runningTotal, group) => {
        if (isMultipleSelectionGroup(group)) {
            const multiSelections = getMultiSelections(selectedOptions.value[group.key]);

            return runningTotal + multiSelections.reduce((groupTotal, selection) => {
                const selectedItem = findGroupItem(group, selection.id);
                return groupTotal + (getOptionItemPrice(selectedItem) * selection.quantity);
            }, 0);
        }

        if (isSingleQuantitySelectionGroup(group)) {
            const selection = getSingleQuantitySelection(selectedOptions.value[group.key]);
            const selectedItem = findGroupItem(group, selection?.id);
            return runningTotal + (getOptionItemPrice(selectedItem) * (selection?.quantity ?? 1));
        }

        const selectedItem = findGroupItem(group, selectedOptions.value[group.key]);
        return runningTotal + getOptionItemPrice(selectedItem);
    }, 0);

    return base + optionTotal;
});

const totalPrice = computed(() => `${(unitPrice.value * normalizedQuantity.value).toFixed(2)}`);

function getOptionGroup(groupKey) {
    return optionGroups.value.find((group) => group.key === groupKey) ?? null;
}

function getSelectedSingleOptionDetails(groupKey) {
    const group = getOptionGroup(groupKey);
    if (!group) {
        return null;
    }

    if (isSingleQuantitySelectionGroup(group)) {
        const selection = getSingleQuantitySelection(selectedOptions.value[groupKey]);
        const selectedItem = findGroupItem(group, selection?.id);

        if (!selectedItem) {
            return null;
        }

        return {
            ...selectedItem,
            quantity: selection?.quantity ?? 1,
        };
    }

    const selectedItem = findGroupItem(group, selectedOptions.value[groupKey]);
    return selectedItem ? { ...selectedItem } : null;
}

function getSelectedMultiOptionDetails(groupKey) {
    const group = getOptionGroup(groupKey);
    if (!group) {
        return [];
    }

    return getMultiSelections(selectedOptions.value[groupKey])
        .map((selection) => {
            const selectedItem = findGroupItem(group, selection.id);
            if (!selectedItem) {
                return null;
            }

            return {
                ...selectedItem,
                quantity: selection.quantity,
            };
        })
        .filter(Boolean);
}

const selectedBurgerBun = computed(() => (product.value === 'burger'
    ? getSelectedSingleOptionDetails('buns')
    : null));

const selectedBurgerPatty = computed(() => (product.value === 'burger'
    ? getSelectedSingleOptionDetails('patties')
    : null));

const selectedBurgerToppings = computed(() => (product.value === 'burger'
    ? getSelectedMultiOptionDetails('toppings')
    : []));

const selectThumbnail = (index) => {
    selectedIndex.value = index;
};

const goMainPage = () => {
    router.push({ name: 'main' });
};

const startFromScratch = () => {
    dismissPresetNotice();
    router.push({ name: 'product', params: { product: 'Burger' } });
};

const addToCart = () => {
    if (isOrderingDisabled.value) {
        return;
    }

    if (totalPrice.value === '0.00') {
        showCartFeedback('Please select at least one option before adding to cart.');
        return;
    }

    addItem({
        id: product.value,
        name: productData.value.name,
        image: productImages.value[0],
        unitPrice: unitPrice.value,
        quantity: normalizedQuantity.value,
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
                const selectedItem = findGroupItem(group, selection?.id);

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

            const selectedItem = findGroupItem(group, selectedOptions.value[group.key]);

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
    clearPresetNoticeTimeout();
});
</script>

<template>
<section class="page product-page">
    <div class="product-breadcrumbs">
        <span class="hover" @click="goMainPage">Home</span> / <span class="current">{{ productData.name }}</span>
    </div>

    <div class="product-grid">
        <component
            :is="BurgerImage"
            v-if="product === 'burger'"
            :selected-bun="selectedBurgerBun"
            :selected-patty="selectedBurgerPatty"
            :selected-toppings="selectedBurgerToppings"
        />
        <div v-else name="product-gallery" class="product-gallery card">
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

            <div
                v-if="presetLoadMessage && isPresetNoticeVisible"
                class="preset-status"
                role="status"
                aria-live="polite"
            >
                <span class="preset-status__message">{{ presetLoadMessage }}</span>
                <div class="preset-status__actions">
                    <button
                        v-if="product === 'burger' && presetBurger"
                        class="secondary"
                        type="button"
                        @click="startFromScratch"
                    >
                        Start from scratch
                    </button>
                    <button class="secondary" type="button" @click="dismissPresetNotice">
                        Dismiss
                    </button>
                </div>
            </div>

            <div class="product-actions">
                <button class="primary" type="button" :disabled="isOrderingDisabled" @click="addToCart">
                    Add to Cart
                </button>
                <label class="quantity-input-group" for="quantity">
                    <span>Qty</span>
                    <input
                        id="quantity"
                        v-model.number="quantity"
                        class="quantity-input"
                        type="number"
                        min="1"
                        :disabled="isOrderingDisabled"
                        @blur="syncQuantityInput"
                        @change="syncQuantityInput"
                    />
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

            <div
                v-else-if="isLoadingOptions"
                class="product-status product-status--loading"
                role="status"
                aria-live="polite"
            >
                Loading available options for this item...
            </div>

            <div
                v-else-if="isOptionsUnavailable"
                class="product-status product-status--error"
                role="alert"
            >
                Ordering is temporarily unavailable while we reconnect to our product service.
            </div>
        </div>
    </div>

    <div class="details-grid" name="product-customization">
        <div class="customization card">
            <div
                v-if="isOptionsUnavailable"
                class="service-unavailable"
                role="alert"
            >
                <span class="service-unavailable__eyebrow">Service update</span>
                <h3>We&rsquo;re having trouble loading product options right now.</h3>
                <p>
                    Our ordering service is temporarily unavailable, so customization and checkout are paused for this item.
                    Please try again in a few minutes.
                </p>
                <div class="service-unavailable__actions">
                    <button class="secondary" type="button" @click="retryLoadingOptions">
                        Retry
                    </button>
                    <button class="secondary" type="button" @click="goMainPage">
                        Return Home
                    </button>
                </div>
            </div>

            <div
                v-else-if="isLoadingOptions"
                class="service-unavailable service-unavailable--loading"
                role="status"
                aria-live="polite"
            >
                <span class="service-unavailable__eyebrow">Loading options</span>
                <h3>We&rsquo;re preparing your customization choices.</h3>
                <p>
                    Please wait a moment while we load the latest options for this item.
                </p>
            </div>

            <component
                :is="customizationComponent"
                v-else-if="customizationComponent"
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
