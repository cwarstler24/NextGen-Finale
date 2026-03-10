<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
    <section class="page">
        <header class="hero">
            <p class="eyebrow">Demo Menu</p>
            <h1>Burger</h1>
            <p class="subtitle">
                Welcome to the Vue demo app. This is the burger page.
            </p>
        </header>

        <div class="card">
            <h2>Burger</h2>
            <p>This page is all about burger.</p>
        </div>
    </section>
</template>
