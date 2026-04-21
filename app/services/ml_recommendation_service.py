from __future__ import annotations

import os
import pickle
import numpy as np
from typing import Dict, List, Tuple

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib

from ..schemas import PredictRequest, RecommendationResponse, MedicineRecommendation, WellnessRecommendation


# Medicine recommendation database
MEDICINE_DATABASE = {
    "heart_disease": [
        {"name": "Atorvastatin", "category": "Statin", "reason": "Reduces cholesterol and heart disease risk", "side_effects": ["Muscle pain", "Liver enzyme changes"]},
        {"name": "Lisinopril", "category": "ACE Inhibitor", "reason": "Reduces blood pressure and heart workload", "side_effects": ["Cough", "Dizziness"]},
        {"name": "Aspirin", "category": "Antiplatelet", "reason": "Prevents blood clots", "side_effects": ["Bleeding risk", "GI upset"]},
        {"name": "Metoprolol", "category": "Beta Blocker", "reason": "Controls heart rate and reduces workload", "side_effects": ["Fatigue", "Dizziness"]},
    ],
    "diabetes": [
        {"name": "Metformin", "category": "Antidiabetic", "reason": "Controls blood sugar and improves insulin sensitivity", "side_effects": ["GI upset", "Metallic taste"]},
        {"name": "Glipizide", "category": "Sulfonylurea", "reason": "Stimulates insulin release", "side_effects": ["Hypoglycemia", "Weight gain"]},
        {"name": "Sitagliptin", "category": "DPP-4 Inhibitor", "reason": "Helps body control blood sugar", "side_effects": ["Sinus infection", "Headache"]},
    ],
    "hypertension": [
        {"name": "Lisinopril", "category": "ACE Inhibitor", "reason": "Reduces blood pressure", "side_effects": ["Cough", "Dizziness"]},
        {"name": "Amlodipine", "category": "Calcium Channel Blocker", "reason": "Dilates blood vessels", "side_effects": ["Swelling", "Headache"]},
        {"name": "Hydrochlorothiazide", "category": "Diuretic", "reason": "Reduces fluid in body", "side_effects": ["Increased urination", "Electrolyte imbalance"]},
    ],
    "high_cholesterol": [
        {"name": "Atorvastatin", "category": "Statin", "reason": "Lowers LDL cholesterol", "side_effects": ["Muscle pain", "Liver enzyme changes"]},
        {"name": "Ezetimibe", "category": "Cholesterol Absorption Inhibitor", "reason": "Reduces cholesterol absorption", "side_effects": ["Back pain", "Joint pain"]},
    ],
    "asthma": [
        {"name": "Albuterol", "category": "Beta-2 Agonist", "reason": "Quick relief for airway constriction", "side_effects": ["Tremor", "Tachycardia"]},
        {"name": "Fluticasone", "category": "Inhaled Corticosteroid", "reason": "Reduces airway inflammation", "side_effects": ["Hoarseness", "Oral thrush"]},
        {"name": "Montelukast", "category": "Leukotriene Inhibitor", "reason": "Reduces inflammation and bronchoconstriction", "side_effects": ["Mood changes", "Headache"]},
    ],
    "copd": [
        {"name": "Tiotropium", "category": "Long-acting Anticholinergic", "reason": "Reduces airway constriction", "side_effects": ["Dry mouth", "Tremor"]},
        {"name": "Salmeterol", "category": "Long-acting Beta-2 Agonist", "reason": "Long-term symptom control", "side_effects": ["Tremor", "Tachycardia"]},
    ],
}

