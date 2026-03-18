<script setup>
import { useRouter } from 'vue-router'
import customBurger from '../data/customBurgers.js';
const router = useRouter()

const goToBurgerPage = () => {
    router.push({ name: 'product' , params: { product: 'Burger' }})
}
</script>

<template>
<div class="page">
    <div class="card" @click="goToBurgerPage">
        <h2>Custom Burger Menu</h2>
        <p>Explore our selection of custom burgers, crafted with the finest ingredients and tailored to your taste. Click here to view our menu and start building your perfect burger today!</p>
    </div>
    <!-- loops through all items in the JSON object-->
    <div v-for="burger in customBurger" :key="burger.name" class="card">
        <h2>{{ burger.name }}</h2>
        <p>{{ burger.description }}</p>
    </div>
</div>
</template>

<style src="../styles/BurgerMenuView.css"></style>
