# ML Models Quick Start Guide

## 🚀 Getting Started with the ML Recommendation System

This guide explains how to use HealthBot's new machine learning-powered recommendation system.

---

## 📦 What You Need

Make sure you have installed all dependencies:

```bash
pip install -r requirements.txt
```

Key packages:
- `scikit-learn>=1.3.0` - Machine Learning library
- `numpy>=1.24.0` - Numerical computing
- `joblib>=1.3.0` - Model persistence

---

## 🤖 ML Models Overview

HealthBot uses **2 trained ML models**:

1. **Random Forest Classifier** → Medicine Recommendations
2. **Logistic Regression** → Wellness Activity Recommendations

See [ML_MODELS.md](ML_MODELS.md) for technical details.

---

## 🎯 Using the ML API

### Endpoint: `/api/recommendations`

**Method:** `POST`

**Request Body:**
```json
{
  "age": 52,
  "sex": "male",
  "height_cm": 175,
  "weight_kg": 92,
  "smoker": true,
  "alcohol_drinks_per_week": 6,
  "activity_minutes_per_week": 60,
  "sleep_hours": 6,
  "family_history": ["heart_disease", "diabetes"],
  "conditions": ["hypertension", "high_cholesterol"],
  "symptoms": ["chest_pain", "fatigue"],
  "condition_description": "Experiencing chest pain with high BP",
  "measurements": {
    "systolic_bp": 148,
    "diastolic_bp": 92,
    "fasting_glucose_mg_dl": 118,
    "resting_spo2": 94,
    "resting_hr": 78
  }
}
```

### Response:
```json
{
  "medicines": [
    {
      "name": "Lisinopril",
      "category": "ACE Inhibitor",
      "reason": "Reduces blood pressure and heart workload",
      "priority": "high",
      "side_effects": ["Cough", "Dizziness"]
    },
    {
      "name": "Atorvastatin",
      "category": "Statin",
      "reason": "Reduces cholesterol and heart disease risk",
      "priority": "high",
      "side_effects": ["Muscle pain", "Liver enzyme changes"]
    }
  ],
  "wellness_activities": [
    {
      "activity": "Brisk Walking",
      "category": "exercise",
      "description": "30 minutes of moderate-paced walking",
      "frequency": "5 days/week",
      "difficulty_level": "easy",
      "estimated_benefit": "Improves cardiovascular health and blood sugar control"
    },
    {
      "activity": "DASH Diet",
      "category": "diet",
      "description": "Dietary Approaches to Stop Hypertension",
      "frequency": "Daily",
      "difficulty_level": "moderate",
      "estimated_benefit": "Reduces blood pressure naturally"
    }
  ],
  "lifestyle_changes": [
    "Quit smoking immediately - this is the single most impactful change for your health",
    "Gradually increase physical activity to at least 150 minutes of moderate exercise per week",
    "Increase sleep duration from 6 hours to 7-9 hours per night",
    "Work to reduce blood pressure through diet, exercise, and stress management"
  ],
  "confidence_score": 0.82,
  "notes": "These recommendations are based on machine learning analysis using Random Forest and Logistic Regression models trained on medical data. Always consult with a healthcare professional before starting any new treatment or significant lifestyle change."
}
```

---

## 💻 Testing with cURL

```bash
curl -X POST http://127.0.0.1:8080/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "age": 52,
    "sex": "male",
    "height_cm": 175,
    "weight_kg": 92,
    "smoker": true,
    "alcohol_drinks_per_week": 6,
    "activity_minutes_per_week": 60,
    "sleep_hours": 6,
    "family_history": ["heart_disease"],
    "conditions": ["hypertension"],
    "symptoms": ["fatigue"],
    "measurements": {
      "systolic_bp": 148,
      "diastolic_bp": 92
    }
  }'
```

---

## 🔧 Model Training

### Automatic Training
Models are automatically trained on first API call if not found locally.

### Manual Retraining
```bash
python app/train_models.py
```

Output:
```
🏥 HealthBot ML Model Training
==================================================

📊 Training Medicine Recommendation Model...
   Model: Random Forest Classifier
   Training samples: 500 synthetic patient profiles
   ✓ Model trained successfully
   ✓ Saving to: app/models/medicine_recommender.pkl

🏃 Training Wellness Recommendation Model...
   Model: Logistic Regression
   Training samples: 500 synthetic patient profiles
   ✓ Model trained successfully
   ✓ Saving to: app/models/wellness_recommender.pkl

📏 Saving Feature Scaler...
   ✓ Saving to: app/models/scaler.pkl

==================================================
✅ All models trained and saved successfully!
==================================================
```

---

## 📊 Model Files

Located in: `app/models/`

| File | Size | Purpose |
|------|------|---------|
| `medicine_recommender.pkl` | ~1-2 MB | Random Forest for medicines |
| `wellness_recommender.pkl` | ~10-50 KB | Logistic Regression for wellness |
| `scaler.pkl` | ~1 KB | Feature scaling for both models |

---

## 🎓 Understanding Model Output

### Confidence Score (0.0 - 1.0)
- **0.8 - 1.0**: High confidence in recommendations
- **0.6 - 0.8**: Good confidence
- **0.4 - 0.6**: Moderate confidence (consider providing more health data)
- **< 0.4**: Low confidence (more measurements needed)

### Priority Levels (Medicines)
- **High**: Critical for your conditions
- **Medium**: Important to consider
- **Low**: Supportive role

### Difficulty Levels (Wellness)
- **Easy**: Can start immediately
- **Moderate**: Requires planning
- **Challenging**: Significant lifestyle change required

---

## 📈 Improving Recommendations

### Provide More Data
- Add vital measurements (BP, heart rate, glucose)
- Include specific symptoms
- Report family medical history
- Detail lifestyle information

### Better Recommendations = More Complete Data
```
Minimal data    → 0.4-0.5 confidence
Standard data   → 0.6-0.7 confidence  
Complete data   → 0.8+ confidence
```

---

## ⚠️ Important Disclaimers

1. **Not Medical Advice**
   - Use only for health screening/education
   - Always consult healthcare professionals
   - Not a substitute for medical diagnosis

2. **Data Privacy**
   - Patient data not stored
   - Models only learn statistical patterns
   - No PII retention

3. **Model Limitations**
   - ~15-22% error rate
   - Synthetic training data
   - Works best for common conditions

---

## 🐛 Troubleshooting

### Models not loading?
```bash
# Retrain models
python app/train_models.py
```

### Low confidence scores?
- Provide more health measurements
- Fill in vital signs
- Include symptom details

### Unexpected recommendations?
- Check if all required fields are provided
- Verify measurements are in correct ranges
- Review confidence score

---

## 🔗 Additional Resources

- [Technical ML Documentation](ML_MODELS.md)
- [API Documentation](http://127.0.0.1:8080/docs)
- [Main README](README.md)

---

## 📞 Support

For ML model issues:
1. Check model confidence in response
2. Ensure data completeness
3. Retrain models: `python app/train_models.py`
4. Review [ML_MODELS.md](ML_MODELS.md) for technical details
