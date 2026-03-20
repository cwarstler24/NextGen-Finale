<script setup>
import { computed, ref } from 'vue';
import BurgerImage from '../components/BurgerImage.vue';
import {
    supportedBurgerBuns,
    supportedBurgerPatties,
    supportedBurgerToppings,
} from '../data/burgerImageCatalog';

const USER_ENDPOINT_BASE = 'http://localhost:8000/Customer';
const FRIES_TYPE_IMAGE_MAP = {
    shoestring: '/images/items/shoestring_fries.PNG',
    waffle: '/images/items/waffle_fries.png',
    curly: '/images/items/curly_fries.png',
    steak: '/images/items/steak_fries.png',
    'sweet potato': '/images/items/sweet_potato_fries.png',
};
const BURGER_NAME_SEPARATOR = ' with ';
const BURGER_TOPPINGS_SEPARATOR = ' and ';
const DEFAULT_FRIES_IMAGE = '/images/Fries1.png';
const supportedBurgerBunNames = [...supportedBurgerBuns];
const supportedBurgerPattyNames = [...supportedBurgerPatties];
const supportedBurgerToppingNames = [...supportedBurgerToppings]
    .filter((name) => name !== 'None')
    .sort((left, right) => right.length - left.length);

const currencyFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
});

const orderDateFormatter = new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
});

const email = ref('');
const user = ref(null);
const errorMessage = ref('');
const isLoading = ref(false);

function formatCurrency(value) {
    return currencyFormatter.format(Number(value) || 0);
}

function formatOrderDate(value) {
    const parsedDate = new Date(value);

    if (Number.isNaN(parsedDate.getTime())) {
        return value;
    }

    return orderDateFormatter.format(parsedDate);
}

function formatItemCount(count) {
    return `${count} item${count === 1 ? '' : 's'}`;
}

function normalizeQuantity(value) {
    return Math.max(1, Number.parseInt(value ?? 1, 10) || 1);
}

function parseBurgerImageProps(name) {
    if (typeof name !== 'string' || !name.includes(BURGER_NAME_SEPARATOR)) {
        return null;
    }

    const separatorIndex = name.indexOf(BURGER_NAME_SEPARATOR);
    const bunName = name.slice(0, separatorIndex).trim();

    if (!supportedBurgerBunNames.includes(bunName)) {
        return null;
    }

    const configurationText = name.slice(separatorIndex + BURGER_NAME_SEPARATOR.length).trim();
    const toppingsSeparatorIndex = configurationText.indexOf(BURGER_TOPPINGS_SEPARATOR);
    const pattyText = toppingsSeparatorIndex >= 0
        ? configurationText.slice(0, toppingsSeparatorIndex).trim()
        : configurationText;
    const toppingsText = toppingsSeparatorIndex >= 0
        ? configurationText.slice(toppingsSeparatorIndex + BURGER_TOPPINGS_SEPARATOR.length).trim()
        : '';

    const pattyMatch = pattyText.match(/^(\d+)\s+(.+)$/);
    const pattyQuantity = normalizeQuantity(pattyMatch?.[1] ?? 1);
    const pattyName = (pattyMatch?.[2] ?? pattyText).trim();

    if (!supportedBurgerPattyNames.includes(pattyName)) {
        return null;
    }

    const selectedToppings = toppingsText
        ? toppingsText
            .split(', ')
            .map((entry) => entry.trim())
            .filter((entry) => supportedBurgerToppingNames.includes(entry))
            .map((entry) => ({ name: entry, quantity: 1 }))
        : [];

    return {
        selectedBun: { name: bunName },
        selectedPatty: {
            name: pattyName,
            quantity: pattyQuantity,
        },
        selectedToppings,
    };
}

function getFriesImageSource(name) {
    if (typeof name !== 'string' || name.trim() === '') {
        return DEFAULT_FRIES_IMAGE;
    }

    const normalizedName = name.trim().toLowerCase();
    const friesTypeMatch = normalizedName.match(/^\d+(?:\.\d+)?oz\s+(.+?)\s+with\s+.+$/i);
    const friesTypeName = friesTypeMatch?.[1]?.trim() ?? '';

    return FRIES_TYPE_IMAGE_MAP[friesTypeName] ?? DEFAULT_FRIES_IMAGE;
}

function getOrderItemVisualData(itemType, name) {
    const normalizedItemType = typeof itemType === 'string' ? itemType.trim().toLowerCase() : '';

    if (normalizedItemType === 'burger') {
        return {
            burgerImageProps: parseBurgerImageProps(name),
            imageSrc: '',
            imageAlt: '',
        };
    }

    if (normalizedItemType === 'fries') {
        return {
            burgerImageProps: null,
            imageSrc: getFriesImageSource(name),
            imageAlt: `${name || 'Fries'} image`,
        };
    }

    return {
        burgerImageProps: null,
        imageSrc: '',
        imageAlt: '',
    };
}

