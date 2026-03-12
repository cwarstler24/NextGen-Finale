<script setup>
import { useCart } from './composables/useCart';

const { cartCount } = useCart();
const currentYear = new Date().getFullYear();

const documentation = () => {
    alert('Documentation is currently unavailable. Please check back later!');
};
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
    <footer class="footer">
        <span>&copy; {{ currentYear }} The Frying Saucer. All rights reserved.</span>
        <span class="hover" @click="documentation"> Documentation</span>
    </footer>
</div>
</template>

<style scoped>
.app-shell {
    min-height: 100dvh;
    padding-bottom: 4.5rem;
}

.content {
    flex: 1;
}

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

.footer {
    position: fixed;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 10;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 0.75rem 1.5rem;
    padding: 1.5rem 3rem;
    background: #ffffff;
    box-shadow: 0 -12px 30px rgba(15, 23, 42, 0.08);
    color: #475569;
    font-size: 0.9rem;
    font-weight: 500;
    text-align: center;
}

.footer span {
    display: inline-flex;
    align-items: center;
}

.footer span + span {
    padding-left: 1.5rem;
    border-left: 1px solid rgba(71, 85, 105, 0.25);
}

@media (max-width: 720px) {
    .app-shell {
        padding-bottom: 4rem;
    }

    .footer {
        padding: 1.5rem;
    }

    .footer span + span {
        padding-left: 0.75rem;
    }
}
</style>
