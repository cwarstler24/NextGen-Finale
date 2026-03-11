<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();
import { ref, computed } from 'vue';

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
                name: 'Classic Burger Combo',
                description: 'A crave-worthy mix of crisp, golden bites with fresh toppings. Balanced, filling, and perfect for a quick lunch or family night in.',
                price: '$12.99',
            };
        case 'fries':
            return {
                name: 'Crispy Fries Combo',
                description: 'Golden, crispy fries seasoned to perfection. A deliciously satisfying side that pairs perfectly with any meal.',
                price: '$8.99',
            };
        default:
            return {
                name: 'Unknown Product',
                description: 'No description available.',
                price: '$0.00',
            };
    };
});

const productOptions = computed(() => {
    switch (product.value) {
        case 'burger':
            return {
                optionNames: ['Bun', 'Patty', 'Toppings'],
                option1: ['Regular', 'Pretzel', 'None'],
                option2: ['Regular', 'Vegan', 'Dirt', 'None'],
                option3: ['Lettuce', 'Tomato','Pickles','Mustard','Katchup','Mayo']
            };
        case 'fries':
            return {
                optionNames: ['Size', 'Type', 'Seasoning'],
                option1: ['Small', 'Medium', 'Large'],
                option2: ['Shoe-Lace', 'Curly', 'Sweet Potato'],
                option3: ['Salt','Cajun','Sugar']
            };
        default:
            return {
                sides: [],
                proteins: [],
                sauces: [],
            };
    }
});

const selectedIndex = ref(0);

const selectThumbnail = (index) => {
  selectedIndex.value = index;
};

const goMainPage = () => {
  router.push({ name: 'main' });
};

</script>
<style src="../styles/ProductView.css" scoped></style>
<template>
        <section class="page product-page">
                <div class="product-breadcrumbs">
                    <span @click="goMainPage" class="hover">Home</span> / <span class="current">{{ $route.params.product }}</span>
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
            <p class="product-description">{{ productData.description }}</p>
        </div>
        <div class="price-tag">
            <span class="price">{{ productData.price }}</span>
        </div>
    </div>


    <div class="product-actions">
        <button class="primary" type="button">
            Add to Cart
        </button>
    </div>
</div>
                </div>

                <div class="details-grid" name="product-customization">
                    <div class="customization card">
                        <h3>Customize your order</h3>
                        <p class="section-description">
                        Choose from popular add-ons and sides to make this meal yours.
                        </p>
                        <div name="options" class="option-grid">
                            <label v-for="(name, idx) in productOptions.optionNames" :key="name">
                                {{ name }}
                                <select>
                                    <option v-for="opt in productOptions[`option${idx+1}`]" :key="opt" :value="opt">
                                    {{ opt }}
                                    </option>
                                </select>
                            </label>
                        </div>
                    </div>

                </div>
        </section>
</template>
