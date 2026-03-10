<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
    <section class="page">
        <header class="hero">
            <p class="eyebrow">Demo Menu</p>
            <h1>Fries</h1>
            <p class="subtitle">
                Welcome to the Vue demo app. This is the fries page.
            </p>
        </header>

        <div class="card">
            <h2>Fries</h2>
            <p>This page is all about fries.</p>
        </div>
    </section>
</template>
