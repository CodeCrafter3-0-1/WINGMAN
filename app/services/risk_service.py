from __future__ import annotations

from ..risk import diabetes_risk, heart_risk, kidney_risk, metabolic_liver_risk, respiratory_risk, stroke_risk
from ..schemas import PredictRequest, PredictResponse, RiskResult


def build_prediction(req: PredictRequest) -> PredictResponse:
    heart = heart_risk(req)
    diab = diabetes_risk(req)
    resp = respiratory_risk(req)
    stroke = stroke_risk(req)
    kidney = kidney_risk(req)
    liver = metabolic_liver_risk(req)

    risks = {
        "heart_disease": RiskResult(
            score=round(heart.score, 4),
            level=heart.level,  # type: ignore[arg-type]
            top_contributors=heart.contributors,
            preventive_measures=heart.preventive,
            recommend_medical_consultation=heart.consult,
        ),
        "diabetes": RiskResult(
            score=round(diab.score, 4),
            level=diab.level,  # type: ignore[arg-type]
            top_contributors=diab.contributors,
            preventive_measures=diab.preventive,
            recommend_medical_consultation=diab.consult,
        ),
        "respiratory_disorder": RiskResult(
            score=round(resp.score, 4),
            level=resp.level,  # type: ignore[arg-type]
            top_contributors=resp.contributors,
            preventive_measures=resp.preventive,
            recommend_medical_consultation=resp.consult,
        ),
        "stroke": RiskResult(
            score=round(stroke.score, 4),
            level=stroke.level,  # type: ignore[arg-type]
            top_contributors=stroke.contributors,
            preventive_measures=stroke.preventive,
            recommend_medical_consultation=stroke.consult,
        ),
        "kidney_disease": RiskResult(
            score=round(kidney.score, 4),
            level=kidney.level,  # type: ignore[arg-type]
            top_contributors=kidney.contributors,
            preventive_measures=kidney.preventive,
            recommend_medical_consultation=kidney.consult,
        ),
        "metabolic_liver_risk": RiskResult(
            score=round(liver.score, 4),
            level=liver.level,  # type: ignore[arg-type]
            top_contributors=liver.contributors,
            preventive_measures=liver.preventive,
            recommend_medical_consultation=liver.consult,
        ),
    }

    return PredictResponse(
        risks=risks,
        disclaimer=(
            "This tool provides informational risk estimates only and is not a diagnosis. "
            "If you have severe symptoms (e.g., chest pain, severe shortness of breath), seek urgent medical care."
        ),
    )

