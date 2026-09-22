export const normalizePhone = (p) => p.replace(/[\s\-()]/g, "");
export const phoneToEmail = (p) => `${normalizePhone(p).replace(/^\+/, "")}@phone.tuition-companion.app`;