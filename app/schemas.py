from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class Sex(str, Enum):
    male = "male"
    female = "female"
    other = "other"


Symptom = Literal[
    "chest_pain",
    "shortness_of_breath",
    "palpitations",
    "swelling_legs",
    "fatigue",
    "frequent_urination",
    "excess_thirst",
    "blurred_vision",
    "unexplained_weight_loss",
    "wheezing",
    "persistent_cough",
    "fever",
]

Condition = Literal[
    "hypertension",
    "high_cholesterol",
    "diabetes",
    "prediabetes",
    "asthma",
    "copd",
    "sleep_apnea",
]

FamilyHistory = Literal[
    "heart_disease",
    "diabetes",
    "asthma",
    "copd",
]


class Measurements(BaseModel):
    systolic_bp: Optional[int] = Field(default=None, ge=60, le=260)
    diastolic_bp: Optional[int] = Field(default=None, ge=30, le=160)
    resting_hr: Optional[int] = Field(default=None, ge=30, le=220)
    fasting_glucose_mg_dl: Optional[int] = Field(default=None, ge=40, le=400)
    random_glucose_mg_dl: Optional[int] = Field(default=None, ge=40, le=600)
    resting_spo2: Optional[int] = Field(default=None, ge=50, le=100)


class PredictRequest(BaseModel):
    age: int = Field(ge=0, le=120)
    sex: Sex

    height_cm: Optional[float] = Field(default=None, ge=50, le=250)
    weight_kg: Optional[float] = Field(default=None, ge=2, le=400)

    smoker: bool = False
    alcohol_drinks_per_week: int = Field(default=0, ge=0, le=200)
    activity_minutes_per_week: int = Field(default=0, ge=0, le=5000)
    sleep_hours: float = Field(default=7.0, ge=0.0, le=24.0)

    family_history: List[FamilyHistory] = Field(default_factory=list)
    conditions: List[Condition] = Field(default_factory=list)
    symptoms: List[Symptom] = Field(default_factory=list)
    condition_description: Optional[str] = Field(default=None, max_length=2000)
    measurements: Measurements = Field(default_factory=Measurements)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
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
                    "measurements": {"systolic_bp": 148, "diastolic_bp": 92, "fasting_glucose_mg_dl": 118, "resting_spo2": 94},
                }
            ]
        }
    }


RiskLevel = Literal["low", "moderate", "high", "urgent"]


class RiskResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    level: RiskLevel
    top_contributors: List[str] = Field(default_factory=list)
    preventive_measures: List[str] = Field(default_factory=list)
    recommend_medical_consultation: bool


class PredictResponse(BaseModel):
    risks: Dict[str, RiskResult]
    disclaimer: str


class MedicineRecommendation(BaseModel):
    name: str
    category: str
    reason: str
    priority: Literal["low", "medium", "high"]
    side_effects: List[str] = Field(default_factory=list)


class WellnessRecommendation(BaseModel):
    activity: str
    category: Literal["exercise", "diet", "lifestyle", "stress_management"]
    description: str
    frequency: str
    difficulty_level: Literal["easy", "moderate", "challenging"]
    estimated_benefit: str


class RecommendationResponse(BaseModel):
    medicines: List[MedicineRecommendation]
    wellness_activities: List[WellnessRecommendation]
    lifestyle_changes: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    notes: str

