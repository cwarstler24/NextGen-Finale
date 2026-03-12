import { computed, ref } from 'vue';

const CART_KEY = 'cart';
const cartItems = ref([]);

let isInitialized = false;
let hasStorageListener = false;

function normalizeOptionValue(value) {
    if (Array.isArray(value)) {
        return [...new Set(value)].sort((left, right) => String(left).localeCompare(String(right)));
    }

    return value ?? null;
}

function normalizeOptions(options = []) {
    return options.map((option) => ({
        name: String(option.name ?? ''),
        value: normalizeOptionValue(option.value),
    }));
}

function normalizeCartItem(item) {
    return {
        id: String(item.id),
        name: String(item.name),
        image: String(item.image ?? ''),
        unitPrice: Number(item.unitPrice) || 0,
        quantity: Math.max(1, Number.parseInt(item.quantity ?? 1, 10) || 1),
        options: normalizeOptions(item.options),
    };
}

function createItemSignature(item) {
    return JSON.stringify({
        id: item.id,
        options: item.options.map((option) => ({
            name: option.name,
            value: option.value,
        })),
    });
}

function writeCart(items) {
    localStorage.setItem(CART_KEY, JSON.stringify(items));
    cartItems.value = items;
}

function readCart() {
    const storedCart = localStorage.getItem(CART_KEY);

    if (!storedCart) {
        return [];
    }

    try {
        const parsedCart = JSON.parse(storedCart);

        if (!Array.isArray(parsedCart)) {
            console.warn('Expected cart storage to contain an array. Resetting cart.');
            localStorage.removeItem(CART_KEY);
            return [];
        }

        return parsedCart.map(normalizeCartItem);
    } catch (error) {
        if (error instanceof SyntaxError) {
            console.warn('Cart storage was invalid JSON. Resetting cart.', error);
            localStorage.removeItem(CART_KEY);
            return [];
        }

        throw error;
    }
}

function ensureCartInitialized() {
    if (typeof window === 'undefined') {
        return;
    }

    if (!isInitialized) {
        cartItems.value = readCart();
        isInitialized = true;
    }

    if (!hasStorageListener) {
        window.addEventListener('storage', (event) => {
            if (event.key === CART_KEY) {
                cartItems.value = readCart();
            }
        });

        hasStorageListener = true;
    }
}

export function useCart() {
    ensureCartInitialized();

    const cartEntries = computed(() => cartItems.value.map((item) => ({
        ...item,
        signature: createItemSignature(item),
        lineTotal: item.unitPrice * item.quantity,
    })));

    const cartCount = computed(() => cartItems.value.reduce((count, item) => count + item.quantity, 0));
    const cartTotal = computed(() => cartItems.value.reduce((total, item) => total + (item.unitPrice * item.quantity), 0));

    function addItem(item) {
        const normalizedItem = normalizeCartItem(item);
        const itemSignature = createItemSignature(normalizedItem);
        const existingIndex = cartItems.value.findIndex((cartItem) => createItemSignature(cartItem) === itemSignature);
        const nextItems = [...cartItems.value];

        if (existingIndex >= 0) {
            nextItems[existingIndex] = {
                ...nextItems[existingIndex],
                quantity: nextItems[existingIndex].quantity + normalizedItem.quantity,
            };
        } else {
            nextItems.push(normalizedItem);
        }

        writeCart(nextItems);
    }

    function removeItem(signature) {
        writeCart(cartItems.value.filter((item) => createItemSignature(item) !== signature));
    }

    function clearCart() {
        writeCart([]);
    }

    return {
        cartEntries,
        cartCount,
        cartTotal,
        addItem,
        removeItem,
        clearCart,
    };
}
