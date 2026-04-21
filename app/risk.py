from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from .schemas import PredictRequest


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def _bmi(req: PredictRequest) -> float | None:
    if req.height_cm is None or req.weight_kg is None:
        return None
    h_m = req.height_cm / 100.0
    if h_m <= 0:
        return None
    return req.weight_kg / (h_m * h_m)


def _has_any(items: Iterable[str], *candidates: str) -> bool:
    s = set(items)
    return any(c in s for c in candidates)


@dataclass(frozen=True)
class RiskOutput:
    score: float
    level: str
    contributors: List[str]
    preventive: List[str]
    consult: bool


def _bucket(score: float, urgent: bool = False) -> Tuple[str, bool]:
    if urgent:
        return "urgent", True
    if score >= 0.70:
        return "high", True
    if score >= 0.35:
        return "moderate", True
    return "low", False


def _data_completeness(req: PredictRequest) -> float:
    """Return a completeness ratio from 0 to 1 for key risk inputs."""
    present = 0
    total = 0

    checks = [
        req.height_cm is not None,
        req.weight_kg is not None,
        req.measurements.systolic_bp is not None,
        req.measurements.diastolic_bp is not None,
        req.measurements.fasting_glucose_mg_dl is not None,
        req.measurements.random_glucose_mg_dl is not None,
        req.measurements.resting_spo2 is not None,
        req.measurements.resting_hr is not None,
        len(req.symptoms) > 0,
        len(req.conditions) > 0,
        len(req.family_history) > 0,
    ]
    for flag in checks:
        total += 1
        if flag:
            present += 1
    return present / total if total else 0.0


def _calibrate_score(raw_score: float, req: PredictRequest, urgent: bool) -> float:
    """
    Calibrate score based on data completeness:
    - sparse data -> reduce score slightly (avoid overestimation)
    - rich data -> increase score slightly (more confident signal)
    Urgent flags keep raw score unchanged.
    """
    if urgent:
        return raw_score
    c = _data_completeness(req)
    if c < 0.35:
        factor = 0.9
    elif c < 0.6:
        factor = 0.96
    elif c >= 0.82:
        factor = 1.08
    else:
        factor = 1.0
    return max(0.0, min(1.0, raw_score * factor))


def heart_risk(req: PredictRequest) -> RiskOutput:
    contrib: List[str] = []
    tips: List[str] = []

    x = -2.2
    x += 0.03 * max(req.age - 35, 0)
    if req.smoker:
        x += 0.7
        contrib.append("Smoker")
        tips.append("If you smoke, make a quit plan and consider cessation supports.")

    if "heart_disease" in req.family_history:
        x += 0.5
        contrib.append("Family history of heart disease")

    if "hypertension" in req.conditions:
        x += 0.7
        contrib.append("Known hypertension")
        tips.append("Monitor blood pressure and follow clinician guidance on targets.")

    if "high_cholesterol" in req.conditions:
        x += 0.4
        contrib.append("Known high cholesterol")
        tips.append("Discuss lipid testing and diet changes (reduce saturated fats).")

    m = req.measurements
    urgent = False
    if m.systolic_bp is not None and m.systolic_bp >= 160:
        x += 0.6
        contrib.append(f"High systolic BP ({m.systolic_bp})")
    if m.diastolic_bp is not None and m.diastolic_bp >= 100:
        x += 0.5
        contrib.append(f"High diastolic BP ({m.diastolic_bp})")
    if m.resting_hr is not None and m.resting_hr >= 100:
        x += 0.35
        contrib.append(f"Elevated resting HR ({m.resting_hr})")
        tips.append("Track resting heart rate trends and discuss persistent elevation with a clinician.")

    if _has_any(req.symptoms, "chest_pain", "shortness_of_breath", "palpitations"):
        x += 0.9
        contrib.append("Cardiac-related symptoms reported")
        tips.append("If symptoms are new, worsening, or severe, seek urgent care.")
        if "chest_pain" in req.symptoms and "shortness_of_breath" in req.symptoms:
            urgent = True

    bmi = _bmi(req)
    if bmi is not None and bmi >= 30:
        x += 0.4
        contrib.append(f"BMI in obese range ({bmi:.1f})")
        tips.append("Aim for gradual weight loss via diet + activity (if safe).")

    if req.activity_minutes_per_week < 75:
        x += 0.3
        contrib.append("Low physical activity")
        tips.append("Target 150 min/week moderate activity (as tolerated).")

    raw_score = _sigmoid(x)
    score = _calibrate_score(raw_score, req, urgent=urgent)
    level, consult = _bucket(score, urgent=urgent)
    if not tips:
        tips = ["Maintain a heart-healthy diet, regular activity, and routine checkups."]

    return RiskOutput(score=score, level=level, contributors=contrib[:5], preventive=tips[:6], consult=consult)