function normalizeOrderItem(item) {
    const itemType = typeof item?.item_type === 'string' && item.item_type.trim() !== ''
        ? item.item_type
        : 'Item';
    const name = typeof item?.name === 'string' && item.name.trim() !== ''
        ? item.name
        : 'Unnamed item';
    const unitPrice = Number(item?.price) || 0;
    const visualData = getOrderItemVisualData(itemType, name);

    return {
        item_type: itemType,
        name,
        unitPrice,
        price: unitPrice,
        quantity: normalizeQuantity(item?.quantity),
        ...visualData,
    };
}

function getOrderItemGroupKey(item) {
    return [
        item.item_type.trim().toLowerCase(),
        item.name.trim().toLowerCase(),
        item.unitPrice.toFixed(2),
    ].join('::');
}

function aggregateOrderItems(items) {
    const groupedItems = new Map();

    items.forEach((item) => {
        const normalizedItem = normalizeOrderItem(item);
        const groupKey = getOrderItemGroupKey(normalizedItem);
        const existingItem = groupedItems.get(groupKey);

        if (existingItem) {
            existingItem.quantity += normalizedItem.quantity;
            existingItem.price += normalizedItem.unitPrice * normalizedItem.quantity;
            return;
        }

        groupedItems.set(groupKey, {
            ...normalizedItem,
            groupKey,
            price: normalizedItem.unitPrice * normalizedItem.quantity,
        });
    });

    return [...groupedItems.values()];
}

const orders = computed(() => {
    const userOrders = Array.isArray(user.value?.orders) ? user.value.orders : [];

    return userOrders
        .map((order, index) => {
            const items = Array.isArray(order?.items)
                ? aggregateOrderItems(order.items)
                : [];
            const parsedDate = new Date(order?.date);
            const sortTimestamp = Number.isNaN(parsedDate.getTime()) ? 0 : parsedDate.getTime();
            const orderId = Number.isInteger(order?.order_id)
                ? order.order_id
                : null;

            return {
                orderKey: orderId !== null ? `order-${orderId}` : `order-${index}-${order?.date ?? 'unknown'}`,
                orderIdLabel: orderId !== null ? `Order #${orderId}` : `Order ${index + 1}`,
                date: order?.date ?? '',
                displayDate: formatOrderDate(order?.date ?? ''),
                price: Number(order?.price) || 0,
                items,
                itemCount: items.reduce((total, item) => total + item.quantity, 0),
                sortTimestamp,
            };
        })
        .sort((left, right) => right.sortTimestamp - left.sortTimestamp);
});

const totalSpent = computed(() => {
    return orders.value.reduce((runningTotal, order) => runningTotal + (Number(order.price) || 0), 0);
});

const averageOrderValue = computed(() => {
    if (orders.value.length === 0) {
        return 0;
    }

    return totalSpent.value / orders.value.length;
});

const latestOrderDate = computed(() => {
    const latestOrder = orders.value[0];
    return latestOrder ? formatOrderDate(latestOrder.date) : 'No orders yet';
});

async function getUser() {
    const trimmedEmail = email.value.trim();

    if (!trimmedEmail) {
        errorMessage.value = 'Please enter an email address.';
        user.value = null;
        return;
    }

    errorMessage.value = '';
    isLoading.value = true;

    try {
        const response = await fetch(`${USER_ENDPOINT_BASE}/${encodeURIComponent(trimmedEmail)}`);
        const responseData = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(
                responseData?.detail
                    ?? responseData?.message
                    ?? `Failed to fetch user data: ${response.status} ${response.statusText}`
            );
        }

        user.value = {
            ...responseData,
            orders: Array.isArray(responseData?.orders) ? responseData.orders : [],
        };
    } catch (error) {
        user.value = null;
        errorMessage.value = error instanceof Error ? error.message : 'Unable to load user data.';
    } finally {
        isLoading.value = false;
    }
}
</script>