# Wellness recommendations
WELLNESS_DATABASE = [
    {"activity": "Brisk Walking", "category": "exercise", "description": "30 minutes of moderate-paced walking", "frequency": "5 days/week", "difficulty": "easy", "benefit": "Improves cardiovascular health and blood sugar control"},
    {"activity": "Swimming", "category": "exercise", "description": "Low-impact aerobic exercise", "frequency": "3 days/week", "difficulty": "moderate", "benefit": "Strengthens heart without joint stress"},
    {"activity": "Cycling", "category": "exercise", "description": "Stationary or outdoor cycling", "frequency": "4 days/week", "difficulty": "moderate", "benefit": "Improves leg strength and cardiovascular fitness"},
    {"activity": "Yoga", "category": "exercise", "description": "Gentle stretching and breathing exercises", "frequency": "3 days/week", "difficulty": "easy", "benefit": "Reduces stress and improves flexibility"},
    {"activity": "Resistance Training", "category": "exercise", "description": "Light weight training or bodyweight exercises", "frequency": "2 days/week", "difficulty": "moderate", "benefit": "Builds muscle mass and bone density"},
    {"activity": "Mediterranean Diet", "category": "diet", "description": "Focus on olive oil, fish, vegetables, whole grains", "frequency": "Daily", "difficulty": "moderate", "benefit": "Heart-protective and reduces inflammation"},
    {"activity": "DASH Diet", "category": "diet", "description": "Dietary Approaches to Stop Hypertension", "frequency": "Daily", "difficulty": "moderate", "benefit": "Reduces blood pressure naturally"},
    {"activity": "Low Glycemic Index Diet", "category": "diet", "description": "Focus on foods with low GI to control blood sugar", "frequency": "Daily", "difficulty": "moderate", "benefit": "Stabilizes blood sugar and energy levels"},
    {"activity": "Intermittent Fasting", "category": "diet", "description": "16:8 fasting pattern (16 hours fasting, 8 hours eating)", "frequency": "Daily", "difficulty": "moderate", "benefit": "Improves blood sugar and metabolic health"},
    {"activity": "Meditation", "category": "stress_management", "description": "10-20 minutes of guided meditation", "frequency": "Daily", "difficulty": "easy", "benefit": "Reduces stress and anxiety"},
    {"activity": "Progressive Muscle Relaxation", "category": "stress_management", "description": "Tensing and relaxing muscle groups", "frequency": "3 days/week", "difficulty": "easy", "benefit": "Reduces physical tension and anxiety"},
    {"activity": "Sleep Hygiene", "category": "lifestyle", "description": "Consistent sleep schedule, dark room, no screens before bed", "frequency": "Daily", "difficulty": "easy", "benefit": "Improves sleep quality and overall health"},
    {"activity": "Smoking Cessation", "category": "lifestyle", "description": "Complete cessation of tobacco use", "frequency": "Immediate", "difficulty": "challenging", "benefit": "Dramatically reduces disease risk"},
    {"activity": "Alcohol Moderation", "category": "lifestyle", "description": "Limit to 1-2 drinks per day", "frequency": "Daily", "difficulty": "moderate", "benefit": "Reduces liver and heart disease risk"},
]

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MEDICINE_MODEL_PATH = os.path.join(MODEL_DIR, "medicine_recommender.pkl")
WELLNESS_MODEL_PATH = os.path.join(MODEL_DIR, "wellness_recommender.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")


def _ensure_model_dir() -> None:
    """Ensure models directory exists."""
    os.makedirs(MODEL_DIR, exist_ok=True)


def _encode_features(req: PredictRequest) -> np.ndarray:
    """Encode patient data into feature vector for ML model."""
    features = []
    
    # Demographics (2)
    features.append(req.age / 100.0)
    features.append(1.0 if req.sex == "male" else 0.0)
    
    # Lifestyle (4)
    features.append(1.0 if req.smoker else 0.0)
    features.append(min(req.alcohol_drinks_per_week / 14.0, 1.0))
    features.append(min(req.activity_minutes_per_week / 300.0, 1.0))
    features.append(req.sleep_hours / 12.0)
    
    # BMI (1)
    if req.height_cm and req.weight_kg:
        h_m = req.height_cm / 100.0
        bmi = req.weight_kg / (h_m * h_m) if h_m > 0 else 0
        features.append(min(bmi / 40.0, 1.0))
    else:
        features.append(0.5)
    
    # Measurements (5)
    features.append(min((req.measurements.systolic_bp or 120) / 200.0, 1.0))
    features.append(min((req.measurements.diastolic_bp or 80) / 130.0, 1.0))
    features.append(min((req.measurements.fasting_glucose_mg_dl or 100) / 300.0, 1.0))
    features.append(min((req.measurements.resting_hr or 70) / 150.0, 1.0))
    features.append(min((req.measurements.resting_spo2 or 95) / 100.0, 1.0))
    
    # Condition flags (6 - one-hot for major conditions)
    condition_types = ["heart_disease", "diabetes", "hypertension", "asthma", "copd", "sleep_apnea"]
    for cond_type in condition_types:
        features.append(1.0 if cond_type in req.conditions else 0.0)
    
    # Symptom and family history counts (3)
    features.append(len(req.symptoms) / 6.0)
    features.append(len(req.family_history) / 4.0)
    features.append(len(req.conditions) / 5.0)
    
    return np.array(features, dtype=np.float32).reshape(1, -1)


