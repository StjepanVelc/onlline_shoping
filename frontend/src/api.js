export const API = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`

function formatValidationErrors(detail) {
    if (!Array.isArray(detail)) {
        return null
    }

    const messages = detail
        .map((item) => item?.msg)
        .filter(Boolean)

    return messages.length > 0 ? messages.join(" ") : null
}

export async function readApiError(response, fallbackMessage) {
    let payload = null

    try {
        payload = await response.json()
    } catch {
        payload = null
    }

    const validationMessage = formatValidationErrors(payload?.detail)
    if (validationMessage) {
        return validationMessage
    }

    if (typeof payload?.detail === "string" && payload.detail.trim()) {
        return payload.detail
    }

    return fallbackMessage
}