<template>
<section class="page user-page">
    <header class="card user-hero">
        <div class="eyebrow">
            Account Lookup
        </div>
        <div class="hero-copy">
            <h1>User Profile</h1>
            <p class="subtitle">
                Search by email to view customer details, saved addresses, and recent orders.
            </p>
        </div>
    </header>

    <form class="card lookup-card" @submit.prevent="getUser">
        <div class="lookup-copy">
            <h2>Find a customer</h2>
            <p>Enter the email tied to an order to load profile information from the API.</p>
        </div>

        <div class="lookup-controls">
            <label class="input-group" for="email">
                <span>Email address</span>
                <input
                    id="email"
                    v-model="email"
                    type="email"
                    name="email"
                    autocomplete="email"
                    placeholder="name@example.com"
                />
            </label>
            <button class="primary" type="submit" :disabled="isLoading">
                {{ isLoading ? 'Loading...' : 'Fetch User Data' }}
            </button>
        </div>

        <p v-if="errorMessage" class="status-message error-message" role="alert">
            {{ errorMessage }}
        </p>
    </form>

    <template v-if="user">
        <section class="user-content">
            <article class="card profile-card">
                <div class="profile-header">
                    <div>
                        <div class="eyebrow">
                            Customer Profile
                        </div>
                        <h2>{{ user.name }}</h2>
                        <p class="profile-email">
                            {{ user.email }}
                        </p>
                    </div>
                    <div class="profile-badge">
                        {{ orders.length }} order<span v-if="orders.length !== 1">s</span>
                    </div>
                </div>

                <div class="stat-grid">
                    <div class="stat-tile">
                        <span>Total spent</span>
                        <strong>{{ formatCurrency(totalSpent) }}</strong>
                    </div>
                    <div class="stat-tile">
                        <span>Average order</span>
                        <strong>{{ formatCurrency(averageOrderValue) }}</strong>
                    </div>
                    <div class="stat-tile">
                        <span>Latest order</span>
                        <strong>{{ latestOrderDate }}</strong>
                    </div>
                </div>
            </article>

            <section class="address-grid">
                <article class="card address-card">
                    <div class="eyebrow">
                        Shipping
                    </div>
                    <h2>Shipping Address</h2>
                    <p>{{ user.shipping_address }}</p>
                </article>

                <article class="card address-card">
                    <div class="eyebrow">
                        Billing
                    </div>
                    <h2>Billing Address</h2>
                    <p>{{ user.billing_address }}</p>
                </article>
            </section>

            <article class="card orders-card">
                <div class="orders-header">
                    <div>
                        <div class="eyebrow">
                            Order History
                        </div>
                        <h2>Recent Orders</h2>
                    </div>
                    <strong class="orders-total">{{ formatCurrency(totalSpent) }}</strong>
                </div>

                <div v-if="orders.length === 0" class="empty-state">
                    <p>This customer has not placed any orders yet.</p>
                </div>

                <ul v-else class="orders-list">
                    <li
                        v-for="order in orders"
                        :key="order.orderKey"
                        class="orders-list-item"
                    >
                        <details class="order-card" :open="orders.length === 1">
                            <summary class="order-summary">
                                <div class="order-summary-main">
                                    <div class="order-summary-topline">
                                        <strong>{{ order.orderIdLabel }}</strong>
                                        <span class="order-item-count">{{ formatItemCount(order.itemCount) }}</span>
                                    </div>
                                    <p>{{ order.displayDate }}</p>
                                </div>
                                <div class="order-summary-side">
                                    <strong class="order-price">{{ formatCurrency(order.price) }}</strong>
                                    <span class="order-summary-toggle">View items</span>
                                </div>
                            </summary>

                            <div class="order-details">
                                <ul v-if="order.items.length > 0" class="order-items-list">
                                    <li
                                        v-for="(item, itemIndex) in order.items"
                                        :key="`${order.orderKey}-item-${item.groupKey}-${itemIndex}`"
                                        class="order-item-row"
                                    >
                                        <div
                                            v-if="item.burgerImageProps || item.imageSrc"
                                            class="order-item-image-preview"
                                        >
                                            <BurgerImage
                                                v-if="item.burgerImageProps"
                                                v-bind="item.burgerImageProps"
                                            />
                                            <img
                                                v-else-if="item.imageSrc"
                                                :src="item.imageSrc"
                                                :alt="item.imageAlt"
                                                class="order-item-image"
                                            />
                                        </div>
                                        <div class="order-item-copy">
                                            <span class="item-type-badge">{{ item.item_type }}</span>
                                            <div class="order-item-name-row">
                                                <p class="order-item-name">
                                                    {{ item.name }}
                                                </p>
                                                <span v-if="item.quantity > 1" class="item-quantity-badge">
                                                    Qty {{ item.quantity }}
                                                </span>
                                            </div>
                                        </div>
                                        <strong class="order-item-price">{{ formatCurrency(item.price) }}</strong>
                                    </li>
                                </ul>

                                <p v-else class="order-items-empty">
                                    No item details were returned for this order.
                                </p>
                            </div>
                        </details>
                    </li>
                </ul>
            </article>
        </section>
    </template>
</section>
</template>

<style src="../styles/mainview.css" scoped></style>
<style src="../styles/UserView.css" scoped></style>
