from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_token, hash_password, verify_password
from app.db import USERS
from app.deps import current_user
from app.schemas import RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: RegisterIn):
    email = data.email.lower()
    if email in USERS:
        raise HTTPException(409, "Email already registered")
    USERS[email] = {"email": email, "name": data.name,
                    "password": hash_password(data.password), "role": "analyst"}
    return TokenOut(access_token=create_token(email, "analyst"), role="analyst")


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = USERS.get(form.username.lower())
    if not user or not verify_password(form.password, user["password"]):
        raise HTTPException(401, "Incorrect email or password")
    return TokenOut(access_token=create_token(user["email"], user["role"]), role=user["role"])


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(current_user)):
    return user