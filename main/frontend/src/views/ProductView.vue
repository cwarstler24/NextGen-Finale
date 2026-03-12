<script setup>
import { computed, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import BurgerOptionsComp from '../components/BurgerOptionsComp.vue';
import FriesOptionsComp from '../components/FriesOptionsComp.vue';

const router = useRouter();

// Get product from route params
const product = computed(() => {
    return (router.currentRoute.value.params.product || '').toLowerCase();
});

// Map product to image arrays
const productImages = computed(() => {
    switch (product.value) {
        case 'burger':
            return ['/images/Burger1.png', '/images/Burger2.png', '/images/Burger3.png'];
        case 'fries':
            return ['/images/Fries1.png', '/images/Fries2.png', '/images/Fries3.png'];
        default:
            return ['/images/placeholder.png', '/images/placeholder.png', '/images/placeholder.png'];
    }
});

const productData = computed(() => {
    // TODO replace with API data

    switch (product.value) {
        case 'burger':
            return {
                name: 'Classic Burger',
                description: 'A crave-worthy mix of crisp, golden bites with fresh toppings. Balanced, filling, and perfect for a quick lunch or family night in.',
                price: '.0',
            };
        case 'fries':
            return {
                name: 'Crispy Fries',
                description: 'Golden, crispy fries seasoned to perfection. A deliciously satisfying side that pairs perfectly with any meal.',
                price: '0.0',
            };
        default:
            return {
                name: 'Unknown Product',
                description: 'No description available.',
                price: '0',
            };
    };
});

const totalPrice = computed(() => {
    const base = parseFloat(productData.value.price.replace('$', '')) || 0;
    let optionTotal = 0;

    for (let i = 0; i < selectedOptions.value.length; i++) {
        const optionKey = `option${i + 1}`;
        const selectedValue = selectedOptions.value[i];
        const selectedValues = Array.isArray(selectedValue) ? selectedValue : [selectedValue];

        for (const value of selectedValues) {
            const idx = productOptions.value[optionKey]?.indexOf(value);
            if (idx !== undefined && idx >= 0) {
                optionTotal += productOptions.value[`${optionKey}Price`][idx] || 0;
            }
        }
    }

    return `${(base + optionTotal).toFixed(2)}`;
});

const productOptions = computed(() => {
    // TODO replace with API data
    switch (product.value) {
        case 'burger':
            return {
                optionNames: ['Bun', 'Patty', 'Toppings'],
                option1: ['Regular', 'Pretzel', 'None'],
                option2: ['Regular', 'Vegan', 'Dirt', 'None'],
                option3: ['Lettuce', 'Tomato','Pickles','Mustard','Katchup','Mayo'],
                option1Price: [1,1.5,0],
                option2Price: [3,4,1,0],
                option3Price: [0.5,0.5,0.5,0,0,0]
            };
        case 'fries':
            return {
                optionNames: ['Size', 'Type', 'Seasoning'],
                option1: ['Small', 'Medium', 'Large'],
                option2: ['Shoe-Lace', 'Curly', 'Sweet Potato'],
                option3: ['Salt','Cajun','Sugar'],
                option1Price: [.5,1,2],
                option2Price: [0,0.5,1],
                option3Price: [0,0.5,0.5]
            };
        default:
            return {
                optionNames: [],
                option1: [],
                option2: [],
                option3: [],
                option1Price: [],
                option2Price: [],
                option3Price: [],
            };
    }
});

const customizationComponent = computed(() => {
    switch (product.value) {
        case 'burger':
            return BurgerOptionsComp;
        case 'fries':
            return FriesOptionsComp;
        default:
            return null;
    }
});

const selectedOptions = ref([]);

watch(
    productOptions,
    (options) => {
        selectedOptions.value = (options.optionNames || []).map((_, idx) => {
            if (product.value === 'fries' && idx === 2) {
                return [];
            }

            return options[`option${idx + 1}`]?.[0] ?? null;
        });
    },
    { immediate: true }
);

const selectedIndex = ref(0);

const selectThumbnail = (index) => {
    selectedIndex.value = index;
};

const goMainPage = () => {
    router.push({ name: 'main' });
};

const addToCart = () => {
    // TODO implement add to cart functionality
    // For now, show an alert with the selected options and total price
    alert(`Added to cart:\nProduct: ${productData.value.name}\nOptions: ${selectedOptions.value.map((opt, idx) => `${productOptions.value.optionNames[idx]}: ${opt}`).join(', ')}\nTotal Price: $${totalPrice.value}`);
};

</script>
<template>
<section class="page product-page">
    <div class="product-breadcrumbs">
        <span class="hover" @click="goMainPage">Home</span> / <span class="current">{{ $route.params.product }}</span>
    </div>

    <div class="product-grid">
        <div name="product-gallery" class="product-gallery card">
            <img name="product-image" class="product-hero" :src="productImages[selectedIndex]" alt="Product hero" />
            <div class="thumbnail-row">
                <button 
                    v-for="(img, idx) in productImages" 
                    :key="img" 
                    class="thumb" 
                    :class="{ 'is-active': idx === selectedIndex }"
                    type="button"
                    @click="selectThumbnail(idx)" 
                >
                    <img :src="img" :alt="`Thumbnail ${idx + 1}`" />
                </button>
            </div>
        </div>

        <div class="product-info card">
            <div class="product-header">
                <div>
                    <h2>{{ productData.name }}</h2>
                    <p class="product-description">
                        {{ productData.description }}
                    </p>
                </div>
                <div class="price-tag">
                    <span class="price">${{ totalPrice }}</span>
                </div>
            </div>


            <div class="product-actions">
                <button class="primary" type="button" @click="addToCart">
                    Add to Cart
                </button>
            </div>
        </div>
    </div>

    <div class="details-grid" name="product-customization">
        <div class="customization card">
            <component
                :is="customizationComponent"
                v-if="customizationComponent"
                v-model="selectedOptions"
                :product-options="productOptions"
            />
            <template v-else>
                <h3>Customize your order (Default)</h3>
                <div name="options" class="option-grid">
                    <label v-for="(name, idx) in productOptions.optionNames" :key="name">
                        {{ name }}
                        <select v-model="selectedOptions[idx]">
                            <option v-for="(opt, optIdx) in productOptions[`option${idx+1}`]" :key="opt" :value="opt">
                                {{ opt }} <span v-if="productOptions[`option${idx+1}Price`][optIdx] > 0"> +{{ productOptions[`option${idx+1}Price`][optIdx] }}</span>
                            </option>
                        </select>
                    </label>
                </div>
            </template>
        </div>
    </div>
</section>
</template>
<style src="../styles/ProductView.css" scoped></style>
