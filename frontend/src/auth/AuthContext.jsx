import { createContext, useContext, useEffect, useState } from "react";
import { signIn, signUp } from "supertokens-web-js/recipe/emailpassword";
import {
  doesSessionExist,
  signOut as stSignOut,
} from "supertokens-web-js/recipe/session";
import "./supertokensInit";
import { api } from "../shared/api";
import { normalizePhone, phoneToEmail } from "./phone";

const AuthCtx = createContext(null);
export const useAuth = () => useContext(AuthCtx);

export function AuthProvider({ children }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      if (await doesSessionExist()) {
        try {
          setProfile(await api("/auth/me"));
        } catch {
          setProfile(null);
        }
      }
      setLoading(false);
    })();
  }, []);

  async function login(phone, password) {
    const response = await signIn({
      formFields: [
        { id: "email", value: phoneToEmail(phone) },
        { id: "password", value: password },
      ],
    });
    if (response.status !== "OK") {
      throw new Error("Invalid phone number or password"); // generic on purpose
    }
    const me = await api("/auth/me");
    setProfile(me);
    return me;
  }

  async function signup({ name, phone, password, role }) {
    const normalized = normalizePhone(phone);
    const response = await signUp({
      formFields: [
        { id: "email", value: phoneToEmail(normalized) },
        { id: "password", value: password },
        { id: "name", value: name },
        { id: "phone", value: normalized },
        { id: "role", value: role },
      ],
    });
    if (response.status !== "OK") {
      const msg =
        response.status === "FIELD_ERROR"
          ? response.formFields[0]?.error
          : response.status === "GENERAL_ERROR"
            ? response.message
            : "Could not create account with these details";
      throw new Error(msg);
    }
    const me = await api("/auth/me");
    setProfile(me);
    return me;
  }

  async function logout() {
    await stSignOut();
    setProfile(null);
  }

  return (
    <AuthCtx.Provider value={{ profile, loading, login, signup, logout }}>
      {children}
    </AuthCtx.Provider>
  );
}
