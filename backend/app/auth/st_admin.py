"""The two SuperTokens calls an administrator needs, in one place (so tests can replace them):
end every session of a user, and remove a user's login identity."""
from supertokens_python.recipe.session.syncio import revoke_all_sessions_for_user
from supertokens_python.syncio import delete_user


def revoke_sessions(supertokens_user_id: str) -> int:
    return len(revoke_all_sessions_for_user(supertokens_user_id))


def delete_identity(supertokens_user_id: str) -> None:
    delete_user(supertokens_user_id)
