const USERNAME_RE = /^[a-z0-9_]{3,30}$/;
const PHONE_RE = /^\+?[0-9]{10,15}$/;

export function normalizeUsername(value) {
  const v = value.trim().toLowerCase();
  if (!USERNAME_RE.test(v)) {
    throw new Error("Username must be 3-30 characters: lowercase letters, numbers, underscore only");
  }
  return v;
}

export function usernameToEmail(username) {
  return `${username}@user.tuition-companion.app`;
}

export function normalizePhone(value) {
  const v = value.replace(/[\s\-()]/g, "");
  if (!PHONE_RE.test(v)) {
    throw new Error("Enter a valid phone number");
  }
  return v;
}