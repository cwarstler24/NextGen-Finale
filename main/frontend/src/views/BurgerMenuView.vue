<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useCart } from '../composables/useCart';
import customBurger from '../data/customBurgers.js';
import { toBurgerImageProps } from '../data/customBurgerImageMapper.js';
import {
    buildBurgerCartOptions,
    buildBurgerSelectionsFromPreset,
    calculateBurgerSelectionsUnitPrice,
    normalizeBurgerOptionGroups,
} from '../data/presetBurgerOptions.js';
import BurgerImage from '../components/BurgerImage.vue';

const BURGER_OPTIONS_ENDPOINT = 'http://localhost:8000/Items/Burger';
const router = useRouter();
const { addItem } = useCart();

const searchQuery = ref('');
const activeFilter = ref('all');
const rawBurgerOptions = ref({});
const burgerOptionsLoadState = ref('idle');
const isAddingBurgerId = ref(null);
const menuCartFeedback = ref({
    burgerId: null,
    type: '',
    message: '',
});
let burgerOptionsPromise = null;
let menuCartFeedbackTimeoutId = null;

const preferredPattyOrder = ['Beef', 'Chicken', 'Fish', 'Veggie', 'Smash', 'None'];

function formatPattyLabel(value) {
    return value === 'None' ? 'No patty' : value;
}

function formatBunLabel(value) {
    return value === 'None' ? 'No bun' : value;
}

function formatToppingLabel(topping) {
    const quantity = Math.max(1, Number.parseInt(topping?.qty ?? 1, 10) || 1);
    return quantity > 1
        ? `${topping.type} x${quantity}`
        : topping.type;
}

function formatList(values) {
    if (values.length <= 1) {
        return values[0] ?? '';
    }

    if (values.length === 2) {
        return `${values[0]} and ${values[1]}`;
    }

    return `${values.slice(0, -1).join(', ')}, and ${values[values.length - 1]}`;
}

function clearMenuCartFeedbackTimeout() {
    if (menuCartFeedbackTimeoutId !== null) {
        clearTimeout(menuCartFeedbackTimeoutId);
        menuCartFeedbackTimeoutId = null;
    }
}

function showMenuCartFeedback(burgerId, type, message) {
    menuCartFeedback.value = {
        burgerId,
        type,
        message,
    };
    clearMenuCartFeedbackTimeout();
    menuCartFeedbackTimeoutId = window.setTimeout(() => {
        menuCartFeedback.value = {
            burgerId: null,
            type: '',
            message: '',
        };
        menuCartFeedbackTimeoutId = null;
    }, 4000);
}

const burgerOptionGroups = computed(() => normalizeBurgerOptionGroups(rawBurgerOptions.value));

const mappedBurgers = computed(() => customBurger.map((burger) => {
    const imageProps = toBurgerImageProps(burger);
    const toppings = Array.isArray(burger.toppings) ? burger.toppings : [];

    return {
        ...burger,
        imageProps,
        bunLabel: formatBunLabel(burger.bun),
        pattyLabel: formatPattyLabel(burger.patty),
        toppingLabels: toppings.map(formatToppingLabel),
        toppingTypeCount: toppings.length,
        toppingCountLabel: toppings.length === 0
            ? 'No toppings'
            : `${toppings.length} topping${toppings.length === 1 ? '' : 's'}`,
        searchableText: [
            burger.name,
            burger.description,
            burger.bun,
            burger.patty,
            ...toppings.map((topping) => topping.type),
        ].join(' ').toLowerCase(),
    };
}));

const totalBurgerCount = computed(() => mappedBurgers.value.length);
const bunStyleCount = computed(() => new Set(mappedBurgers.value.map((burger) => burger.bunLabel)).size);
const pattyStyleCount = computed(() => new Set(mappedBurgers.value.map((burger) => burger.pattyLabel)).size);

const pattyFilters = computed(() => {
    const counts = mappedBurgers.value.reduce((totals, burger) => {
        totals.set(burger.patty, (totals.get(burger.patty) ?? 0) + 1);
        return totals;
    }, new Map());

    const orderedPattyValues = [...counts.keys()].sort((left, right) => {
        const leftIndex = preferredPattyOrder.indexOf(left);
        const rightIndex = preferredPattyOrder.indexOf(right);

        if (leftIndex !== -1 && rightIndex !== -1) {
            return leftIndex - rightIndex;
        }

        if (leftIndex !== -1) {
            return -1;
        }

        if (rightIndex !== -1) {
            return 1;
        }

        return left.localeCompare(right);
    });

    return [
        {
            value: 'all',
            label: 'All burgers',
            count: mappedBurgers.value.length,
        },
        ...orderedPattyValues.map((value) => ({
            value,
            label: formatPattyLabel(value),
            count: counts.get(value) ?? 0,
        })),
    ];
});

const filteredBurgers = computed(() => {
    const normalizedQuery = searchQuery.value.trim().toLowerCase();

    return mappedBurgers.value.filter((burger) => {
        const matchesFilter = activeFilter.value === 'all' || burger.patty === activeFilter.value;
        const matchesSearch = normalizedQuery === '' || burger.searchableText.includes(normalizedQuery);
        return matchesFilter && matchesSearch;
    });
});

