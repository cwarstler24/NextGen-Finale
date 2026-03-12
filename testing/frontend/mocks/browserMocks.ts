import { vi } from 'vitest';

export const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
};

export const fetchMock = vi.fn(() =>
    Promise.resolve({
        json: () => Promise.resolve({}),
    })
);

Object.defineProperty(globalThis, 'localStorage', {
    value: localStorageMock,
    writable: true,
});

Object.defineProperty(globalThis, 'fetch', {
    value: fetchMock,
    writable: true,
});
