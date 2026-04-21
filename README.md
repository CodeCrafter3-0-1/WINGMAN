## AI-Based Early Disease Detection Platform

This is a **local runnable MVP** for early risk screening (not diagnosis). It accepts user-reported inputs (symptoms, medical history, lifestyle) and returns:

- **Risk scores** for: heart disease, diabetes, respiratory disorder, stroke, kidney disease, metabolic liver risk
- **Preventive measures** suggestions
- A **recommendation** on whether medical consultation is warranted
- **Session-based login** and protected dashboard pages
- A **health chatbot** for user guidance

### What this MVP is (and is not)

- **Is**: a software scaffold + deterministic risk scoring you can iterate on quickly.
- **Is not**: a clinically validated medical device. Use only for prototyping and education.

### Quickstart

1) Create a virtual environment (recommended)

```bash
python -m venv .venv
```

2) Activate it

- PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

3) Install dependencies

```bash
pip install -r requirements.txt
```

4) Run the app server

```bash
python -m uvicorn app.server:app --host 127.0.0.1 --port 8080 --reload
```

Then open:

- Login page: `http://127.0.0.1:8080/login`
- Dashboard: `http://127.0.0.1:8080/dashboard`
- Chatbot: `http://127.0.0.1:8080/chatbot`
- API docs: `http://127.0.0.1:8080/docs`
- Health: `http://127.0.0.1:8080/api/health`
- Example payload: `http://127.0.0.1:8080/api/example`

If port `8080` is already in use, switch to another port (example `8081`):

```bash
python -m uvicorn app.server:app --host 127.0.0.1 --port 8081 --reload

### Demo login users

- `admin@example.com` / `admin123`
- `doctor@example.com` / `doctor123`
```

### Example request

```json
{
  "age": 52,
  "sex": "male",
  "height_cm": 175,
  "weight_kg": 92,
  "smoker": true,
  "alcohol_drinks_per_week": 6,
  "activity_minutes_per_week": 60,
  "sleep_hours": 6.0,
  "family_history": ["heart_disease", "diabetes"],
  "conditions": ["hypertension"],
  "symptoms": ["chest_pain", "shortness_of_breath", "fatigue"],
  "condition_description": "Optional detailed description of the patient's condition",
  "measurements": {
    "systolic_bp": 148,
    "diastolic_bp": 92,
    "fasting_glucose_mg_dl": 118,
    "resting_spo2": 94
  }
}
```

