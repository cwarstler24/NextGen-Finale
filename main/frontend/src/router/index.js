import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import ProductView from '../views/ProductView.vue'
import CartView from '../views/CartView.vue'
import CheckoutView from '../views/CheckoutView.vue'
import UserView from '../views/UserView.vue'
import BurgerMenuView from '../views/BurgerMenuView.vue'

const routes = [
    {
        path: "/",
        name: "main",
        component: MainView,
    },
    {
        path: "/product/:product/:presetId?",
        name: "product",
        component: ProductView,
    },
    {
        path: "/cart",
        name: "cart",
        component: CartView,
    },
    {
        path: "/checkout",
        name: "checkout",
        component: CheckoutView,
    },
    {
        path: "/user",
        name: "user",
        component: UserView,
    },
    {
        path: "/burger-menu",
        name: "burger-menu",
        component: BurgerMenuView,
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
