<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToDetails = () => {
    router.push({ name: 'details' })
}
</script>

<template>
<section class="page">
    <header class="hero">
        <p class="eyebrow">
            Demo Menu
        </p>
        <h1>Main Menu</h1>
        <p class="subtitle">
            Welcome to the Vue demo app. Pick the button below to continue.
        </p>
    </header>

    <div class="card">
        <h2>Quick Start</h2>
        <p>Clicking this button takes you to the second page.</p>
        <button class="primary" type="button" @click="goToDetails">
            Go to the Details Page
        </button>
    </div>
</section>
</template>
