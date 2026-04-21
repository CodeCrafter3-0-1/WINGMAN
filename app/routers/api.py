from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr

from ..auth import authenticate, login_user, logout_user
from ..schemas import PredictRequest, PredictResponse, RecommendationResponse
from ..services.chatbot_service import generate_chat_reply
from ..services.risk_service import build_prediction
from ..services.ml_recommendation_service import get_recommendations

router = APIRouter(prefix="/api", tags=["api"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChatRequest(BaseModel):
    message: str


@router.get("/health")
def health() -> dict:
    return {"ok": True}


@router.get("/example")
def example_request() -> dict:
    return {
        "age": 52,
        "sex": "male",
        "height_cm": 175,
        "weight_kg": 92,
        "smoker": True,
        "alcohol_drinks_per_week": 6,
        "activity_minutes_per_week": 60,
        "sleep_hours": 6.0,
        "family_history": ["heart_disease", "diabetes"],
        "conditions": ["hypertension"],
        "symptoms": ["chest_pain", "shortness_of_breath", "fatigue"],
        "condition_description": "I've been experiencing chest pain and shortness of breath for the past 2 weeks. The pain is worse when I exert myself and I've noticed some swelling in my ankles recently.",
        "measurements": {
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "fasting_glucose_mg_dl": None,
            "random_glucose_mg_dl": None,
            "resting_hr": None,
            "resting_spo2": None,
        },
    }


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    return build_prediction(req)


@router.post("/recommendations", response_model=RecommendationResponse)
def recommendations(req: PredictRequest) -> RecommendationResponse:
    """Generate ML-based personalized medicine and wellness recommendations."""
    return get_recommendations(req)


@router.post("/auth/login")
def login(request: Request, payload: LoginRequest) -> dict:
    if not authenticate(payload.email, payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    login_user(request, payload.email)
    return {"ok": True, "email": payload.email}


@router.post("/auth/logout")
def logout(request: Request) -> dict:
    logout_user(request)
    return {"ok": True}


@router.get("/auth/me")
def me(request: Request) -> dict:
    email = request.session.get("user_email")
    return {"authenticated": bool(email), "email": email}


@router.post("/chat")
def chat(payload: ChatRequest) -> dict:
    return {"reply": generate_chat_reply(payload.message)}