const hasActiveFilters = computed(() => activeFilter.value !== 'all' || searchQuery.value.trim() !== '');
const resultSummary = computed(() => {
    const visibleCount = filteredBurgers.value.length;
    const totalCount = mappedBurgers.value.length;

    if (!hasActiveFilters.value) {
        return `Showing all ${totalCount} signature burgers.`;
    }

    return `Showing ${visibleCount} of ${totalCount} signature burgers.`;
});

function resetFilters() {
    searchQuery.value = '';
    activeFilter.value = 'all';
}

function goToBurgerPage() {
    router.push({ name: 'product', params: { product: 'Burger' } });
}

function goToPresetBurger(burgerId) {
    router.push({
        name: 'product',
        params: {
            product: 'Burger',
            presetId: String(burgerId),
        },
    });
}

async function loadBurgerOptions() {
    if (burgerOptionsPromise) {
        return burgerOptionsPromise;
    }

    burgerOptionsLoadState.value = 'loading';
    burgerOptionsPromise = fetch(BURGER_OPTIONS_ENDPOINT)
        .then(async (response) => {
            if (!response.ok) {
                throw new Error(`Failed to load burger options: ${response.status} ${response.statusText}`);
            }

            rawBurgerOptions.value = await response.json();
            burgerOptionsLoadState.value = 'success';
        })
        .catch((error) => {
            burgerOptionsLoadState.value = 'error';
            console.error('Unable to fetch burger options for menu cart actions', error);
        })
        .finally(() => {
            burgerOptionsPromise = null;
        });

    return burgerOptionsPromise;
}

async function addPresetBurgerToCart(burger) {
    if (burgerOptionsLoadState.value !== 'success') {
        await loadBurgerOptions();
    }

    if (burgerOptionsLoadState.value !== 'success') {
        showMenuCartFeedback(
            burger.id,
            'error',
            'This burger cannot be added right now because ordering options are unavailable.'
        );
        return;
    }

    isAddingBurgerId.value = burger.id;

    try {
        const {
            selections,
            unavailableIngredients,
            unavailableCoreSelections,
            adjustedIngredients,
        } = buildBurgerSelectionsFromPreset(burgerOptionGroups.value, burger);

        if (unavailableCoreSelections.length > 0) {
            showMenuCartFeedback(
                burger.id,
                'error',
                `This burger cannot be added directly because ${formatList(unavailableCoreSelections)} is unavailable. Load it in the builder to adjust the recipe.`
            );
            return;
        }

        addItem({
            id: 'burger',
            name: burger.name,
            image: '',
            unitPrice: calculateBurgerSelectionsUnitPrice(burgerOptionGroups.value, selections),
            quantity: 1,
            options: buildBurgerCartOptions(burgerOptionGroups.value, selections),
        });

        const messageParts = [`${burger.name} added to cart.`];
        const skippedToppings = unavailableIngredients.filter((ingredient) => !unavailableCoreSelections.includes(ingredient));
        if (skippedToppings.length > 0) {
            messageParts.push(`Skipped unavailable toppings: ${formatList(skippedToppings)}.`);
        }
        if (adjustedIngredients.length > 0) {
            messageParts.push(`Reduced quantities for: ${formatList(adjustedIngredients)}.`);
        }

        showMenuCartFeedback(burger.id, 'success', messageParts.join(' '));
    } finally {
        isAddingBurgerId.value = null;
    }
}

onMounted(() => {
    loadBurgerOptions();
});

onBeforeUnmount(() => {
    clearMenuCartFeedbackTimeout();
});
</script>

