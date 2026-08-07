from typing import Annotated
from clerk_backend_api.security.types import RequestState
from fastapi import Depends, HTTPException

from authentication.auth import require_auth

def require_system_role(role: str):
    """Check role for the user's ACTIVE organization (the one in `o.rol`).

    Pass the role without the `org:` prefix (e.g., `"admin"`, `"member"`) to
    match what Clerk stores in the claim.
    """
    def _check(
        state: Annotated[RequestState, Depends(require_auth)],
    ) -> RequestState:
        if state.payload.get("role") != role:
            raise HTTPException(status_code=403, detail=f"Access denied: required role '{role}', but got '{state.payload.get('role')}'")
        return state
    return _check
