import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DetailsView from '../views/DetailsView.vue'
import BurgerView from '../views/BurgerView.vue'
import FriesView from '../views/FriesView.vue'
import MainView from '../views/MainView.vue'
import ProductView from '../views/ProductView.vue'

const routes = [
    {
        path: "/",
        name: "main",
        component: MainView,
    },
    {
        path: '/home',
        name: 'home',
        component: HomeView,
    },
    {
        path: '/details',
        name: 'details',
        component: DetailsView,
    },
    {
        path: "/burger",
        name: "burger",
        component: BurgerView,
    },
    {
        path: "/fries",
        name: "fries",
        component: FriesView,
    },
    {
        path: "/product",
        name: "product",
        component: ProductView,
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
