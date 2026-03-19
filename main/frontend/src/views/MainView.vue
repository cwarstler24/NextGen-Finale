<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToBurgerPage = () => {
    router.push({ name: 'burger-menu' })
}

const goToFriesPage = () => {
    router.push({ name: 'product' , params: { product: 'Fries' }})
}
</script>

<template>
<section class="page">
    <div class="products-row">
        <div class="card product-card" @click="goToBurgerPage">
            <img src="/images/Burger1.png" alt="Burger" class="product-image" />
            <div>Burger</div>
        </div>
        <div class="card product-card" @click="goToFriesPage">
            <img src="/images/Fries1.png" alt="Fries" class="product-image" />
            <div>Fries</div>
        </div>
    </div>
</section>
</template>

<style src="../styles/mainview.css" scoped></style>
