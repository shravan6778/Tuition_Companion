// Administrator API (backend/app/admin/routes.py). Every function resolves to the response body (null for 204).
import api from "../shared/api";

const body = (p) => p.then((r) => r.data);
const qs = (params = {}) => {
  const q = new URLSearchParams(Object.entries(params).filter(([, v]) => v != null && v !== "")).toString();
  return q ? `?${q}` : "";
};

export const getStatus = () => body(api.get("/admin/status"));

export const listUsers = (params) => body(api.get(`/admin/users${qs(params)}`));
export const disableUser = (id, reason) => body(api.post(`/admin/users/${id}/disable`, { reason }));
export const enableUser = (id) => body(api.post(`/admin/users/${id}/enable`));
export const approveUser = (id) => body(api.post(`/admin/users/${id}/approve`));
export const rejectUser = (id) => body(api.post(`/admin/users/${id}/reject`, {}));
export const setUserCaps = (id, caps) => body(api.put(`/admin/users/${id}/caps`, { caps }));
export const deletePreview = (id) => body(api.get(`/admin/users/${id}/delete-preview`));
export const deleteUser = (id, confirm_username) =>
  body(api(`/admin/users/${id}`, { method: "DELETE", body: { confirm_username } }));

export const failedChapters = () => body(api.get("/admin/chapters/failed"));
export const retryChapter = (id) => body(api.post(`/admin/chapters/${id}/retry`));

export const getUsage = (days = 7) => body(api.get(`/admin/usage${qs({ days })}`));
export const setKillSwitch = (engaged, reason) => body(api.post("/admin/ai/kill-switch", { engaged, reason }));

export const listInvites = () => body(api.get("/admin/teacher-invites"));
export const createInvite = (note, expires_in_days) => body(api.post("/admin/teacher-invites", { note, expires_in_days }));
export const revokeInvite = (id) => body(api.delete(`/admin/teacher-invites/${id}`));

export const auditLog = (params) => body(api.get(`/admin/audit-log${qs(params)}`));
