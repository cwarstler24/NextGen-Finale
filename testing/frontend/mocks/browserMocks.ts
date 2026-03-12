// Mock localStorage
Object.defineProperty(global, 'localStorage', {
    value: {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn()
    },
    writable: true
});

// Mock fetch (can be expanded later)
global.fetch = vi.fn(() =>
    Promise.resolve({
        json: () => Promise.resolve({})
    })
);
