import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import ProductView from '../views/ProductView.vue'

const routes = [
    {
        path: "/",
        name: "main",
        component: MainView,
    },
    {
        path: "/product/:product",
        name: "product",
        component: ProductView,
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