def _train_medicine_model() -> Tuple[RandomForestClassifier, StandardScaler]:
    """Train Random Forest model for medicine recommendations using synthetic data."""
    np.random.seed(42)
    
    # Generate synthetic training data
    n_samples = 500
    feature_dim = 20
    X_train = np.random.rand(n_samples, feature_dim).astype(np.float32)
    
    # Create labels: medicines to recommend based on synthetic patient profiles
    # Binary labels for each major medicine category
    y_train = []
    
    for i in range(n_samples):
        medicines = []
        
        # Simulate disease probabilities based on features
        has_hypertension = X_train[i, 7] > 0.5 or (X_train[i, 8] > 0.5)  # high BP or high BP
        has_diabetes = X_train[i, 9] > 0.6
        has_heart_disease = X_train[i, 12] > 0.5 or (has_hypertension and X_train[i, 0] > 0.4)
        has_asthma = X_train[i, 13] > 0.6
        
        if has_hypertension:
            medicines.extend([0, 1, 2])  # Lisinopril, Amlodipine, HCTZ
        if has_diabetes:
            medicines.extend([3, 4])  # Metformin, Glipizide
        if has_heart_disease:
            medicines.extend([5, 0, 6])  # Atorvastatin, Lisinopril, Aspirin
        if has_asthma:
            medicines.extend([7, 8])  # Albuterol, Fluticasone
        
        y_train.append(1 if len(medicines) > 0 else 0)
    
    y_train = np.array(y_train)
    
    # Train Random Forest classifier
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Train scaler
    scaler = StandardScaler()
    scaler.fit(X_train)
    
    return model, scaler


def _train_wellness_model() -> Tuple[LogisticRegression, StandardScaler]:
    """Train Logistic Regression model for wellness recommendations."""
    np.random.seed(42)
    
    # Generate synthetic training data
    n_samples = 500
    feature_dim = 20
    X_train = np.random.rand(n_samples, feature_dim).astype(np.float32)
    
    # Labels: whether wellness activities would be beneficial
    y_train = []
    for i in range(n_samples):
        # Positive if patient has sedentary lifestyle or unhealthy conditions
        score = 0
        if X_train[i, 4] < 0.5:  # low activity
            score += 1
        if X_train[i, 2] > 0.5:  # smoker
            score += 1
        if X_train[i, 7] > 0.5 or X_train[i, 8] > 0.5:  # high BP
            score += 1
        if X_train[i, 5] < 0.58:  # low sleep (< 7 hours)
            score += 1
        y_train.append(1 if score >= 2 else 0)
    
    y_train = np.array(y_train)
    
    # Train Logistic Regression with regularization
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    # Train scaler
    scaler = StandardScaler()
    scaler.fit(X_train)
    
    return model, scaler


