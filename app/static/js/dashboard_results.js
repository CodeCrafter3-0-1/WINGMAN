function formatTitle(name) {
  return String(name || "").replaceAll("_", " ");
}

function getWorstRisk(risks) {
  const levelOrder = { low: 0, moderate: 1, high: 2, urgent: 3 };
  let worst = { key: "none", score: 0, level: "low" };
  Object.entries(risks || {}).forEach(([key, risk]) => {
    const level = risk.level || "low";
    const score = risk.score || 0;
    if (
      levelOrder[level] > levelOrder[worst.level] ||
      (levelOrder[level] === levelOrder[worst.level] && score > worst.score)
    ) {
      worst = { key, level, score };
    }
  });
  return worst;
}

function renderInputSummary(payload) {
  const container = document.getElementById("inputSummary");
  if (!container) return;

  const formatList = (items) => items && items.length ? items.join(", ") : "None specified";
  const formatMeasurement = (value, unit) => value != null ? `${value} ${unit}` : "Not provided";

  container.innerHTML = `
    <div class="input-card">
      <div class="input-header">
        <i class="fas fa-user"></i>
        <h3>Basic Information</h3>
      </div>
      <div class="input-details">
        <div class="input-item"><strong>Age:</strong> ${payload.age} years</div>
        <div class="input-item"><strong>Sex:</strong> ${formatTitle(payload.sex)}</div>
        <div class="input-item"><strong>Height:</strong> ${formatMeasurement(payload.height_cm, "cm")}</div>
        <div class="input-item"><strong>Weight:</strong> ${formatMeasurement(payload.weight_kg, "kg")}</div>
        <div class="input-item"><strong>Smoker:</strong> ${payload.smoker ? "Yes" : "No"}</div>
      </div>
    </div>

    <div class="input-card">
      <div class="input-header">
        <i class="fas fa-running"></i>
        <h3>Lifestyle</h3>
      </div>
      <div class="input-details">
        <div class="input-item"><strong>Activity:</strong> ${formatMeasurement(payload.activity_minutes_per_week, "min/week")}</div>
        <div class="input-item"><strong>Sleep:</strong> ${formatMeasurement(payload.sleep_hours, "hours/night")}</div>
        <div class="input-item"><strong>Alcohol:</strong> ${formatMeasurement(payload.alcohol_drinks_per_week, "drinks/week")}</div>
      </div>
    </div>

    <div class="input-card">
      <div class="input-header">
        <i class="fas fa-stethoscope"></i>
        <h3>Health History</h3>
      </div>
      <div class="input-details">
        <div class="input-item"><strong>Family History:</strong> ${formatList(payload.family_history)}</div>
        <div class="input-item"><strong>Conditions:</strong> ${formatList(payload.conditions)}</div>
        <div class="input-item"><strong>Symptoms:</strong> ${formatList(payload.symptoms)}</div>
      </div>
    </div>

    <div class="input-card">
      <div class="input-header">
        <i class="fas fa-flask"></i>
        <h3>Measurements</h3>
      </div>
      <div class="input-details">
        <div class="input-item"><strong>Blood Pressure:</strong> ${payload.measurements?.systolic_bp && payload.measurements?.diastolic_bp ? `${payload.measurements.systolic_bp}/${payload.measurements.diastolic_bp} mmHg` : "Not provided"}</div>
        <div class="input-item"><strong>Fasting Glucose:</strong> ${formatMeasurement(payload.measurements?.fasting_glucose_mg_dl, "mg/dL")}</div>
        <div class="input-item"><strong>Random Glucose:</strong> ${formatMeasurement(payload.measurements?.random_glucose_mg_dl, "mg/dL")}</div>
        <div class="input-item"><strong>Resting HR:</strong> ${formatMeasurement(payload.measurements?.resting_hr, "bpm")}</div>
        <div class="input-item"><strong>SpO2:</strong> ${formatMeasurement(payload.measurements?.resting_spo2, "%")}</div>
      </div>
    </div>
  `;
}

