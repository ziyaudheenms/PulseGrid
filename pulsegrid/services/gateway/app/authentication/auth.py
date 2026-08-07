from typing import Annotated

from clerk_backend_api import AuthenticateRequestOptions, authenticate_request
from clerk_backend_api.security.types import RequestState
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings

http_bearer = HTTPBearer(auto_error=False)


def require_auth(
    request: Request,
    _creds: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)] = None,
) -> RequestState:
    state = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=settings.CLERK_SECRET_KEY,
            jwt_key=settings.CLERK_JWT_KEY,
            authorized_parties=settings.CLERK_AUTHORIZED_PARTIES,
            accepts_token=["session_token"],
        ),
    )
    if not state.is_signed_in:
        raise HTTPException(
            status_code=401,
            detail=state.reason.name if state.reason else "unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return state    #the returned state is a 'RequestState'
