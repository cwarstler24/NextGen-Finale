<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToBurgerPage = () => {
  router.push({ name: 'product' , params: { product: 'Burger' }})
}

const goToFriesPage = () => {
  router.push({ name: 'product' , params: { product: 'Fries' }})
}
</script>
<style src="../styles/mainview.css" scoped></style>

<template>
    <section class="page">
        <div class="products-row">
            <div class="card product-card" @click="goToBurgerPage">
                <img src="/src/assets/Burger.png" alt="Burger" class="product-image" />
                <div>Burger</div>
            </div>
            <div class="card product-card" @click="goToFriesPage">
                <img src="/src/assets/Fries.png" alt="Fries" class="product-image"/>
                <div>Fries</div>
            </div>
        </div>
    </section>
</template>

