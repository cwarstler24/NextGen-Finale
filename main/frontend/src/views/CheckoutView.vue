<script setup>
import { reactive, ref, watch } from 'vue';
import { useCart } from '../composables/useCart';
import { useRouter } from 'vue-router';
import { buildApiUrl } from '../config/runtimeConfig';

const ORDER_ENDPOINT = buildApiUrl('/Order/');

const router = useRouter();
const { cartEntries, cartTotal, clearCart } = useCart();
const isSubmitting = ref(false);
const isOrderComplete = ref(false);

function formatCurrency(value) {
    return `$${value.toFixed(2)}`;
}

function parseOptionIds(rawValue, optionLabel, itemName) {
    const values = Array.isArray(rawValue) ? rawValue : [rawValue];
    const parsedIds = values
        .filter((value) => value !== null && value !== undefined && value !== '')
        .map((value) => Number.parseInt(value, 10));

    if (parsedIds.some((value) => !Number.isInteger(value))) {
        throw new Error(`Invalid ${optionLabel} selection for ${itemName}.`);
    }

    return parsedIds;
}

function parseToppingSelections(rawValue, itemName) {
    if (!Array.isArray(rawValue)) {
        throw new Error(`Invalid topping selection for ${itemName}.`);
    }

    return rawValue.map((entry) => {
        const parsedId = Number.parseInt(entry?.id, 10);
        const parsedQuantity = Number.parseInt(entry?.quantity, 10);

        if (!Number.isInteger(parsedId) || !Number.isInteger(parsedQuantity) || parsedQuantity < 1) {
            throw new Error(`Invalid topping selection for ${itemName}.`);
        }

        return {
            topping_id: parsedId,
            count: parsedQuantity,
        };
    });
}

function parseSingleQuantitySelection(rawValue, optionLabel, itemName) {
    if (!Array.isArray(rawValue) || rawValue.length !== 1) {
        throw new Error(`Invalid ${optionLabel} selection for ${itemName}.`);
    }

    const parsedQuantity = Number.parseInt(rawValue[0]?.quantity, 10);
    if (!Number.isInteger(parsedQuantity) || parsedQuantity < 1) {
        throw new Error(`Invalid ${optionLabel} quantity for ${itemName}.`);
    }

    return parsedQuantity;
}

function getOption(item, optionName) {
    return item.options.find((option) => option.name.toLowerCase() === optionName.toLowerCase());
}

function formatApiErrorDetail(detail) {
    if (typeof detail === 'string' && detail.trim() !== '') {
        return detail;
    }

    if (Array.isArray(detail)) {
        const messages = detail
            .map((entry) => {
                if (typeof entry === 'string' && entry.trim() !== '') {
                    return entry;
                }

                if (!entry || typeof entry !== 'object') {
                    return null;
                }

                const fieldPath = Array.isArray(entry.loc)
                    ? entry.loc
                        .filter((segment) => typeof segment === 'string' || typeof segment === 'number')
                        .slice(1)
                        .join('.')
                    : '';
                const message = typeof entry.msg === 'string' && entry.msg.trim() !== ''
                    ? entry.msg
                    : JSON.stringify(entry);

                return fieldPath ? `${fieldPath}: ${message}` : message;
            })
            .filter((message) => typeof message === 'string' && message.trim() !== '');

        return messages.length > 0 ? messages.join('; ') : null;
    }

    if (detail && typeof detail === 'object') {
        if (typeof detail.message === 'string' && detail.message.trim() !== '') {
            return detail.message;
        }

        return JSON.stringify(detail);
    }

    return null;
}

function getResponseErrorMessage(responseData, fallbackMessage) {
    return formatApiErrorDetail(responseData?.detail)
        ?? formatApiErrorDetail(responseData?.message)
        ?? fallbackMessage;
}

function buildOrderPayload() {
    const burgers = [];
    const fries = [];

    for (const item of cartEntries.value) {
        if (item.id !== 'burger' && item.id !== 'fries') {
            continue;
        }

        for (let itemCount = 0; itemCount < item.quantity; itemCount += 1) {
            if (item.id === 'burger') {
                const bunIds = parseOptionIds(getOption(item, 'Bun')?.id, 'bun', item.name);
                const pattyIds = parseOptionIds(getOption(item, 'Patty')?.id, 'patty', item.name);
                const toppingIds = parseToppingSelections(getOption(item, 'Toppings')?.id ?? [], item.name);
                const pattyCount = parseSingleQuantitySelection(getOption(item, 'Patty')?.value, 'patty', item.name);

                if (bunIds.length !== 1 || pattyIds.length !== 1) {
                    throw new Error(`Burger selections are incomplete for ${item.name}.`);
                }

                burgers.push({
                    bun_id: bunIds[0],
                    patty_id: pattyIds[0],
                    toppings: toppingIds,
                    patty_count: pattyCount,
                });
                continue;
            }

            const sizeIds = parseOptionIds(getOption(item, 'Size')?.id, 'size', item.name);
            const typeIds = parseOptionIds(getOption(item, 'Type')?.id, 'type', item.name);
            const seasoningIds = parseOptionIds(getOption(item, 'Seasoning')?.id, 'seasoning', item.name);

            if (sizeIds.length !== 1 || typeIds.length !== 1 || seasoningIds.length !== 1) {
                throw new Error(`Fries selections are incomplete for ${item.name}. Please update your cart and try again.`);
            }

            fries.push({
                size_id: sizeIds[0],
                type_id: typeIds[0],
                seasoning_id: seasoningIds[0],
            });
        }
    }

    return {
        customer: {
            name: userData.name.trim(),
            email: userData.email.trim(),
            shipping_address: userData.shipping_address.trim(),
            billing_address: userData.billing_address.trim(),
        },
        burgers,
        fries,
        date: new Date().toISOString(),
    };
}

