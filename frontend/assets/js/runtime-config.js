// Configure your backend API base URL for static hosting (GitHub Pages).
// Example: "https://your-app-name.azurewebsites.net"
window.FILEGOBLIN_API_BASE_URL = window.FILEGOBLIN_API_BASE_URL || "";

function buildApiUrl(path) {
    const normalizedPath = path.startsWith("/") ? path : `/${path}`;
    const base = (window.FILEGOBLIN_API_BASE_URL || "").trim().replace(/\/$/, "");
    if (!base) return normalizedPath;
    return `${base}${normalizedPath}`;
}
