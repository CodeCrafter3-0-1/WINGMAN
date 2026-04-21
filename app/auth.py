from __future__ import annotations

from fastapi import HTTPException, Request, status

DEMO_USERS = {
    "admin@example.com": "admin123",
    "doctor@example.com": "doctor123",
}


def login_user(request: Request, email: str) -> None:
    request.session["user_email"] = email


def logout_user(request: Request) -> None:
    request.session.clear()


def authenticate(email: str, password: str) -> bool:
    return DEMO_USERS.get(email) == password


def get_current_user(request: Request) -> str:
    email = request.session.get("user_email")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
    return str(email)

