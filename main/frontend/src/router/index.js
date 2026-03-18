import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import ProductView from '../views/ProductView.vue'
import CartView from '../views/CartView.vue'
import CheckoutView from '../views/CheckoutView.vue'
import UserView from '../views/UserView.vue'
import ConfirmationView from '../views/ConfirmationView.vue'

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
        path: "/confirmation",
        name: "confirm",
        component: ConfirmationView,
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