def diabetes_risk(req: PredictRequest) -> RiskOutput:
    contrib: List[str] = []
    tips: List[str] = []

    x = -2.4
    x += 0.028 * max(req.age - 40, 0)

    bmi = _bmi(req)
    if bmi is not None:
        if bmi >= 30:
            x += 0.9
            contrib.append(f"BMI in obese range ({bmi:.1f})")
        elif bmi >= 25:
            x += 0.5
            contrib.append(f"BMI in overweight range ({bmi:.1f})")

    if "diabetes" in req.family_history:
        x += 0.6
        contrib.append("Family history of diabetes")

    if _has_any(req.conditions, "prediabetes"):
        x += 1.0
        contrib.append("Known prediabetes")

    m = req.measurements
    urgent = False
    if m.fasting_glucose_mg_dl is not None:
        if m.fasting_glucose_mg_dl >= 126:
            x += 1.4
            contrib.append(f"High fasting glucose ({m.fasting_glucose_mg_dl})")
        elif m.fasting_glucose_mg_dl >= 100:
            x += 0.8
            contrib.append(f"Elevated fasting glucose ({m.fasting_glucose_mg_dl})")

    if m.random_glucose_mg_dl is not None and m.random_glucose_mg_dl >= 200:
        x += 1.2
        contrib.append(f"High random glucose ({m.random_glucose_mg_dl})")

    if _has_any(req.symptoms, "frequent_urination", "excess_thirst", "blurred_vision", "unexplained_weight_loss"):
        x += 0.8
        contrib.append("Diabetes-related symptoms reported")
        tips.append("If symptoms are significant or worsening, seek clinical evaluation soon.")
        if "unexplained_weight_loss" in req.symptoms and (
            "excess_thirst" in req.symptoms or "frequent_urination" in req.symptoms
        ):
            urgent = True

    if req.activity_minutes_per_week < 75:
        x += 0.25
        contrib.append("Low physical activity")

    if req.sleep_hours < 6:
        x += 0.2
        contrib.append("Short sleep duration")
        tips.append("Aim for 7–9 hours sleep; poor sleep can worsen metabolic risk.")

    tips.extend(
        [
            "Favor high-fiber foods (vegetables, legumes, whole grains) and minimize sugary drinks.",
            "If available, consider HbA1c/fasting glucose testing with a clinician.",
        ]
    )

    raw_score = _sigmoid(x)
    score = _calibrate_score(raw_score, req, urgent=urgent)
    level, consult = _bucket(score, urgent=urgent)
    return RiskOutput(score=score, level=level, contributors=contrib[:5], preventive=tips[:6], consult=consult)


