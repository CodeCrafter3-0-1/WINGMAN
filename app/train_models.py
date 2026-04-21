"""
Model training script for ML-based health recommendations.

This script trains and saves the machine learning models used for generating
personalized medicine and wellness recommendations.

Models trained:
1. Random Forest Classifier - for medicine recommendations
2. Logistic Regression - for wellness activity recommendations
"""

from __future__ import annotations

import os
import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ml_recommendation_service import (
    _train_medicine_model,
    _train_wellness_model,
    _ensure_model_dir,
    MEDICINE_MODEL_PATH,
    WELLNESS_MODEL_PATH,
    SCALER_PATH,
)
import joblib


def train_and_save_models() -> None:
    """Train all models and save them to disk."""
    print("🏥 HealthBot ML Model Training")
    print("=" * 50)
    
    _ensure_model_dir()
    
    # Train medicine model
    print("\n📊 Training Medicine Recommendation Model...")
    print("   Model: Random Forest Classifier")
    print("   Training samples: 500 synthetic patient profiles")
    
    medicine_model, scaler = _train_medicine_model()
    
    print("   ✓ Model trained successfully")
    print(f"   ✓ Saving to: {MEDICINE_MODEL_PATH}")
    joblib.dump(medicine_model, MEDICINE_MODEL_PATH)
    
    # Train wellness model
    print("\n🏃 Training Wellness Recommendation Model...")
    print("   Model: Logistic Regression")
    print("   Training samples: 500 synthetic patient profiles")
    
    wellness_model, _ = _train_wellness_model()
    
    print("   ✓ Model trained successfully")
    print(f"   ✓ Saving to: {WELLNESS_MODEL_PATH}")
    joblib.dump(wellness_model, WELLNESS_MODEL_PATH)
    
    # Save scaler
    print("\n📏 Saving Feature Scaler...")
    print(f"   ✓ Saving to: {SCALER_PATH}")
    joblib.dump(scaler, SCALER_PATH)
    
    # Print model information
    print("\n" + "=" * 50)
    print("✅ All models trained and saved successfully!")
    print("=" * 50)
    
    print("\n📋 Model Information:")
    print(f"   Random Forest (Medicine): {medicine_model.n_estimators} trees, max_depth={medicine_model.max_depth}")
    print(f"   Logistic Regression (Wellness): {'liblinear' if hasattr(wellness_model, 'solver') else 'default'} solver")
    print(f"   Feature dimension: 20")
    print(f"\n   Models location: {os.path.dirname(MEDICINE_MODEL_PATH)}")
    

if __name__ == "__main__":
    train_and_save_models()
