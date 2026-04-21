"""
Test script for ML recommendation API.

Run this script to test the machine learning models:
    python app/test_ml_api.py

Make sure the API server is running on port 8080:
    python -m uvicorn app.server:app --host 127.0.0.1 --port 8080 --reload
"""

from __future__ import annotations

import json
import requests
from typing import Dict, Any


# API endpoint
API_URL = "http://127.0.0.1:8080/api/recommendations"

# Test cases
TEST_CASES = [
    {
        "name": "🫀 High-Risk Cardiovascular Patient",
        "data": {
            "age": 62,
            "sex": "male",
            "height_cm": 180,
            "weight_kg": 95,
            "smoker": True,
            "alcohol_drinks_per_week": 8,
            "activity_minutes_per_week": 30,
            "sleep_hours": 6.5,
            "family_history": ["heart_disease", "stroke"],
            "conditions": ["hypertension", "high_cholesterol"],
            "symptoms": ["chest_pain", "shortness_of_breath", "fatigue"],
            "condition_description": "History of chest pain, especially with exertion",
            "measurements": {
                "systolic_bp": 155,
                "diastolic_bp": 98,
                "fasting_glucose_mg_dl": 115,
                "resting_hr": 82,
                "resting_spo2": 92,
            }
        }
    },
    {
        "name": "🩺 Diabetic Patient",
        "data": {
            "age": 48,
            "sex": "female",
            "height_cm": 165,
            "weight_kg": 78,
            "smoker": False,
            "alcohol_drinks_per_week": 2,
            "activity_minutes_per_week": 120,
            "sleep_hours": 7.0,
            "family_history": ["diabetes"],
            "conditions": ["diabetes", "hypertension"],
            "symptoms": ["frequent_urination", "excess_thirst", "fatigue"],
            "measurements": {
                "systolic_bp": 135,
                "diastolic_bp": 85,
                "fasting_glucose_mg_dl": 155,
                "resting_hr": 72,
                "resting_spo2": 96,
            }
        }
    },
    {
        "name": "🫁 Respiratory Patient",
        "data": {
            "age": 55,
            "sex": "male",
            "height_cm": 175,
            "weight_kg": 88,
            "smoker": True,
            "alcohol_drinks_per_week": 3,
            "activity_minutes_per_week": 45,
            "sleep_hours": 6.5,
            "family_history": ["asthma", "copd"],
            "conditions": ["asthma", "sleep_apnea"],
            "symptoms": ["persistent_cough", "wheezing", "shortness_of_breath"],
            "measurements": {
                "systolic_bp": 138,
                "diastolic_bp": 88,
                "resting_hr": 85,
                "resting_spo2": 91,
            }
        }
    },
    {
        "name": "💪 Healthy Lifestyle Patient",
        "data": {
            "age": 35,
            "sex": "female",
            "height_cm": 170,
            "weight_kg": 62,
            "smoker": False,
            "alcohol_drinks_per_week": 1,
            "activity_minutes_per_week": 300,
            "sleep_hours": 8.0,
            "family_history": [],
            "conditions": [],
            "symptoms": [],
            "measurements": {
                "systolic_bp": 118,
                "diastolic_bp": 76,
                "fasting_glucose_mg_dl": 95,
                "resting_hr": 60,
                "resting_spo2": 98,
            }
        }
    },
]


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_section(text: str) -> None:
    """Print a formatted section."""
    print(f"\n  📌 {text}")
    print("  " + "-" * 66)


def format_medicines(medicines: list) -> str:
    """Format medicine list for display."""
    if not medicines:
        return "    No medications recommended"
    
    lines = []
    for i, med in enumerate(medicines, 1):
        priority_emoji = "🔴" if med["priority"] == "high" else "🟡" if med["priority"] == "medium" else "🟢"
        lines.append(f"    {priority_emoji} {med['name']} ({med['category']})")
        lines.append(f"       Reason: {med['reason']}")
        if med['side_effects']:
            lines.append(f"       Side effects: {', '.join(med['side_effects'][:2])}")
    return "\n".join(lines)


def format_wellness(activities: list) -> str:
    """Format wellness activities for display."""
    if not activities:
        return "    No activities recommended"
    
    lines = []
    for i, activity in enumerate(activities, 1):
        difficulty_emoji = "🟢" if activity["difficulty_level"] == "easy" else "🟡" if activity["difficulty_level"] == "moderate" else "🔴"
        category_emoji = {
            "exercise": "🏃",
            "diet": "🥗",
            "stress_management": "🧘",
            "lifestyle": "🛌"
        }.get(activity["category"], "📝")
        
        lines.append(f"    {category_emoji} {activity['activity']} ({difficulty_emoji} {activity['difficulty_level']})")
        lines.append(f"       Frequency: {activity['frequency']}")
        lines.append(f"       Benefit: {activity['estimated_benefit']}")
    return "\n".join(lines)


def test_api(test_case: Dict[str, Any]) -> None:
    """Test the ML recommendation API with a test case."""
    print_section(test_case["name"])
    
    try:
        # Make API request
        print("  ⏳ Sending request to ML model...")
        response = requests.post(API_URL, json=test_case["data"], timeout=10)
        
        if response.status_code != 200:
            print(f"  ❌ Error: {response.status_code}")
            print(f"  {response.text}")
            return
        
        result = response.json()
        
        # Display confidence
        confidence = result.get("confidence_score", 0)
        confidence_bar = "█" * int(confidence * 20) + "░" * (20 - int(confidence * 20))
        print(f"  Confidence: [{confidence_bar}] {confidence:.1%}")
        
        # Display medicines
        print_section("Recommended Medicines")
        print(format_medicines(result.get("medicines", [])))
        
        # Display wellness
        print_section("Recommended Wellness Activities")
        print(format_wellness(result.get("wellness_activities", [])))
        
        # Display lifestyle changes
        lifestyle = result.get("lifestyle_changes", [])
        if lifestyle:
            print_section("Lifestyle Changes")
            for change in lifestyle:
                print(f"    • {change}")
        
        # Display notes
        notes = result.get("notes", "")
        if notes:
            print_section("Notes")
            print(f"    {notes}")
        
        print("\n  ✅ Test passed!")
        
    except requests.exceptions.ConnectionError:
        print("  ❌ Connection Error: Cannot connect to API server")
        print("  Make sure the API is running:")
        print("     python -m uvicorn app.server:app --host 127.0.0.1 --port 8080 --reload")
    except requests.exceptions.Timeout:
        print("  ❌ Timeout: API response took too long")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")


def main() -> None:
    """Run all tests."""
    print_header("🏥 HealthBot ML Recommendation API Test Suite")
    print("\n  Testing machine learning models:")
    print("    • Random Forest Classifier (Medicine Recommendations)")
    print("    • Logistic Regression (Wellness Recommendations)")
    print(f"\n  API Endpoint: {API_URL}")
    print(f"  Total test cases: {len(TEST_CASES)}")
    
    for test_case in TEST_CASES:
        test_api(test_case)
    
    print_header("✅ Test Suite Complete")
    print("\n  For more information:")
    print("    • API Docs: http://127.0.0.1:8080/docs")
    print("    • ML Documentation: See ML_MODELS.md")
    print("    • Quick Start Guide: See MODEL_QUICKSTART.md\n")


if __name__ == "__main__":
    main()