const purchase = async () => {
    if (!validateUserData()) {
        alert('Please fill in all required fields before checking out.');
        return;
    }

    if (isSubmitting.value) {
        return;
    }

    try {
        isSubmitting.value = true;

        const response = await fetch(ORDER_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(buildOrderPayload()),
        });

        const responseData = await response.json().catch(() => null);
        if (!response.ok) {
            throw new Error(getResponseErrorMessage(
                responseData,
                `Checkout failed: ${response.status} ${response.statusText}`
            ));
        }

        const orderSummary = {
            orderId: responseData?.order_id ?? null,
            totalPrice: responseData?.total_price ?? cartTotal.value,
            customerName: userData.name.trim(),
        };

        isOrderComplete.value = true;
        clearCart();
        router.push({ name: 'confirm', state: orderSummary });
    } catch (error) {
        console.error('Unable to place order');
        alert(error instanceof Error ? error.message : 'Unable to place order.');
    } finally {
        isSubmitting.value = false;
    }
};

const emptyCart = () => {
    if (confirm('Are you sure you want to clear your cart?')) {
        clearCart();
        router.push({ name: 'main' });
    }
};


watch(
    () => cartEntries.value.length,
    (count) => {
        if (count === 0 && !isOrderComplete.value) {
            router.replace({ name: 'cart' });
        }
    },
    { immediate: true }
);

const validateUserData = () => {
    return (
        userData.name.trim() !== '' &&
        userData.email.trim() !== '' &&
        userData.shipping_address.trim() !== '' &&
        userData.billing_address.trim() !== ''
    );
};

const userData = reactive({
    name: '',
    email: '',
    shipping_address: '',
    billing_address: '',
});

</script>

<template>
<section class="page checkout-page">
    <div name="orderSummary" class="card checkout-summary">
        <h1>Order Summary</h1>
        <div v-if="cartEntries.length === 0">
            <p>Your cart is empty. Please add some items to your cart before checking out.</p>
        </div>
        <div v-else class="order-summary-content">
            <ul class="order-items">
                <li v-for="item in cartEntries" :key="item.signature" class="order-item">
                    <div class="order-item-info">
                        <h2>{{ item.name }}</h2>
                        <p>Quantity: {{ item.quantity }}</p>
                    </div>
                    <strong>{{ formatCurrency(item.lineTotal) }}</strong>
                </li>
            </ul>
            <div class="order-total">
                <span>Total</span>
                <strong>{{ formatCurrency(cartTotal) }}</strong>
            </div>
        </div>
    </div>

    <div name="userData" class="card checkout-customer">
        <h1>Customer Information</h1>
        <form class="checkout_form" @submit.prevent="purchase">
            <div class="form-group">
                <div class="input">
                    <label for="name">Name: </label>
                    <input v-model="userData.name" type="text" required />
                </div>
                <div class="input">
                    <label for="email">Email: </label>
                    <input v-model="userData.email" type="email" required />
                </div>
                <div class="input">
                    <label for="shipping_address">Shipping Address: </label>
                    <input v-model="userData.shipping_address" type="text" required />
                </div>
                <div class="input">
                    <label for="billing_address">Billing Address: </label>
                    <input v-model="userData.billing_address" type="text" required />
                </div>
            </div>

            <div class="checkout-actions">
                <button class="primary" type="submit" :disabled="cartEntries.length === 0 || isSubmitting">
                    {{ isSubmitting ? 'Submitting...' : 'Checkout' }}
                </button>
                <button class="secondary" type="button" :disabled="cartEntries.length === 0 || isSubmitting" @click="emptyCart">
                    Clear
                </button>
            </div>
        </form>
    </div>
</section>
</template>

<style src="../styles/CheckoutView.css" scoped></style>
<style src="../styles/mainview.css" scoped></style>