def respiratory_risk(req: PredictRequest) -> RiskOutput:
    contrib: List[str] = []
    tips: List[str] = []

    x = -2.3
    x += 0.02 * max(req.age - 40, 0)

    if req.smoker:
        x += 0.9
        contrib.append("Smoker")
        tips.append("Quitting smoking is the single biggest step to reduce respiratory risk.")

    if _has_any(req.conditions, "asthma", "copd", "sleep_apnea"):
        x += 0.9
        contrib.append("Known respiratory condition")
        tips.append("Ensure you have an action plan and take prescribed meds as directed.")

    if _has_any(req.family_history, "asthma", "copd"):
        x += 0.3
        contrib.append("Family history of respiratory disease")

    m = req.measurements
    urgent = False
    if m.resting_spo2 is not None and m.resting_spo2 <= 92:
        x += 1.5
        contrib.append(f"Low resting SpO2 ({m.resting_spo2})")
        urgent = True
    elif m.resting_spo2 is not None and m.resting_spo2 <= 94:
        x += 0.8
        contrib.append(f"Borderline resting SpO2 ({m.resting_spo2})")
    if m.resting_hr is not None and m.resting_hr >= 110:
        x += 0.25
        contrib.append(f"High resting HR ({m.resting_hr})")

    if _has_any(req.symptoms, "shortness_of_breath", "wheezing", "persistent_cough", "fever"):
        x += 0.9
        contrib.append("Respiratory symptoms reported")
        tips.append("If breathing difficulty is severe, seek urgent care.")
        if "shortness_of_breath" in req.symptoms and (m.resting_spo2 is not None and m.resting_spo2 <= 94):
            urgent = True

    tips.extend(
        [
            "Avoid smoke/irritants; consider masking in polluted environments.",
            "Stay up to date on vaccinations (as appropriate) and hand hygiene during outbreaks.",
        ]
    )

    raw_score = _sigmoid(x)
    score = _calibrate_score(raw_score, req, urgent=urgent)
    level, consult = _bucket(score, urgent=urgent)
    return RiskOutput(score=score, level=level, contributors=contrib[:5], preventive=tips[:6], consult=consult)


def stroke_risk(req: PredictRequest) -> RiskOutput:
    contrib: List[str] = []
    tips: List[str] = []

    # Not clinically validated. Heuristic: age + BP + smoking + diabetes-related factors + symptoms overlap.
    x = -2.5
    x += 0.03 * max(req.age - 45, 0)

    if req.smoker:
        x += 0.55
        contrib.append("Smoker")
        tips.append("If you smoke, make a quit plan and consider cessation supports.")

    if "hypertension" in req.conditions:
        x += 0.7
        contrib.append("Known hypertension")
        tips.append("Control blood pressure; ask about home BP monitoring.")

    if _has_any(req.conditions, "diabetes", "prediabetes"):
        x += 0.45
        contrib.append("Diabetes / prediabetes")
        tips.append("Consider HbA1c/fasting glucose testing and nutrition changes.")

    if "heart_disease" in req.family_history:
        x += 0.25
        contrib.append("Family history of heart disease")

    m = req.measurements
    urgent = False
    if m.systolic_bp is not None and m.systolic_bp >= 180:
        x += 0.8
        contrib.append(f"Very high systolic BP ({m.systolic_bp})")
        urgent = True
    elif m.systolic_bp is not None and m.systolic_bp >= 160:
        x += 0.55
        contrib.append(f"High systolic BP ({m.systolic_bp})")

    if m.diastolic_bp is not None and m.diastolic_bp >= 110:
        x += 0.6
        contrib.append(f"Very high diastolic BP ({m.diastolic_bp})")
        urgent = True
    elif m.diastolic_bp is not None and m.diastolic_bp >= 100:
        x += 0.4
        contrib.append(f"High diastolic BP ({m.diastolic_bp})")
    if m.resting_hr is not None and m.resting_hr >= 110:
        x += 0.3
        contrib.append(f"High resting HR ({m.resting_hr})")

    # We don't have neuro-specific symptoms in schema; use severe cardiopulmonary symptoms as a proxy for "urgent evaluation needed"
    # for this MVP only.
    if _has_any(req.symptoms, "chest_pain", "shortness_of_breath", "palpitations"):
        x += 0.35
        contrib.append("Concerning symptoms reported")
        tips.append("If symptoms are sudden/severe or you feel faint, seek urgent care.")

    bmi = _bmi(req)
    if bmi is not None and bmi >= 30:
        x += 0.35
        contrib.append(f"BMI in obese range ({bmi:.1f})")
        tips.append("Aim for gradual weight loss via diet + activity (if safe).")

    if req.activity_minutes_per_week < 75:
        x += 0.2
        contrib.append("Low physical activity")
        tips.append("Target 150 min/week moderate activity (as tolerated).")

    tips.extend(
        [
            "Limit salt and prioritize fruits/vegetables; consider a DASH-style diet.",
            "Discuss cholesterol testing and cardiovascular risk with a clinician.",
        ]
    )

    raw_score = _sigmoid(x)
    score = _calibrate_score(raw_score, req, urgent=urgent)
    level, consult = _bucket(score, urgent=urgent)
    return RiskOutput(score=score, level=level, contributors=contrib[:5], preventive=tips[:6], consult=consult)


