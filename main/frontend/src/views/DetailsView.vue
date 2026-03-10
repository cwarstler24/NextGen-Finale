<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.push({ name: 'home' })
}
</script>

<template>
  <section class="page">
    <header class="hero">
      <p class="eyebrow">Demo Page</p>
      <h1>Details</h1>
      <p class="subtitle">
        You made it! This page demonstrates simple navigation with Vue Router.
      </p>
    </header>

    <div class="card">
      <h2>What’s next?</h2>
      <ul class="list">
        <li>Swap this copy for your own demo content.</li>
        <li>Add more menu items as the app grows.</li>
        <li>Style it however you like.</li>
      </ul>
      <button class="secondary" type="button" @click="goBack">
        Back to Main Menu
      </button>
    </div>
  </section>
</template>
