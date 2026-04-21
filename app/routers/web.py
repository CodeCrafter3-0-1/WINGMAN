from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(tags=["web"])


@router.get("/")
def landing(request: Request):
    if request.session.get("user_email"):
        return RedirectResponse(url="/introduction", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@router.get("/login")
def login_page(request: Request):
    if request.session.get("user_email"):
        return RedirectResponse(url="/introduction", status_code=302)
    return templates.TemplateResponse(request, "login.html", {})


@router.get("/introduction")
def introduction_page(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "introduction.html", {"email": email})


@router.get("/dashboard")
def dashboard_page(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "dashboard.html", {"email": email})


@router.get("/dashboard/results")
def dashboard_results_page(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "dashboard_results.html", {"email": email})


@router.get("/recommended-medicines")
def recommended_medicines_page(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "recommended_medicines.html", {"email": email})


@router.get("/care-plan")
def care_plan_page(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "care_plan.html", {"email": email})


@router.get("/wellness-program")
def wellness_program_page(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "wellness_program.html", {"email": email})


@router.get("/faq-support")
def faq_support_page(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "faq_support.html", {"email": email})


@router.get("/terms-and-conditions")
def terms_and_conditions_page(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "terms_and_conditions.html", {"email": email})


@router.get("/verification-quality")
def verification_quality_page(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "verification_quality.html", {"email": email})


@router.get("/chatbot")
def chatbot_page(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "chatbot.html", {"email": email})