<template>
<section class="page burger-menu-page">
    <header class="hero burger-menu-hero">
        <div class="burger-menu-hero__copy">
            <span class="eyebrow">Signature burger menu</span>
            <h1>Browse the full lineup before you build your own.</h1>
            <p class="subtitle">
                Explore every preset burger, compare buns, patties, and toppings, then head to the burger builder
                when you are ready to customize an order.
            </p>

            <div class="burger-menu-hero__actions">
                <button class="primary" type="button" @click="goToBurgerPage">
                    Build Your Own Burger
                </button>
                <a class="burger-menu-link" href="#signature-burger-grid">
                    Browse signature burgers
                </a>
            </div>
        </div>

        <div class="burger-menu-stats" aria-label="Burger menu summary">
            <article class="burger-menu-stat card">
                <span class="burger-menu-stat__value">{{ totalBurgerCount }}</span>
                <span class="burger-menu-stat__label">Signature builds</span>
            </article>
            <article class="burger-menu-stat card">
                <span class="burger-menu-stat__value">{{ bunStyleCount }}</span>
                <span class="burger-menu-stat__label">Bun styles</span>
            </article>
            <article class="burger-menu-stat card">
                <span class="burger-menu-stat__value">{{ pattyStyleCount }}</span>
                <span class="burger-menu-stat__label">Patty options</span>
            </article>
        </div>
    </header>

    <section class="card menu-toolbar" aria-label="Burger menu filters">
        <div class="menu-toolbar__header">
            <div>
                <span class="eyebrow">Browse smarter</span>
                <h2>Find the burger that fits your mood.</h2>
            </div>
            <p>
                Search by name, topping, bun, or patty, then use the quick filters to narrow the list.
            </p>
        </div>

        <div class="menu-toolbar__controls">
            <label class="search-field" for="burger-search">
                <span class="search-field__label">Search the menu</span>
                <input
                    id="burger-search"
                    v-model.trim="searchQuery"
                    class="search-field__input"
                    type="search"
                    placeholder="Try bacon, veggie, pretzel, honey..."
                />
            </label>

            <div class="filter-chip-list" role="group" aria-label="Filter burgers by patty type">
                <button
                    v-for="filter in pattyFilters"
                    :key="filter.value"
                    class="filter-chip"
                    :class="{ 'is-active': activeFilter === filter.value }"
                    type="button"
                    @click="activeFilter = filter.value"
                >
                    <span>{{ filter.label }}</span>
                    <span class="filter-chip__count">{{ filter.count }}</span>
                </button>
            </div>
        </div>

        <div class="menu-toolbar__summary">
            <p>{{ resultSummary }}</p>
            <button v-if="hasActiveFilters" class="secondary menu-toolbar__reset" type="button" @click="resetFilters">
                Clear filters
            </button>
        </div>
    </section>

    <section id="signature-burger-grid" class="burger-grid-section">
        <div class="burger-grid-section__header">
            <div>
                <span class="eyebrow">Preset combinations</span>
                <h2>Explore the signature lineup.</h2>
            </div>
            <p>
                These cards are here to help you compare flavors and ingredients. When you find inspiration, use
                <strong>Build Your Own Burger</strong> to start an order.
            </p>
        </div>

        <div v-if="filteredBurgers.length > 0" class="burger-grid">
            <article v-for="burger in filteredBurgers" :key="burger.id" class="card burger-menu-card">
                <div class="burger-preview">
                    <BurgerImage v-bind="burger.imageProps" class="burger-preview__fallback-image" />
                </div>

                <div class="burger-menu-card__content">
                    <div class="burger-menu-card__header">
                        <div>
                            <h3>{{ burger.name }}</h3>
                            <p>{{ burger.description }}</p>
                        </div>
                    </div>

                    <div class="burger-badge-row" aria-label="Burger summary">
                        <span class="detail-pill">{{ burger.bunLabel }}</span>
                        <span class="detail-pill">{{ burger.pattyLabel }}</span>
                        <span class="detail-pill">{{ burger.toppingCountLabel }}</span>
                    </div>

                    <dl class="burger-facts">
                        <div class="burger-facts__item">
                            <dt>Bun</dt>
                            <dd>{{ burger.bunLabel }}</dd>
                        </div>
                        <div class="burger-facts__item">
                            <dt>Patty</dt>
                            <dd>{{ burger.pattyLabel }}</dd>
                        </div>
                        <div class="burger-facts__item">
                            <dt>Toppings</dt>
                            <dd>{{ burger.toppingTypeCount }}</dd>
                        </div>
                    </dl>

                    <div class="burger-toppings">
                        <h4>Toppings</h4>
                        <div class="burger-toppings__list">
                            <span v-if="burger.toppingLabels.length === 0" class="topping-chip topping-chip--muted">
                                No toppings
                            </span>
                            <span v-for="topping in burger.toppingLabels" :key="topping" class="topping-chip">
                                {{ topping }}
                            </span>
                        </div>
                    </div>

                    <p class="burger-menu-card__note">
                        Like this combination? Use the burger builder to recreate it and adjust the details your way.
                    </p>

                    <div class="burger-menu-card__actions">
                        <button
                            class="primary"
                            type="button"
                            :disabled="isAddingBurgerId === burger.id"
                            @click="addPresetBurgerToCart(burger)"
                        >
                            {{ isAddingBurgerId === burger.id ? 'Adding...' : 'Add to Cart' }}
                        </button>
                        <button class="secondary" type="button" @click="goToPresetBurger(burger.id)">
                            Load This Burger
                        </button>
                    </div>

                    <p
                        v-if="menuCartFeedback.burgerId === burger.id"
                        class="burger-menu-card__feedback"
                        :class="`is-${menuCartFeedback.type}`"
                        role="status"
                        aria-live="polite"
                    >
                        {{ menuCartFeedback.message }}
                    </p>
                </div>
            </article>
        </div>

        <div v-else class="card burger-empty-state" role="status" aria-live="polite">
            <h3>No burgers match those filters.</h3>
            <p>Try a broader search or clear the active filters to see the full burger menu again.</p>
            <button class="secondary" type="button" @click="resetFilters">
                Reset menu filters
            </button>
        </div>
    </section>
</section>
</template>

<style src="../styles/BurgerMenuView.css"></style>
