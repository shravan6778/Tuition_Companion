import SuperTokens from "supertokens-web-js";
import EmailPassword from "supertokens-web-js/recipe/emailpassword";
import Session from "supertokens-web-js/recipe/session";

SuperTokens.init({
  appInfo: {
    appName: "Tuition Companion",
    apiDomain: import.meta.env.VITE_API_URL,
    apiBasePath: "/auth",
  },
  recipeList: [Session.init(), EmailPassword.init()],
});