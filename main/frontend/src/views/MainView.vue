<script setup>
import { useRouter } from 'vue-router'
import BurgerImage from '../components/BurgerImage.vue'

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
            <BurgerImage class="product-image-illustration" />
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