function renderSummary(payload, data) {
  const root = document.getElementById("quickSummary");
  const stepsRoot = document.getElementById("nextSteps");
  if (!root || !stepsRoot) return;

  const risks = (data && data.risks) || {};
  const values = Object.values(risks);
  const total = values.length || 1;
  const highCount = values.filter((r) => r.level === "high" || r.level === "urgent").length;
  const consultCount = values.filter((r) => r.recommend_medical_consultation).length;
  const worst = getWorstRisk(risks);
  const scorePct = Math.round((worst.score || 0) * 100);

  root.innerHTML = `
    <div class="summary-card tone-blue">
      <div class="label">Highest flagged risk</div>
      <div class="value">${formatTitle(worst.key)} (${worst.level})</div>
      <div class="sub">${scorePct}% score</div>
    </div>
    <div class="summary-card tone-purple">
      <div class="label">High/Urgent categories</div>
      <div class="value">${highCount} of ${total}</div>
      <div class="sub">Use care plan for next actions</div>
    </div>
    <div class="summary-card tone-green">
      <div class="label">Consultation suggestions</div>
      <div class="value">${consultCount} categories</div>
      <div class="sub">${consultCount ? "Clinician follow-up recommended" : "Routine follow-up likely enough"}</div>
    </div>
  `;

  const optionalUsed = [];
  if (payload?.measurements?.fasting_glucose_mg_dl != null) optionalUsed.push("fasting glucose");
  if (payload?.measurements?.random_glucose_mg_dl != null) optionalUsed.push("random glucose");
  if (payload?.measurements?.resting_spo2 != null) optionalUsed.push("SpO2");
  if (payload?.measurements?.resting_hr != null) optionalUsed.push("resting HR");

  const toolsText = optionalUsed.length
    ? `Optional measurements used: ${optionalUsed.join(", ")}.`
    : "No optional medical-tool measurements were used.";

  stepsRoot.innerHTML = `
    <div class="info-box tone-blue">
      <h3>What to do now</h3>
      <p>If severe symptoms are present, seek urgent care. Otherwise use care-plan and medicine pages for structured next steps.</p>
    </div>
    <div class="info-box tone-green">
      <h3>Data confidence tip</h3>
      <p>${toolsText}</p>
    </div>
  `;
}

function renderResults(payload, data) {
  const results = document.getElementById("results");
  results.innerHTML = "";
  renderSummary(payload, data);

  // Show condition description if provided
  if (payload.condition_description) {
    const conditionDiv = document.getElementById("conditionDescription");
    const conditionText = document.getElementById("conditionText");
    if (conditionDiv && conditionText) {
      conditionText.textContent = payload.condition_description;
      conditionDiv.style.display = "block";
    }
  }

  Object.entries((data && data.risks) || {}).forEach(([name, risk]) => {
    const div = document.createElement("div");
    div.className = "risk-card";
    const scorePercent = Math.round((risk.score || 0) * 100);
    const levelClass = risk.level || "low";

    div.innerHTML = `
      <div class="risk-header">
        <h3>${formatTitle(name)}</h3>
        <span class="risk-badge ${levelClass}">${risk.level}</span>
      </div>
      <div class="risk-score">
        <div class="score-bar">
          <div class="score-fill ${levelClass}" style="width: ${scorePercent}%"></div>
        </div>
        <div class="score-text">${scorePercent}% risk score</div>
      </div>
      <div class="risk-details">
        <div class="detail-section">
          <h4><i class="fas fa-exclamation-triangle"></i> Top Contributors</h4>
          <ul>
            ${(risk.top_contributors || []).map(c => `<li>${c}</li>`).join("") || "<li>No specific contributors identified</li>"}
          </ul>
        </div>
        <div class="detail-section">
          <h4><i class="fas fa-shield-alt"></i> Preventive Measures</h4>
          <ul>
            ${(risk.preventive_measures || []).map(m => `<li>${m}</li>`).join("") || "<li>General healthy lifestyle recommended</li>"}
          </ul>
        </div>
        <div class="consultation-section ${risk.recommend_medical_consultation ? 'recommended' : 'not-required'}">
          <i class="fas fa-user-md"></i>
          <strong>Medical Consultation:</strong> ${risk.recommend_medical_consultation ? "Recommended - Please consult a healthcare provider" : "Not required at this time"}
        </div>
      </div>
    `;
    results.appendChild(div);
  });

  if (data && data.disclaimer) {
    const note = document.createElement("div");
    note.className = "disclaimer-note";
    note.innerHTML = `
      <i class="fas fa-info-circle"></i>
      <div>
        <strong>Important:</strong> ${data.disclaimer}
      </div>
    `;
    results.appendChild(note);
  }

  const meta = document.getElementById("predictionMeta");
  const includedExtras = [];
  if (payload?.measurements?.fasting_glucose_mg_dl != null) {
    includedExtras.push(`fasting glucose ${payload.measurements.fasting_glucose_mg_dl}`);
  }
  if (payload?.measurements?.resting_spo2 != null) {
    includedExtras.push(`SpO2 ${payload.measurements.resting_spo2}`);
  }
  if (payload?.measurements?.resting_hr != null) includedExtras.push(`resting HR ${payload.measurements.resting_hr}`);
  if (payload?.measurements?.random_glucose_mg_dl != null) {
    includedExtras.push(`random glucose ${payload.measurements.random_glucose_mg_dl}`);
  }
  if (payload?.condition_description) {
    includedExtras.push("detailed condition description");
  }

  // Calculate data completeness
  const completeness = calculateDataCompleteness(payload);
  const completenessEl = document.getElementById("confidence");
  if (completenessEl) {
    const completenessPercent = Math.round(completeness * 100);
    completenessEl.textContent = `${completenessPercent}%`;
    completenessEl.className = `stat-value ${completenessPercent >= 80 ? 'high' : completenessPercent >= 50 ? 'medium' : 'low'}`;
  }

  meta.textContent = includedExtras.length
    ? `Additional data used: ${includedExtras.join(", ")}.` + (payload?.condition_description ? " Patient provided detailed description of their condition." : "")
    : "Tip: include resting HR, random glucose, and condition details for richer prediction signals.";
}

