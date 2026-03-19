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
            <RouterLink to="/user" class="nav-pill">
                User
            </RouterLink>
            <RouterLink to="/product/Burger" class="nav-pill">
                Burger
            </RouterLink>
            <RouterLink to="/product/Fries" class="nav-pill">
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
    isolation: isolate;
}

.app-shell::before,
.app-shell::after {
    content: '';
    position: fixed;
    z-index: -1;
    border-radius: 999px;
    filter: blur(10px);
    pointer-events: none;
}

.app-shell::before {
    top: 6rem;
    left: -6rem;
    width: 18rem;
    height: 18rem;
    background: radial-gradient(circle, rgba(255, 191, 94, 0.24) 0%, transparent 70%);
}

.app-shell::after {
    right: -5rem;
    bottom: 5rem;
    width: 20rem;
    height: 20rem;
    background: radial-gradient(circle, rgba(180, 78, 41, 0.16) 0%, transparent 72%);
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
    width: 3.15rem;
    height: 3.15rem;
    padding: 0.2rem;
    border-radius: 1rem;
    background: rgba(255, 249, 241, 0.12);
    border: 1px solid rgba(255, 234, 215, 0.16);
    box-shadow: 0 12px 24px rgba(17, 9, 6, 0.18);
}

.brand-name {
    font-size: 1.12rem;
    letter-spacing: 0.02em;
}

.nav-pill,
.cart-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 0.95rem;
    border-radius: 999px;
    background: rgba(255, 248, 238, 0.08);
    border: 1px solid rgba(255, 233, 211, 0.12);
    transition: background-color 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
}

.nav-pill:hover,
.cart-link:hover {
    background: rgba(255, 248, 238, 0.14);
    border-color: rgba(255, 221, 187, 0.22);
    transform: translateY(-2px);
}

.nav-pill.router-link-active,
.cart-link.router-link-active {
    background: linear-gradient(135deg, rgba(201, 105, 44, 0.98) 0%, rgba(168, 79, 31, 0.98) 100%);
    border-color: rgba(255, 228, 201, 0.18);
    color: #fffaf4;
    box-shadow: 0 14px 24px rgba(169, 79, 31, 0.22);
}

.cart-icon {
    width: 1.55em;
    flex-shrink: 0;
}

.cart-badge {
    min-width: 1.5rem;
    padding: 0.1rem 0.4rem;
    border-radius: 999px;
    background: rgba(255, 247, 239, 0.95);
    color: #7c3918;
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
    background: rgba(255, 251, 245, 0.9);
    border-top: 1px solid rgba(92, 58, 39, 0.12);
    box-shadow: 0 -12px 36px rgba(58, 31, 17, 0.12);
    backdrop-filter: blur(14px);
    color: #715847;
    font-size: 0.9rem;
    font-weight: 600;
    text-align: center;
}

.footer span {
    display: inline-flex;
    align-items: center;
}

.footer span + span {
    padding-left: 1.5rem;
    border-left: 1px solid rgba(113, 88, 71, 0.22);
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