def kidney_risk(req: PredictRequest) -> RiskOutput:
    contrib: List[str] = []
    tips: List[str] = []

    # Heuristic: hypertension + diabetes + age + obesity -> higher kidney disease risk.
    x = -2.6
    x += 0.02 * max(req.age - 50, 0)

    if "hypertension" in req.conditions:
        x += 0.9
        contrib.append("Known hypertension")
        tips.append("Keep blood pressure controlled; kidney risk rises with uncontrolled BP.")

    if _has_any(req.conditions, "diabetes", "prediabetes"):
        x += 0.85
        contrib.append("Diabetes / prediabetes")
        tips.append("Control blood sugar; ask about annual kidney screening (urine albumin, eGFR).")

    bmi = _bmi(req)
    if bmi is not None and bmi >= 30:
        x += 0.35
        contrib.append(f"BMI in obese range ({bmi:.1f})")

    m = req.measurements
    if m.systolic_bp is not None and m.systolic_bp >= 160:
        x += 0.35
        contrib.append(f"High systolic BP ({m.systolic_bp})")

    if m.fasting_glucose_mg_dl is not None and m.fasting_glucose_mg_dl >= 126:
        x += 0.5
        contrib.append(f"High fasting glucose ({m.fasting_glucose_mg_dl})")

    if req.smoker:
        x += 0.25
        contrib.append("Smoker")

    tips.extend(
        [
            "Ask for kidney tests: creatinine/eGFR and urine albumin-to-creatinine ratio (UACR).",
            "Avoid frequent NSAID use unless advised; stay hydrated (as appropriate).",
            "If you have diabetes or hypertension, schedule regular follow-ups.",
        ]
    )

    raw_score = _sigmoid(x)
    score = _calibrate_score(raw_score, req, urgent=False)
    level, consult = _bucket(score)
    return RiskOutput(score=score, level=level, contributors=contrib[:5], preventive=tips[:6], consult=consult)


def metabolic_liver_risk(req: PredictRequest) -> RiskOutput:
    contrib: List[str] = []
    tips: List[str] = []

    # Heuristic for metabolic-associated fatty liver risk: BMI + prediabetes/diabetes + inactivity + alcohol.
    x = -2.7
    x += 0.015 * max(req.age - 35, 0)

    bmi = _bmi(req)
    if bmi is not None:
        if bmi >= 30:
            x += 1.0
            contrib.append(f"BMI in obese range ({bmi:.1f})")
        elif bmi >= 25:
            x += 0.6
            contrib.append(f"BMI in overweight range ({bmi:.1f})")

    if _has_any(req.conditions, "diabetes", "prediabetes"):
        x += 0.75
        contrib.append("Diabetes / prediabetes")

    if req.activity_minutes_per_week < 75:
        x += 0.3
        contrib.append("Low physical activity")

    if req.alcohol_drinks_per_week >= 14:
        x += 0.6
        contrib.append(f"Higher alcohol intake ({req.alcohol_drinks_per_week}/week)")
        tips.append("Consider reducing alcohol intake; discuss safe limits with a clinician.")
    elif req.alcohol_drinks_per_week >= 7:
        x += 0.25
        contrib.append(f"Moderate alcohol intake ({req.alcohol_drinks_per_week}/week)")

    tips.extend(
        [
            "If concerned, ask about liver enzymes (ALT/AST) and ultrasound if appropriate.",
            "Prioritize weight management and regular activity; even 5–10% weight loss can help.",
            "Choose high-fiber foods and reduce sugary drinks/refined carbs.",
        ]
    )

    raw_score = _sigmoid(x)
    score = _calibrate_score(raw_score, req, urgent=False)
    level, consult = _bucket(score)
    return RiskOutput(score=score, level=level, contributors=contrib[:5], preventive=tips[:6], consult=consult)

