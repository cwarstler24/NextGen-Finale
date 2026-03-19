<script setup>
import { computed } from 'vue';
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

const estimatedMinutes = Math.floor(Math.random() * 11) + 15;

const estimatedReadyTime = computed(() => {
    const ready = new Date(Date.now() + estimatedMinutes * 60_000);
    return ready.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
});

const progressSteps = [
    { label: 'Order Placed', icon: '✓', active: true },
    { label: 'Preparing', icon: '🧅', active: true },
    { label: 'Grilling', icon: '🔥', active: false },
    { label: 'Ready for Pickup', icon: '🛍️', active: false },
];

function goHome() {
    router.push({ name: 'main' });
}
</script>

<template>
<section v-if="orderId !== null" class="page confirmation-page">
    <div class="card confirmation-hero">
        <div class="hero-icon">
            🎉
        </div>
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
        <div class="detail-row">
            <span>Estimated Ready</span>
            <strong>{{ estimatedReadyTime }} (~{{ estimatedMinutes }} min)</strong>
        </div>
    </div>

    <div class="card progress-card">
        <h2>Order Progress</h2>
        <div class="progress-tracker">
            <div class="progress-line">
                <div
                    class="progress-fill"
                    :style="{ width: `${(progressSteps.filter(s => s.active).length - 1) / (progressSteps.length - 1) * 100}%` }"
                ></div>
            </div>
            <div class="progress-steps">
                <div
                    v-for="(step, index) in progressSteps"
                    :key="index"
                    class="progress-step"
                    :class="{ active: step.active }"
                >
                    <div class="step-dot">
                        <span v-if="step.active">{{ step.icon }}</span>
                        <span v-else class="step-number">{{ index + 1 }}</span>
                    </div>
                    <span class="step-label">{{ step.label }}</span>
                </div>
            </div>
        </div>
    </div>

    <button class="primary back-home-button" type="button" @click="goHome">
        Back to Home
    </button>
</section>
</template>

<style src="../styles/ConfirmationView.css" scoped></style>
<style src="../styles/mainview.css" scoped></style>
