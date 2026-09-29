const API = import.meta.env.VITE_API_URL;

export async function api(path, { method = "GET", body } = {}) {
  // FormData (file uploads): let the browser set the multipart Content-Type itself.
  const isForm = body instanceof FormData;
  const res = await fetch(`${API}${path}`, {
    method,
    credentials: "include",
    headers: isForm ? undefined : { "Content-Type": "application/json" },
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(typeof err.detail === "string" ? err.detail : "Please check the details you entered.");
  }
  if (res.status === 204) return null; // e.g. DELETE
  return res.json();
}