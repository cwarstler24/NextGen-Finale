<script setup>
import { useCart } from '../composables/useCart';
import { useRouter } from 'vue-router';

const router = useRouter();
const { cartEntries, cartCount, cartTotal, removeItem, clearCart } = useCart();

function formatCurrency(value) {
    return `$${value.toFixed(2)}`;
}

function formatOptionValue(value) {
    if (Array.isArray(value)) {
        if (value.every((entry) => entry && typeof entry === 'object' && !Array.isArray(entry))) {
            return value.length > 0
                ? value.map((entry) => `${entry.name ?? entry.id} x${entry.quantity ?? 1}`).join(', ')
                : 'None selected';
        }

        return value.length > 0 ? value.join(', ') : 'None selected';
    }

    return value || 'None selected';
}

const purchase = () => {
    router.push({ name: 'checkout' });
};
</script>

<template>
<section class="page cart-page">
    <div class="cart-header">
        <div>
            <h1>Your Cart</h1>
            <p v-if="cartCount > 0">
                {{ cartCount }} item<span v-if="cartCount !== 1">s</span> ready for checkout.
            </p>
        </div>
    </div>

    <div v-if="cartEntries.length === 0" class="card empty-cart">
        <p>Your cart is currently empty. Please add some delicious items to your cart!</p>
    </div>

    <div v-else class="cart-layout">
        <article v-for="item in cartEntries" :key="item.signature" class="card cart-item">
            <img v-if="item.image" :src="item.image" :alt="item.name" class="cart-item-image" />
            <div class="cart-item-content">
                <div class="cart-item-top">
                    <div>
                        <h2>{{ item.name }}</h2>
                        <p>Quantity: {{ item.quantity }}</p>
                    </div>
                    <strong>{{ formatCurrency(item.lineTotal) }}</strong>
                </div>

                <ul class="cart-options">
                    <li v-for="option in item.options" :key="`${item.signature}-${option.name}`">
                        <span>{{ option.name }}:</span> {{ formatOptionValue(option.value) }}
                    </li>
                </ul>

                <button class="secondary remove-button" type="button" @click="removeItem(item.signature)">
                    Remove
                </button>
            </div>
        </article>

        <aside class="card cart-summary">
            <h2>Summary</h2>
            <div class="summary-row">
                <span>Items</span>
                <span>{{ cartCount }}</span>
            </div>
            <div class="summary-row total-row">
                <span>Total</span>
                <strong>{{ formatCurrency(cartTotal) }}</strong>
            </div>
            <button class="primary purchase-button" type="button" @click="purchase">
                Checkout
            </button>
            <button v-if="cartCount > 0" class="secondary" type="button" @click="clearCart">
                Clear Cart
            </button>
        </aside>
    </div>
</section>
</template>

<style src="../styles/mainview.css" scoped></style>
<style src="../styles/CartView.css" scoped></style>
