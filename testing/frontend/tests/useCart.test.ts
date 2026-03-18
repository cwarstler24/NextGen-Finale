import { beforeEach, describe, expect, it, vi } from 'vitest';
import { localStorageMock } from '../mocks/browserMocks';

async function loadUseCart() {
    return import('../../../main/frontend/src/composables/useCart.js');
}

describe('useCart', () => {
    beforeEach(() => {
        vi.resetModules();
        localStorageMock.getItem.mockReset();
        localStorageMock.setItem.mockReset();
        localStorageMock.removeItem.mockReset();
        localStorageMock.clear.mockReset();
    });

    it('adds items, merges duplicates, and removes them by signature', async () => {
        localStorageMock.getItem.mockReturnValue(null);

        const { useCart } = await loadUseCart();
        const cart = useCart();

        cart.addItem({
            id: 'burger',
            image: '/images/Burger1.png',
            name: 'Classic Burger',
            options: [
                { id: '102', name: 'Bun', value: 'Pretzel' },
                { id: ['301'], name: 'Toppings', value: ['Lettuce'] },
            ],
            quantity: 1,
            unitPrice: 6,
        });

        cart.addItem({
            id: 'burger',
            image: '/images/Burger1.png',
            name: 'Classic Burger',
            options: [
                { id: '102', name: 'Bun', value: 'Pretzel' },
                { id: ['301'], name: 'Toppings', value: ['Lettuce'] },
            ],
            quantity: 2,
            unitPrice: 6,
        });

        expect(cart.cartCount.value).toBe(3);
        expect(cart.cartTotal.value).toBe(18);
        expect(cart.cartEntries.value).toHaveLength(1);
        expect(cart.cartEntries.value[0].quantity).toBe(3);

        const signature = cart.cartEntries.value[0].signature;
        cart.removeItem(signature);

        expect(cart.cartCount.value).toBe(0);
        expect(cart.cartTotal.value).toBe(0);

        cart.clearCart();
        expect(localStorageMock.setItem).toHaveBeenLastCalledWith('cart', JSON.stringify([]));
    });

    it('normalizes incomplete cart items when adding them', async () => {
        localStorageMock.getItem.mockReturnValue(null);

        const { useCart } = await loadUseCart();
        const cart = useCart();

        cart.addItem({
            id: 42,
            name: 'Mystery Item',
            options: [
                { id: undefined, name: undefined, value: undefined },
                { id: ['b', 'a', 'a'], name: 'Extras', value: ['z', 'a', 'a'] },
            ],
            quantity: 0,
            unitPrice: 'not-a-number',
        });

        expect(cart.cartEntries.value[0]).toMatchObject({
            id: '42',
            image: '',
            name: 'Mystery Item',
            quantity: 1,
            unitPrice: 0,
        });
        expect(cart.cartEntries.value[0].options).toEqual([
            { id: null, name: '', value: null },
            { id: ['a', 'b'], name: 'Extras', value: ['a', 'z'] },
        ]);
    });

    it('resets invalid storage and responds to storage events', async () => {
        const addEventListenerSpy = vi.spyOn(window, 'addEventListener');
        const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

        localStorageMock.getItem
            .mockReturnValueOnce('{"badJson":')
            .mockReturnValueOnce(JSON.stringify([
                {
                    id: 'fries',
                    image: '/images/Fries1.png',
                    name: 'Crispy Fries',
                    options: [{ id: '401', name: 'Size', value: 'Small' }],
                    quantity: 2,
                    unitPrice: 2.5,
                },
            ]));

        const { useCart } = await loadUseCart();
        const cart = useCart();

        expect(localStorageMock.removeItem).toHaveBeenCalledWith('cart');
        expect(cart.cartCount.value).toBe(0);

        const storageListener = addEventListenerSpy.mock.calls.find(
            ([eventName]) => eventName === 'storage'
        )?.[1];

        expect(storageListener).toBeDefined();
        if (typeof storageListener === 'function') {
            storageListener({ key: 'cart' } as StorageEvent);
        } else if (storageListener && 'handleEvent' in storageListener) {
            storageListener.handleEvent({ key: 'cart' } as StorageEvent);
        } else {
            throw new Error('Storage listener was not registered correctly.');
        }

        expect(cart.cartCount.value).toBe(2);
        expect(cart.cartTotal.value).toBe(5);
        expect(cart.cartEntries.value[0].lineTotal).toBe(5);

        addEventListenerSpy.mockRestore();
        warnSpy.mockRestore();
    });

    it('resets non-array storage payloads before using the cart', async () => {
        const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
        localStorageMock.getItem.mockReturnValue('{"id":"not-an-array"}');

        const { useCart } = await loadUseCart();
        const cart = useCart();

        expect(warnSpy).toHaveBeenCalledWith('Expected cart storage to contain an array. Resetting cart.');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('cart');
        expect(cart.cartEntries.value).toEqual([]);

        warnSpy.mockRestore();
    });

    it('rethrows unexpected parsing failures', async () => {
        const expectedError = new Error('parse failed');
        localStorageMock.getItem.mockReturnValue('cart-data');

        const parseSpy = vi.spyOn(JSON, 'parse').mockImplementation(() => {
            throw expectedError;
        });

        const { useCart } = await loadUseCart();

        expect(() => useCart()).toThrow(expectedError);

        parseSpy.mockRestore();
    });

    it('skips browser initialization when window is unavailable', async () => {
        vi.stubGlobal('window', undefined);

        const { useCart } = await loadUseCart();
        const cart = useCart();

        expect(cart.cartEntries.value).toEqual([]);
        expect(cart.cartCount.value).toBe(0);
        expect(localStorageMock.getItem).not.toHaveBeenCalled();

        vi.unstubAllGlobals();
    });
});