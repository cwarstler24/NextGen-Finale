<script setup>
import { useCart } from './composables/useCart';

const { cartCount } = useCart();
</script>

<template>
<div class="app-shell">
    <nav class="top-nav">
        <span class="brand">
            <img src="/images/Logo.jpg" style="width: 3em" alt="Logo" class="brand-icon" />
            <RouterLink to="/" class="brand-name"> The Frying Saucer </RouterLink>
        </span>
        <div class="nav-links">
            <RouterLink to="/product/Burger">
                Burger
            </RouterLink>
            <RouterLink to="/product/Fries">
                Fries
            </RouterLink>
            <RouterLink to="/cart" class="cart-link">
                <span>Cart</span>
                <span v-if="cartCount > 0" class="cart-badge">{{ cartCount }}</span>
                <img src="/images/burger_bag.png" alt="Cart" class="cart-icon" />
            </RouterLink>
        </div>
    </nav>

    <main class="content">
        <RouterView />
    </main>
</div>
</template>

<style scoped>
.brand {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.brand-icon {
    vertical-align: middle;
    flex-shrink: 0;
}

.cart-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    background-color: rgba(255, 255, 255, 0.12);
}

.cart-icon {
    width: 1.5em;
    flex-shrink: 0;
}

.cart-badge {
    min-width: 1.5rem;
    padding: 0.1rem 0.4rem;
    border-radius: 999px;
    background: #ffffff;
    color: #000000;
    font-size: 0.85rem;
    font-weight: 700;
    text-align: center;
}
</style>
