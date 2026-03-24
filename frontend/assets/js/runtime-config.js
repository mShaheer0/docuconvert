// Configure your backend API base URL for static hosting (GitHub Pages).
// Example: "https://your-app-name.azurewebsites.net"
window.DOCUCONVERT_API_BASE_URL = window.DOCUCONVERT_API_BASE_URL || "";

function buildApiUrl(path) {
    const normalizedPath = path.startsWith("/") ? path : `/${path}`;
    const base = (window.DOCUCONVERT_API_BASE_URL || "").trim().replace(/\/$/, "");
    if (!base) return normalizedPath;
    return `${base}${normalizedPath}`;
}
