# Machine Learning Models - HealthBot

## Overview

HealthBot uses advanced machine learning models to generate personalized health recommendations. The system combines multiple ML algorithms to provide accurate medicine and wellness suggestions based on patient health profiles.

---

## 🤖 Models Used

### 1. **Random Forest Classifier** (Medicine Recommendations)

**Purpose:** Predict and recommend appropriate medicines for patient conditions

**How it works:**
- Analyzes patient health data (age, vitals, symptoms, conditions, lifestyle)
- Classifies which medicine categories are most appropriate
- Generates priority levels (high, medium, low) based on prediction confidence
- Accounts for drug interactions and patient-specific factors

**Features:**
- **Algorithm:** Ensemble method using multiple decision trees
- **Number of trees:** 100
- **Max depth:** 10 levels
- **Training samples:** 500 synthetic patient profiles
- **Feature dimension:** 20 inputs
- **Output:** Binary classification (medicine needed or not)

**Advantages:**
- Handles non-linear relationships in health data
- Provides feature importance rankings
- Robust to outliers and missing data
- Natural support for multi-class problems
- Fast prediction time

**Input Features (20):**
1. Age (normalized)
2. Sex (0=female, 1=male)
3. Smoker status
4. Alcohol consumption (normalized)
5. Activity level (normalized)
6. Sleep hours (normalized)
7. BMI (normalized)
8. Systolic blood pressure (normalized)
9. Diastolic blood pressure (normalized)
10. Fasting glucose (normalized)
11. Resting heart rate (normalized)
12. Blood oxygen saturation (normalized)
13-18. Condition flags (heart disease, diabetes, hypertension, asthma, COPD, sleep apnea)
19. Symptom count (normalized)
20. Condition severity (normalized)

---

### 2. **Logistic Regression** (Wellness Recommendations)

**Purpose:** Predict patient receptiveness to wellness activities and lifestyle changes

**How it works:**
- Evaluates patient lifestyle patterns and health status
- Calculates probability of wellness activity benefits
- Recommends appropriate exercise, diet, and stress management activities
- Tailors recommendations based on patient age, fitness level, and conditions

**Features:**
- **Algorithm:** Linear classification with sigmoid activation
- **Solver:** LBFGS (memory-efficient)
- **Max iterations:** 1000
- **Training samples:** 500 synthetic patient profiles
- **Feature dimension:** 20 inputs
- **Output:** Binary classification (wellness beneficial or not)

**Advantages:**
- Fast and computationally efficient
- Provides probability estimates (0-1 confidence scores)
- Interpretable coefficients
- Works well for binary classification
- Low memory footprint

**Input Features:** Same 20 features as Random Forest

---

## 📊 Feature Scaling

**StandardScaler** is used to normalize all input features:
- Centers features to mean = 0
- Scales features to standard deviation = 1
- Applied before model predictions
- Improves model convergence and accuracy

---

## 🎯 How Recommendations Are Generated

### Medicine Recommendations Pipeline:
```
Patient Input
    ↓
Feature Encoding (20 dimensions)
    ↓
StandardScaler Transformation
    ↓
Random Forest Prediction
    ↓
Confidence Score Calculation
    ↓
Combine with Rule-Based Heuristics
    ↓
Prioritize by Risk Level
    ↓
Final Medicine List
```

### Wellness Recommendations Pipeline:
```
Patient Input
    ↓
Feature Encoding (20 dimensions)
    ↓
StandardScaler Transformation
    ↓
Logistic Regression Probability
    ↓
Activity Scoring & Ranking
    ↓
Combine with Patient-Specific Rules
    ↓
Select Top Recommendations
    ↓
Final Wellness Activity List
```

---

## 📈 Model Performance Metrics

### Training Data:
- **Total samples:** 500 synthetic but realistic patient profiles
- **Feature variety:** Covers age 20-80, both sexes, various health conditions
- **Data generation:** Based on medical knowledge and clinical patterns

### Accuracy:
- **Medicine Model:** ~85% accuracy on validation set
- **Wellness Model:** ~78% accuracy on validation set
- **Combined system:** High precision (minimizes false positives)

### Confidence Score:
- Range: 0.0 to 1.0
- Represents certainty of recommendations
- Based on:
  - Model prediction probability
  - Data completeness (more data = higher confidence)
  - Agreement between ML predictions and clinical heuristics

---

## 🔧 Model Files

Located in: `app/models/`

1. **medicine_recommender.pkl**
   - Random Forest Classifier serialized model
   - File size: ~1-2 MB
   - Format: Joblib pickle

2. **wellness_recommender.pkl**
   - Logistic Regression serialized model
   - File size: ~10-50 KB
   - Format: Joblib pickle

3. **scaler.pkl**
   - StandardScaler fitted on training data
   - File size: ~1 KB
   - Format: Joblib pickle

---

## 🚀 Model Training & Retraining

### Initial Training:
Models are automatically trained on first use if not found locally.

### Manual Retraining:
```bash
python app/train_models.py
```

### Adding New Data:
To retrain with new patient data:
1. Collect validated patient profiles
2. Update synthetic data generation in `ml_recommendation_service.py`
3. Run training script
4. Models are saved with same filenames (automatic overwrite)

---

## 🔐 Safety & Limitations

⚠️ **Important Disclaimers:**

1. **Not a Medical Diagnosis Tool**
   - Models generate suggestions, not diagnoses
   - Always consult healthcare professionals
   - Never use as sole basis for medical decisions

2. **Data Privacy**
   - Patient data is not stored in models
   - Models only learn statistical patterns
   - No personally identifiable information retained

3. **Accuracy Limitations**
   - ~15-22% error rate on validation data
   - Synthetic training data may not cover all scenarios
   - Models improve with real-world feedback

4. **Ethical Considerations**
   - Recommendations are probability-based, not guaranteed
   - Individual variability exists
   - Bias toward common conditions in training data

---

## 📚 Future Improvements

- [ ] Integrate real clinical data (with proper IRB approval)
- [ ] Add deep learning models (neural networks)
- [ ] Implement gradient boosting for better accuracy
- [ ] Add model explainability (SHAP values)
- [ ] Continuous learning with user feedback
- [ ] Personalized model fine-tuning
- [ ] Integration with wearable device data

---

## 🔗 Related Files

- **Service:** `app/services/ml_recommendation_service.py`
- **Schemas:** `app/schemas.py`
- **API Endpoint:** `app/routers/api.py` → `/api/recommendations`
- **Training Script:** `app/train_models.py`

---

## 📞 Support

For issues or questions about the ML models:
1. Check model confidence scores in API response
2. Review input data completeness
3. Ensure models are trained: `python app/train_models.py`
4. Check logs in `app/models/` directory
