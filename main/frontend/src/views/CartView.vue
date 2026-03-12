<script setup>
import { useCart } from '../composables/useCart';

const { cartEntries, cartCount, cartTotal, removeItem, clearCart } = useCart();

function formatCurrency(value) {
    return `$${value.toFixed(2)}`;
}

function formatOptionValue(value) {
    if (Array.isArray(value)) {
        return value.length > 0 ? value.join(', ') : 'None selected';
    }

    return value || 'None selected';
}
</script>

<template>
<section class="page cart-page">
    <div class="cart-header">
        <div>
            <h1>Your Cart</h1>
            <p v-if="cartCount > 0">{{ cartCount }} item<span v-if="cartCount !== 1">s</span> ready for checkout.</p>
        </div>
        <button v-if="cartCount > 0" class="secondary" type="button" @click="clearCart">
            Clear Cart
        </button>
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
        </aside>
    </div>
</section>
</template>

<style src="../styles/mainview.css" scoped></style>
<style scoped>
.cart-page {
    display: grid;
    gap: 1.5rem;
}

.cart-header,
.cart-item-top,
.summary-row {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
}

.cart-header {
    align-items: center;
}

.cart-layout {
    display: grid;
    gap: 1rem;
}

.cart-item {
    display: grid;
    grid-template-columns: minmax(120px, 160px) 1fr;
    gap: 1rem;
    align-items: start;
}

.cart-item-image {
    width: 100%;
    border-radius: 0.75rem;
    object-fit: cover;
}

.cart-item-content,
.cart-options,
.cart-summary,
.empty-cart {
    display: grid;
    gap: 0.75rem;
}

.cart-options {
    padding-left: 1rem;
    margin: 0;
}

.total-row {
    padding-top: 0.75rem;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.remove-button {
    justify-self: start;
}

@media (max-width: 700px) {
    .cart-header,
    .cart-item,
    .cart-item-top {
        grid-template-columns: 1fr;
        display: grid;
    }
}
</style>
