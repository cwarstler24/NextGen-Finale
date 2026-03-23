function normalizeUrl(value, fallback) {
    const trimmedValue = typeof value === 'string' ? value.trim() : '';
    return trimmedValue || fallback;
}

function removeTrailingSlash(value) {
    return value.replace(/\/+$/, '');
}

export const apiBaseUrl = removeTrailingSlash(
    normalizeUrl(import.meta.env.VITE_API_BASE_URL, 'http://localhost:8000'),
);

export const docsBaseUrl = removeTrailingSlash(
    normalizeUrl(import.meta.env.VITE_DOCS_BASE_URL, 'http://127.0.0.1:8001'),
);

export function buildApiUrl(path) {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${apiBaseUrl}${normalizedPath}`;
}
