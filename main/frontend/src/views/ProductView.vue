<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();
import { onMounted } from 'vue';
</script>
<style src="../styles/ProductView.css" scoped></style>

<template>
        <section class="page product-page">
                <div class="product-breadcrumbs">
                    <span>Home</span> / <span class="current">{{ $route.params.product }}</span>
                </div>

                <div class="product-grid">
                        <div class="product-gallery card">
                                <img class="product-hero" src="../assets/placeholder.png" alt="Product hero" />
                                <div class="thumbnail-row">
                                        <button class="thumb is-active" type="button">
                                                <img src="../assets/placeholder.png" alt="Thumbnail 1" />
                                        </button>
                                        <button class="thumb" type="button">
                                                <img src="../assets/placeholder.png" alt="Thumbnail 2" />
                                        </button>
                                        <button class="thumb" type="button">
                                                <img src="../assets/placeholder.png" alt="Thumbnail 3" />
                                        </button>
                                </div>
                                <div class="gallery-meta">
                                        <span>Seasonal favorite</span>
                                        <span>High-protein</span>
                                </div>
                        </div>

                        <div class="product-info card">
                                <div class="product-header">
                                        <div>
                                                <p class="eyebrow">Signature combo</p>
                                                <h2>Product Name</h2>
                                                <p class="product-description">
                                                        A crave-worthy mix of crisp, golden bites with fresh toppings. Balanced, filling,
                                                        and perfect for a quick lunch or family night in.
                                                </p>
                                        </div>
                                        <div class="price-tag">
                                                <span class="price">$12.99</span>
                                                <span class="per">per meal</span>
                                        </div>
                                </div>

                                <div class="meta-row">
                                        <div>
                                                <span class="meta-label">Rating</span>
                                                <strong>4.8</strong>
                                                <span class="meta-muted">(234 reviews)</span>
                                        </div>
                                        <div>
                                                <span class="meta-label">Calories</span>
                                                <strong>520</strong>
                                        </div>
                                        <div>
                                                <span class="meta-label">Prep time</span>
                                                <strong>15 min</strong>
                                        </div>
                                </div>

                                <div class="product-actions">
                                        <button class="primary" type="button">
                                                Add to Cart
                                        </button>
                                        <button class="secondary" type="button" @click="router.push({ name: 'home' })">
                                                Back to Home
                                        </button>
                                </div>

                                <div class="shipping-callout">
                                        <strong>Free pickup</strong>
                                        <span>Ready in 20-25 minutes · Freshly made to order</span>
                                </div>
                        </div>
                </div>

                <div class="details-grid">
                        <div class="card">
                                <h3>Customize your order</h3>
                                <p class="section-description">
                                        Choose from popular add-ons and sides to make this meal yours.
                                </p>
                                <div class="option-grid">
                                        <label>
                                                Side
                                                <select>
                                                        <option value="fries">Crispy fries</option>
                                                        <option value="salad">Garden salad</option>
                                                        <option value="fruit">Fresh fruit</option>
                                                </select>
                                        </label>
                                        <label>
                                                Protein
                                                <select>
                                                        <option value="classic">Classic</option>
                                                        <option value="spicy">Spicy</option>
                                                        <option value="plant">Plant-based</option>
                                                </select>
                                        </label>
                                        <label>
                                                Sauce
                                                <select>
                                                        <option value="aioli">Garlic aioli</option>
                                                        <option value="chipotle">Chipotle</option>
                                                        <option value="honey">Honey mustard</option>
                                                </select>
                                        </label>
                                </div>
                        </div>

                        <div class="card">
                                <h3>What’s included</h3>
                                <ul class="list">
                                        <li>Made-to-order entrée with premium seasoning</li>
                                        <li>Two classic sides and house sauce</li>
                                        <li>Eco-friendly packaging and utensils</li>
                                        <li>Nutritional info and allergen guide</li>
                                </ul>
                        </div>
                </div>
        </section>
</template>

<style scoped>
.product-page {
    gap: 2.5rem;
}

.product-breadcrumbs {
    font-size: 0.9rem;
    color: #64748b;
}

.product-breadcrumbs .current {
    color: #0f172a;
    font-weight: 600;
}

.product-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
    gap: 2rem;
    align-items: start;
}

.product-gallery {
    gap: 1.5rem;
}

.product-hero {
    border-radius: 16px;
    width: 100%;
    object-fit: cover;
    background: #e2e8f0;
}

.thumbnail-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
}

.thumb {
    padding: 0.35rem;
    border-radius: 12px;
    border: 1px solid transparent;
    background: #f8fafc;
}

.thumb.is-active {
    border-color: #38bdf8;
    background: #e0f2fe;
}

.gallery-meta {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    color: #475569;
    font-size: 0.9rem;
}

.product-info {
    gap: 1.5rem;
}

.product-header {
    display: flex;
    gap: 1.5rem;
    justify-content: space-between;
    align-items: flex-start;
}

.product-description {
    margin: 0.75rem 0 0;
    color: #64748b;
}

.price-tag {
    text-align: right;
    background: #f1f5f9;
    padding: 0.75rem 1rem;
    border-radius: 14px;
    min-width: 110px;
}

.price {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
}

.per {
    color: #64748b;
    font-size: 0.85rem;
}

.meta-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
    background: #f8fafc;
    padding: 1rem;
    border-radius: 14px;
    color: #0f172a;
}

.meta-label {
    display: block;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94a3b8;
}

.meta-muted {
    color: #94a3b8;
    font-size: 0.85rem;
    margin-left: 0.25rem;
}

.product-actions {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.shipping-callout {
    display: grid;
    gap: 0.25rem;
    padding: 1rem;
    border-radius: 14px;
    background: #ecfeff;
    color: #0f172a;
    font-size: 0.95rem;
}

.details-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 2rem;
}

.section-description {
    margin: 0;
    color: #64748b;
}

.option-grid {
    display: grid;
    gap: 1rem;
    margin-top: 1rem;
}

.option-grid label {
    display: grid;
    gap: 0.5rem;
    font-weight: 600;
    color: #0f172a;
}

.option-grid select {
    padding: 0.65rem 0.75rem;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    font-family: inherit;
    background: #ffffff;
}

@media (max-width: 960px) {
    .product-grid {
        grid-template-columns: 1fr;
    }

    .product-header {
        flex-direction: column;
    }

    .price-tag {
        text-align: left;
    }

    .details-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 600px) {
    .meta-row {
        grid-template-columns: 1fr;
    }
}
</style>
