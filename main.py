from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, Annotated

import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi_users import FastAPIUsers
from pydantic import BaseModel, Field

from fastapi import FastAPI, Request, status, Depends, Header
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import ResponseValidationError, HTTPException
from fastapi.responses import JSONResponse

from auth.auth import auth_backend, SECRET
from auth.database import User
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate

app = FastAPI(
    title="Trading App"
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# def fake_decode_token(token):
#     # This doesn't provide any security at all
#     # Check the next version
#     user = get_user(fake_users_db, token)
#     return user

oauth2_scheme = fastapi_users.current_user()
# @app.get("/protected-route")
# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     # user = fake_decode_token(token)
#     # if not user:
#     #     raise HTTPException(
#     #     status_code=status.HTTP_401_UNAUTHORIZED,
#     #     detail="Invalid authentication credentials",
#     #     headers={"WWW-Authenticate": "Bearer"},
#     #     )
#     return 'user'

async def get_enabled_backends(request: Request):
    """Return the enabled dependencies following custom logic."""
    if request.url.path == "/protected-route-only-jwt":
        return [auth_backend]


current_active_user = fastapi_users.current_user(active=True, get_enabled_backends=get_enabled_backends)

@app.get("/protected-route-only-jwt")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.email}. You are authenticated with a JWT."


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"