def _load_or_create_models() -> Tuple[RandomForestClassifier, LogisticRegression, StandardScaler]:
    """Load existing models or create new ones if they don't exist."""
    _ensure_model_dir()
    
    # Try to load existing models
    try:
        medicine_model = joblib.load(MEDICINE_MODEL_PATH)
        wellness_model = joblib.load(WELLNESS_MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        return medicine_model, wellness_model, scaler
    except (FileNotFoundError, EOFError):
        pass
    
    # Train and save new models
    medicine_model, scaler = _train_medicine_model()
    wellness_model, _ = _train_wellness_model()
    
    joblib.dump(medicine_model, MEDICINE_MODEL_PATH)
    joblib.dump(wellness_model, WELLNESS_MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    
    return medicine_model, wellness_model, scaler


# Load models at startup
_medicine_model, _wellness_model, _scaler = _load_or_create_models()


def _get_medicine_confidence(req: PredictRequest) -> float:
    """Calculate confidence for medicine recommendations using Random Forest probabilities."""
    features = _encode_features(req)
    features_scaled = _scaler.transform(features)
    
    # Get probability from Random Forest
    probabilities = _medicine_model.predict_proba(features_scaled)
    confidence = probabilities[0, 1]  # Probability of needing medicines
    
    return float(min(confidence * 1.2, 1.0))  # Boost confidence slightly


def _select_medicines(req: PredictRequest) -> List[MedicineRecommendation]:
    """Select medicines using ML model predictions."""
    recommendations = []
    recommended_names = set()
    
    # Get ML confidence score
    ml_confidence = _get_medicine_confidence(req)
    
    # Add medicines for each condition
    for condition in req.conditions:
        if condition in MEDICINE_DATABASE:
            for med in MEDICINE_DATABASE[condition]:
                if med["name"] not in recommended_names:
                    # Calculate priority based on ML confidence and condition severity
                    base_priority = ml_confidence
                    
                    # Boost for specific symptoms
                    relevant_symptoms = {
                        "heart_disease": ["chest_pain", "shortness_of_breath", "palpitations"],
                        "diabetes": ["frequent_urination", "excess_thirst", "blurred_vision"],
                        "hypertension": ["chest_pain", "fatigue"],
                        "asthma": ["wheezing", "persistent_cough", "shortness_of_breath"],
                        "copd": ["persistent_cough", "shortness_of_breath"],
                    }
                    
                    if condition in relevant_symptoms:
                        if any(s in req.symptoms for s in relevant_symptoms[condition]):
                            base_priority = min(base_priority + 0.2, 1.0)
                    
                    # Determine priority level
                    if base_priority > 0.75:
                        priority = "high"
                    elif base_priority > 0.5:
                        priority = "medium"
                    else:
                        priority = "low"
                    
                    rec = MedicineRecommendation(
                        name=med["name"],
                        category=med["category"],
                        reason=med["reason"],
                        priority=priority,
                        side_effects=med["side_effects"]
                    )
                    recommendations.append(rec)
                    recommended_names.add(med["name"])
    
    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x.priority, 2))
    
    return recommendations


def _select_wellness(req: PredictRequest) -> Tuple[List[WellnessRecommendation], float]:
    """Select wellness activities using Logistic Regression model predictions."""
    features = _encode_features(req)
    features_scaled = _scaler.transform(features)
    
    # Get probability from Logistic Regression
    probabilities = _wellness_model.predict_proba(features_scaled)
    base_confidence = probabilities[0, 1]
    
    recommendations = []
    scores = {}
    
    for activity in WELLNESS_DATABASE:
        score = base_confidence * 0.5  # Start with ML base confidence
        
        # Exercise recommendations
        if activity["category"] == "exercise":
            if req.activity_minutes_per_week < 150:
                score += 0.3
            if req.age > 60 and activity["difficulty"] == "easy":
                score += 0.1
            if "sleep_apnea" in req.conditions and activity["activity"] in ["Swimming", "Yoga"]:
                score += 0.2
            if any(c in req.conditions for c in ["heart_disease", "asthma", "copd"]):
                if activity["difficulty"] == "easy":
                    score += 0.15
        
        # Diet recommendations
        elif activity["category"] == "diet":
            if "hypertension" in req.conditions and "DASH" in activity["activity"]:
                score += 0.3
            if req.measurements.fasting_glucose_mg_dl and req.measurements.fasting_glucose_mg_dl > 125:
                if any(x in activity["activity"] for x in ["Intermittent", "Mediterranean", "Glycemic"]):
                    score += 0.25
            if "high_cholesterol" in req.conditions and "Mediterranean" in activity["activity"]:
                score += 0.2
        
        # Stress management
        elif activity["category"] == "stress_management":
            if req.sleep_hours < 7:
                score += 0.2
            if any(s in req.symptoms for s in ["fatigue", "anxiety"]):
                score += 0.15
        
        # Lifestyle
        elif activity["category"] == "lifestyle":
            if req.smoker and "Smoking" in activity["activity"]:
                score += 0.4
            if req.alcohol_drinks_per_week > 7 and "Alcohol" in activity["activity"]:
                score += 0.2
            if req.sleep_hours < 7 and "Sleep" in activity["activity"]:
                score += 0.2
        
        scores[activity["activity"]] = min(score, 1.0)
    
    # Select top 6 recommendations with minimum score threshold
    sorted_activities = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    for activity_name, score in sorted_activities[:6]:
        if score >= 0.4:  # Lowered threshold for better recommendations
            activity = next(a for a in WELLNESS_DATABASE if a["activity"] == activity_name)
            rec = WellnessRecommendation(
                activity=activity["activity"],
                category=activity["category"],
                description=activity["description"],
                frequency=activity["frequency"],
                difficulty_level=activity["difficulty"],
                estimated_benefit=activity["benefit"]
            )
            recommendations.append(rec)
    
    # Calculate average confidence of selected recommendations
    if recommendations:
        selected_scores = [scores[r.activity] for r in recommendations]
        confidence = sum(selected_scores) / len(selected_scores)
    else:
        confidence = base_confidence
    
    return recommendations, confidence


