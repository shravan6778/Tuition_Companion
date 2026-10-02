const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Callable function; always resolves to { data }
export async function api(path, options = {}) {
  const { headers, body, ...rest } = options;

  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
  const isPlainObject =
    body && typeof body === "object" && !isFormData && !(body instanceof Blob);

  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...rest,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(headers || {}),
    },
    body: isPlainObject ? JSON.stringify(body) : body,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const err = new Error(
      errorData.detail || `Request failed with status ${res.status}`,
    );
    err.status = res.status;
    err.data = errorData;
    throw err;
  }

  if (res.status === 204) return { data: null };

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  return { data };
}

// Convenience methods
api.get = (path, options = {}) => api(path, { method: "GET", ...options });

api.post = (path, body, options = {}) =>
  api(path, { method: "POST", body: body || undefined, ...options });

api.delete = (path, options = {}) => api(path, { method: "DELETE", ...options });

export default api;