function calculateDataCompleteness(payload) {
  let present = 0;
  let total = 0;

  // Basic info
  const basicFields = ['age', 'sex', 'height_cm', 'weight_kg'];
  basicFields.forEach(field => {
    total++;
    if (payload[field] != null) present++;
  });

  // Lifestyle
  const lifestyleFields = ['smoker', 'alcohol_drinks_per_week', 'activity_minutes_per_week', 'sleep_hours'];
  lifestyleFields.forEach(field => {
    total++;
    if (payload[field] != null) present++;
  });

  // Health history
  total++;
  if ((payload.family_history || []).length > 0) present++;

  total++;
  if ((payload.conditions || []).length > 0) present++;

  total++;
  if ((payload.symptoms || []).length > 0) present++;

  // Measurements
  const measurementFields = ['systolic_bp', 'diastolic_bp', 'fasting_glucose_mg_dl', 'random_glucose_mg_dl', 'resting_hr', 'resting_spo2'];
  measurementFields.forEach(field => {
    total++;
    if (payload.measurements && payload.measurements[field] != null) present++;
  });

  // Condition description
  total++;
  if (payload.condition_description && payload.condition_description.trim()) present++;

  return total > 0 ? present / total : 0;
}

document.getElementById("logoutBtn").addEventListener("click", async () => {
  await fetch("/api/auth/logout", { method: "POST" });
  window.location.href = "/login";
});

document.getElementById("printBtn").addEventListener("click", () => {
  window.print();
});

(function init() {
  const errorEl = document.getElementById("predictionError");
  let raw = null;
  try {
    raw = sessionStorage.getItem("lastPrediction");
  } catch (_) {
    raw = null;
  }
  if (!raw) {
    try {
      raw = localStorage.getItem("lastPrediction");
    } catch (_) {
      raw = null;
    }
  }
  if (!raw && window.name) {
    raw = window.name;
  }
  if (!raw) {
    errorEl.textContent = "No recent prediction found. Please run analysis from dashboard.";
    return;
  }

  try {
    const parsed = JSON.parse(raw);
    renderInputSummary(parsed.payload);
    renderResults(parsed.payload, parsed.data);

    // Set assessment date
    const dateEl = document.getElementById("assessmentDate");
    if (dateEl && parsed.generated_at) {
      const date = new Date(parsed.generated_at);
      dateEl.textContent = date.toLocaleDateString() + " " + date.toLocaleTimeString();
    }
  } catch (_) {
    errorEl.textContent = "Could not load prediction output. Please run analysis again.";
  }
})();