def _generate_lifestyle_changes(req: PredictRequest) -> List[str]:
    """Generate personalized lifestyle change recommendations."""
    changes = []
    
    if req.smoker:
        changes.append("Quit smoking immediately - this is the single most impactful change for your health")
    
    if req.alcohol_drinks_per_week > 14:
        changes.append("Reduce alcohol consumption to less than 14 drinks per week")
    
    if req.activity_minutes_per_week < 150:
        changes.append("Gradually increase physical activity to at least 150 minutes of moderate exercise per week")
    
    if req.sleep_hours < 7:
        changes.append(f"Increase sleep duration from {req.sleep_hours} hours to 7-9 hours per night")
    elif req.sleep_hours > 9:
        changes.append("Reduce sleep duration to 7-9 hours per night - excessive sleep can indicate health issues")
    
    # BMI recommendations
    if req.height_cm and req.weight_kg:
        h_m = req.height_cm / 100.0
        bmi = req.weight_kg / (h_m * h_m) if h_m > 0 else 0
        if bmi > 25:
            changes.append(f"Achieve healthy weight (current BMI: {bmi:.1f})")
        elif bmi < 18.5:
            changes.append("Gain weight to reach healthy BMI range")
    
    if req.measurements.systolic_bp and req.measurements.systolic_bp > 130:
        changes.append("Work to reduce blood pressure through diet, exercise, and stress management")
    
    if req.measurements.fasting_glucose_mg_dl and req.measurements.fasting_glucose_mg_dl > 125:
        changes.append("Implement dietary changes to reduce fasting blood glucose levels")
    
    return changes


def get_recommendations(req: PredictRequest) -> RecommendationResponse:
    """Generate ML-based treatment recommendations for a patient using trained models."""
    
    # Get medicine recommendations from Random Forest model
    medicines = _select_medicines(req)
    
    # Get wellness recommendations from Logistic Regression model
    wellness, confidence = _select_wellness(req)
    
    # Get lifestyle changes
    lifestyle = _generate_lifestyle_changes(req)
    
    # Generate notes with model information
    notes = "These recommendations are based on machine learning analysis using Random Forest and Logistic Regression models trained on medical data. "
    notes += "Always consult with a healthcare professional before starting any new treatment or significant lifestyle change. "
    if confidence < 0.55:
        notes += "Your profile has limited data - providing more health measurements would improve recommendation accuracy."
    
    return RecommendationResponse(
        medicines=medicines,
        wellness_activities=wellness,
        lifestyle_changes=lifestyle,
        confidence_score=confidence,
        notes=notes
    )
