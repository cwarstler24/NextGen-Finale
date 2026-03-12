<script setup>
import { watch } from 'vue';
import { useCart } from '../composables/useCart';
import { useRouter } from 'vue-router';

const router = useRouter();
const { cartEntries, cartTotal, clearCart } = useCart();

function formatCurrency(value) {
    return `$${value.toFixed(2)}`;
}

const purchase = () => {
    // TODO Implement with API
    if (validateUserData()) {
        alert('Purchase successful! Thank you for your order.');
        clearCart();
        router.push({ name: 'home' });
    } else {
        alert('Please fill in all required fields before checking out.');
    }
};

const emptyCart = () => {
    if (confirm('Are you sure you want to clear your cart?')) {
        clearCart();
        router.push({ name: 'home' });
    }
};


watch(
    () => cartEntries.value.length,
    (count) => {
        if (count === 0) {
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

const userData = {
    name: '',
    email: '',
    shipping_address: '',
    billing_address: '',
};

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
        <form @submit.prevent="purchase" class="checkout-form">
            <div class="form-group">
                <div class="input">
                    <label for="name">Name: </label>
                    <input v-model="userData.name" type="text" id="name" required />
                </div>
                <div class="input">
                    <label for="email">Email: </label>
                    <input v-model="userData.email" type="email" id="email" required />
                </div>
                <div class="input">
                    <label for="shipping_address">Shipping Address: </label>
                    <input v-model="userData.shipping_address" type="text" id="shipping_address" required />
                </div>
                <div class="input">
                    <label for="billing_address">Billing Address: </label>
                    <input v-model="userData.billing_address" type="text" id="billing_address" required />
                </div>
            </div>

            <div class="checkout-actions">
                <button class="secondary" type="button" @click="emptyCart" :disabled="cartEntries.length === 0">
                    Clear Cart
                </button>
                <button class="primary" type="submit" :disabled="cartEntries.length === 0">
                    Checkout
                </button>
            </div>
        </form>
    </div>
</section>
</template>

<style src="../styles/CheckoutView.css" scoped></style>
<style src="../styles/mainview.css" scoped></style>
