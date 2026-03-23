<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const orderId = history.state?.orderId ?? null;
const totalPrice = history.state?.totalPrice ?? 0;
const customerName = history.state?.customerName ?? 'Customer';

if (orderId === null) {
    router.replace({ name: 'main' });
}

function formatCurrency(value) {
    return `$${Number(value).toFixed(2)}`;
}

function goHome() {
    router.push({ name: 'main' });
}
</script>

<template>
<section v-if="orderId !== null" class="page confirmation-page">
    <div class="card confirmation-hero">
        <h1>Order Confirmed!</h1>
        <p class="hero-subtitle">
            Thanks, <strong>{{ customerName }}</strong>! Your order has been placed and is being prepared.
        </p>
    </div>

    <div class="card order-details-card">
        <div class="detail-row">
            <span>Order Number</span>
            <strong>#{{ orderId }}</strong>
        </div>
        <div class="detail-row">
            <span>Total</span>
            <strong>{{ formatCurrency(totalPrice) }}</strong>
        </div>
    </div>

    <button class="primary back-home-button" type="button" @click="goHome">
        Back to Home
    </button>
</section>
</template>

<style src="../styles/ConfirmationView.css" scoped></style>
<style src="../styles/mainview.css" scoped></style>
