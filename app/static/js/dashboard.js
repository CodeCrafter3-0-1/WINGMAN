const tokenize = (v) =>
  (v || "")
    .split(",")
    .map((x) => x.trim().toLowerCase())
    .filter(Boolean);

const CANONICAL = {
  family_history: new Set(["heart_disease", "diabetes", "asthma", "copd"]),
  conditions: new Set(["hypertension", "high_cholesterol", "diabetes", "prediabetes", "asthma", "copd", "sleep_apnea"]),
  symptoms: new Set([
    "chest_pain", "shortness_of_breath", "palpitations", "swelling_legs", "fatigue",
    "frequent_urination", "excess_thirst", "blurred_vision", "unexplained_weight_loss",
    "wheezing", "persistent_cough", "fever"
  ])
};

const ALIASES = {
  shortness: "shortness_of_breath",
  "shortness of breath": "shortness_of_breath",
  chestpain: "chest_pain",
  "chest pain": "chest_pain",
  highcholesterol: "high_cholesterol",
  cholesterol: "high_cholesterol",
  sleepapnea: "sleep_apnea"
};

function normalizeTokens(raw, category) {
  const invalid = [];
  const normalized = [];
  tokenize(raw).forEach((t) => {
    const key = ALIASES[t] || t.replaceAll(" ", "_");
    if (CANONICAL[category].has(key)) normalized.push(key);
    else invalid.push(t);
  });
  return { values: [...new Set(normalized)], invalid };
}

function boundedNumber(id, min, max) {
  const raw = document.getElementById(id).value.trim();
  if (raw === "") return null;
  const n = Number(raw);
  if (!Number.isFinite(n)) return null;
  if (n < min || n > max) return null;
  return n;
}

function payloadFromForm() {
  const fam = normalizeTokens(document.getElementById("family").value, "family_history");
  const cond = normalizeTokens(document.getElementById("conditions").value, "conditions");
  const sym = normalizeTokens(document.getElementById("symptoms").value, "symptoms");

  return {
    age: boundedNumber("age", 0, 120) ?? 0,
    sex: document.getElementById("sex").value,
    height_cm: boundedNumber("height", 50, 250),
    weight_kg: boundedNumber("weight", 2, 400),
    smoker: document.getElementById("smoker").value === "true",
    alcohol_drinks_per_week: boundedNumber("alcohol", 0, 200) ?? 0,
    activity_minutes_per_week: boundedNumber("activity", 0, 5000) ?? 0,
    sleep_hours: boundedNumber("sleep", 0, 24) ?? 7,
    family_history: fam.values,
    conditions: cond.values,
    symptoms: sym.values,
    measurements: {
      systolic_bp: boundedNumber("bpSys", 60, 260),
      diastolic_bp: boundedNumber("bpDia", 30, 160),
      fasting_glucose_mg_dl: boundedNumber("glucose", 40, 400),
      random_glucose_mg_dl: boundedNumber("randomGlucose", 40, 600),
      resting_hr: boundedNumber("restingHr", 30, 220),
      resting_spo2: boundedNumber("spo2", 50, 100)
    },
    condition_description: document.getElementById("condition_description").value.trim() || null,
    _invalidTokens: [...fam.invalid, ...cond.invalid, ...sym.invalid]
  };
}

document.getElementById("loadExample").addEventListener("click", async () => {
  const ex = await (await fetch("/api/example")).json();
  document.getElementById("age").value = ex.age ?? "";
  document.getElementById("sex").value = ex.sex ?? "male";
  document.getElementById("height").value = ex.height_cm ?? "";
  document.getElementById("weight").value = ex.weight_kg ?? "";
  document.getElementById("smoker").value = String(!!ex.smoker);
  document.getElementById("alcohol").value = ex.alcohol_drinks_per_week ?? 0;
  document.getElementById("activity").value = ex.activity_minutes_per_week ?? 0;
  document.getElementById("sleep").value = ex.sleep_hours ?? 7;
  document.getElementById("family").value = (ex.family_history || []).join(",");
  document.getElementById("conditions").value = (ex.conditions || []).join(",");
  document.getElementById("symptoms").value = (ex.symptoms || []).join(",");
  document.getElementById("condition_description").value = ex.condition_description ?? "";
  document.getElementById("bpSys").value = ex.measurements?.systolic_bp ?? "";
  document.getElementById("bpDia").value = ex.measurements?.diastolic_bp ?? "";
  document.getElementById("glucose").value = ex.measurements?.fasting_glucose_mg_dl ?? "";
  document.getElementById("randomGlucose").value = ex.measurements?.random_glucose_mg_dl ?? "";
  document.getElementById("restingHr").value = ex.measurements?.resting_hr ?? "";
  document.getElementById("spo2").value = ex.measurements?.resting_spo2 ?? "";
});

document.getElementById("logoutBtn").addEventListener("click", async () => {
  await fetch("/api/auth/logout", { method: "POST" });
  window.location.href = "/login";
});

// Toggle functionality for optional sections
document.getElementById("conditionToggle").addEventListener("click", () => {
  const content = document.getElementById("conditionContent");
  const icon = document.querySelector("#conditionToggle i");
  content.classList.toggle("open");
  if (content.classList.contains("open")) {
    icon.className = "fas fa-chevron-up";
  } else {
    icon.className = "fas fa-chevron-down";
  }
});

document.getElementById("measurementsToggle").addEventListener("click", () => {
  const content = document.getElementById("measurementsContent");
  const icon = document.querySelector("#measurementsToggle i");
  content.classList.toggle("open");
  if (content.classList.contains("open")) {
    icon.className = "fas fa-chevron-up";
  } else {
    icon.className = "fas fa-chevron-down";
  }
});

document.getElementById("predictForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errorEl = document.getElementById("predictionError");
  if (errorEl) errorEl.textContent = "";
  const payload = payloadFromForm();
  const invalid = payload._invalidTokens || [];
  delete payload._invalidTokens;

  if (invalid.length) {
    if (errorEl) errorEl.textContent = `Ignored invalid tags: ${invalid.join(", ")}. Use underscore tags like chest_pain.`;
  }

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      let msg = "Prediction failed.";
      try {
        const body = await res.json();
        if (Array.isArray(body.detail)) {
          msg = body.detail.map((d) => `${d.loc?.join(".")}: ${d.msg}`).join(" | ");
        } else {
          msg = body.detail || msg;
        }
      } catch (_) {
        // Keep default message.
      }
      if (errorEl) errorEl.textContent = msg;
      return;
    }

    const data = await res.json();
    const packageForResultsPage = {
      payload,
      data,
      generated_at: new Date().toISOString()
    };
    const packed = JSON.stringify(packageForResultsPage);
    try {
      sessionStorage.setItem("lastPrediction", packed);
    } catch (_) {
      // Ignore and try fallback storage.
    }
    try {
      localStorage.setItem("lastPrediction", packed);
    } catch (_) {
      // Ignore and use window.name fallback.
    }
    window.name = packed;
    window.location.href = "/dashboard/results";
  } catch (err) {
    if (errorEl) errorEl.textContent = `Prediction failed: ${String(err?.message || err)}`;
  }
});

