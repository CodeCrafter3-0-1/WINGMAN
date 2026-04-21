from .server import app

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .routers.api import router as api_router
from .routers.web import router as web_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Health Risk Intelligence Platform",
    version="1.0.0",
    description="Early disease risk screening with dashboard, login, and chatbot.",
)

app.add_middleware(
    SessionMiddleware,
    secret_key="change-this-secret-in-production",
    same_site="lax",
    https_only=False,
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(web_router)
app.include_router(api_router)

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .routers.api import router as api_router
from .routers.web import router as web_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Health Risk Intelligence Platform",
    version="1.0.0",
    description="Early disease risk screening with dashboard, login, and chatbot.",
)

app.add_middleware(
    SessionMiddleware,
    secret_key="change-this-secret-in-production",
    same_site="lax",
    https_only=False,
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(web_router)
app.include_router(api_router)

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .risk import diabetes_risk, heart_risk, kidney_risk, metabolic_liver_risk, respiratory_risk, stroke_risk
from .schemas import PredictRequest, PredictResponse, RiskResult


app = FastAPI(
    title="Early Disease Detection (MVP)",
    version="0.1.0",
    description=(
        "Prototype screening API that produces early risk scores from self-reported inputs. "
        "Not a medical device; not for diagnosis."
    ),
)

_HOME_HTML = """\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Early Disease Detection (MVP)</title>
    <style>
      :root { color-scheme: light dark; }
      body {
        font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
        margin: 0;
        line-height: 1.35;
        background:
          radial-gradient(1200px 500px at 20% -10%, rgba(59,130,246,.22), transparent 60%),
          radial-gradient(900px 450px at 110% 10%, rgba(16,185,129,.18), transparent 55%),
          radial-gradient(700px 420px at 20% 120%, rgba(236,72,153,.14), transparent 55%);
      }
      .wrap { max-width: 1100px; margin: 34px auto; padding: 0 18px; }
      .topbar { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
      .brand h1 { margin: 0; font-size: 22px; letter-spacing: .2px; }
      .brand p { margin: 6px 0 0 0; opacity: .82; }
      .links { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
      a { text-decoration: none; }
      a:hover { text-decoration: underline; }
      .spark {
        width: 12px; height: 12px; border-radius: 3px;
        background: linear-gradient(135deg, rgba(59,130,246,.9), rgba(16,185,129,.85));
        box-shadow: 0 0 0 3px rgba(59,130,246,.12);
      }
      .pill {
        display: inline-flex; gap: 8px; align-items: center;
        padding: 8px 12px;
        border-radius: 999px;
        border: 1px solid rgba(127,127,127,.35);
        background: rgba(127,127,127,.10);
      }
      .grid { display: grid; grid-template-columns: 1.1fr .9fr; gap: 14px; margin-top: 16px; }
      @media (max-width: 980px) { .grid { grid-template-columns: 1fr; } }
      .card {
        padding: 16px 16px;
        border: 1px solid rgba(127,127,127,.35);
        border-radius: 14px;
        background: rgba(20,20,20,.03);
        backdrop-filter: blur(8px);
      }
      .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
      @media (max-width: 740px) { .row { grid-template-columns: 1fr; } }
      label { display: block; font-size: 12px; opacity: .85; margin: 10px 0 6px; }
      input, select, textarea {
        width: 100%;
        box-sizing: border-box;
        padding: 10px 11px;
        border-radius: 10px;
        border: 1px solid rgba(127,127,127,.35);
        background: rgba(127,127,127,.08);
        outline: none;
      }
      textarea { min-height: 78px; resize: vertical; }
      .hint { margin-top: 6px; font-size: 12px; opacity: .76; }
      .btnrow { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; align-items: center; }
      button {
        padding: 10px 12px;
        border-radius: 12px;
        border: 1px solid rgba(127,127,127,.35);
        background: rgba(127,127,127,.12);
        cursor: pointer;
        font-weight: 600;
      }
      button.primary {
        background: linear-gradient(135deg, rgba(59,130,246,.55), rgba(16,185,129,.45));
        border-color: rgba(59,130,246,.35);
      }
      button:disabled { opacity: .6; cursor: not-allowed; }
      code { padding: 2px 6px; border-radius: 8px; background: rgba(127,127,127,.15); }
      .warn {
        margin-top: 14px;
        padding: 10px 12px;
        border-left: 4px solid #d97706;
        background: rgba(217,119,6,.10);
        border-radius: 10px;
      }
      .muted { opacity: .82; }
      .kvs { display: grid; grid-template-columns: 1fr; gap: 10px; }
      .risk {
        border: 1px solid rgba(127,127,127,.35);
        border-radius: 14px;
        padding: 12px 12px;
        background: rgba(127,127,127,.07);
      }
      .risk h3 { margin: 0 0 8px 0; font-size: 14px; display: flex; justify-content: space-between; gap: 10px; }
      .badge { padding: 3px 10px; border-radius: 999px; font-size: 12px; border: 1px solid rgba(127,127,127,.35); }
      .b-low { background: rgba(16,185,129,.18); border-color: rgba(16,185,129,.35); }
      .b-moderate { background: rgba(59,130,246,.16); border-color: rgba(59,130,246,.35); }
      .b-high { background: rgba(245,158,11,.16); border-color: rgba(245,158,11,.35); }
      .b-urgent { background: rgba(239,68,68,.16); border-color: rgba(239,68,68,.35); }
      .meter {
        width: 100%;
        height: 10px;
        border-radius: 999px;
        overflow: hidden;
        border: 1px solid rgba(127,127,127,.30);
        background: rgba(127,127,127,.10);
        margin: 8px 0 10px 0;
      }
      .meter > div {
        height: 100%;
        width: 0%;
        border-radius: 999px;
        transition: width .35s ease;
      }
      .m-low { background: linear-gradient(90deg, rgba(16,185,129,.75), rgba(16,185,129,.45)); }
      .m-moderate { background: linear-gradient(90deg, rgba(59,130,246,.75), rgba(59,130,246,.45)); }
      .m-high { background: linear-gradient(90deg, rgba(245,158,11,.80), rgba(245,158,11,.45)); }
      .m-urgent { background: linear-gradient(90deg, rgba(239,68,68,.85), rgba(239,68,68,.45)); }
      .insights {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 10px;
      }
      @media (max-width: 740px) { .insights { grid-template-columns: 1fr; } }
      .insight {
        border: 1px solid rgba(127,127,127,.30);
        border-radius: 14px;
        padding: 12px 12px;
        background: linear-gradient(135deg, rgba(127,127,127,.10), rgba(127,127,127,.04));
      }
      .insight .t { font-size: 12px; opacity: .78; }
      .insight .v { font-size: 16px; font-weight: 700; margin-top: 6px; letter-spacing: .1px; }
      .insight .s { font-size: 12px; opacity: .82; margin-top: 6px; }
      .chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        padding: 5px 10px;
        border-radius: 999px;
        border: 1px solid rgba(127,127,127,.30);
        background: rgba(127,127,127,.08);
      }
      .chip.ok { border-color: rgba(16,185,129,.35); background: rgba(16,185,129,.12); }
      .chip.warn { border-color: rgba(245,158,11,.35); background: rgba(245,158,11,.12); }
      .chip.bad { border-color: rgba(239,68,68,.35); background: rgba(239,68,68,.12); }
      .list { margin: 6px 0 0 18px; }
      .hr { height: 1px; background: rgba(127,127,127,.28); margin: 12px 0; }
      .footer { margin-top: 14px; font-size: 12px; opacity: .8; }
      details.explain { margin-top: 12px; }
      details.explain summary {
        cursor: pointer;
        user-select: none;
        list-style: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 10px;
        border-radius: 12px;
        border: 1px solid rgba(127,127,127,.30);
        background: rgba(127,127,127,.08);
        font-weight: 650;
      }
      details.explain summary::-webkit-details-marker { display:none; }
      .legend { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
      @media (max-width: 740px) { .legend { grid-template-columns: 1fr; } }
      .legend .item {
        border: 1px solid rgba(127,127,127,.30);
        border-radius: 14px;
        padding: 12px 12px;
        background: rgba(127,127,127,.06);
      }
      .legend .item .h { display:flex; align-items:center; justify-content:space-between; gap:10px; margin: 0 0 8px 0; }
      .legend .item .p { font-size: 12px; opacity: .82; margin: 0; }
      .callout {
        margin-top: 10px;
        padding: 10px 12px;
        border: 1px solid rgba(127,127,127,.30);
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(59,130,246,.12), rgba(16,185,129,.08));
      }
      .callout strong { font-weight: 750; }
    </style>
  </head>
  <body>
    <div class="wrap">
      <div class="topbar">
        <div class="brand">
          <h1>Early Disease Detection (MVP)</h1>
          <p class="muted">Quick screening demo (informational only) — enter inputs, get risk levels and next-step tips.</p>
        </div>
        <div class="links">
          <a class="pill" href="/docs" title="Open Swagger UI"><span class="spark"></span> API docs</a>
          <a class="pill" href="/example" title="Fetch example JSON"><span class="spark"></span> Example JSON</a>
          <a class="pill" href="/health" title="Health check"><span class="spark"></span> Health</a>
        </div>
      </div>

      <div class="grid">
        <div class="card">
          <h2 style="margin:0 0 8px 0; font-size:16px;">Try it</h2>
          <div class="warn">
            <strong>Disclaimer:</strong> informational only, not a diagnosis. If you have severe symptoms, seek urgent medical care.
          </div>

          <form id="f" style="margin-top:12px;">
            <div class="row">
              <div>
                <label for="age">Age</label>
                <input id="age" type="number" min="0" max="120" value="52" required />
              </div>
              <div>
                <label for="sex">Sex</label>
                <select id="sex">
                  <option value="male" selected>male</option>
                  <option value="female">female</option>
                  <option value="other">other</option>
                </select>
              </div>
            </div>

            <div class="row">
              <div>
                <label for="height">Height (cm)</label> 
                <input id="height" type="number" min="50" max="250" value="175" />
              </div>
              <div>
                <label for="weight">Weight (kg)</label>
                <input id="weight" type="number" min="2" max="400" value="92" />
              </div>
            </div>

            <div class="row">
              <div>
                <label for="smoker">Smoker</label>
                <select id="smoker">
                  <option value="false" selected>false</option>
                  <option value="true">true</option>
                </select>
              </div>
              <div>
                <label for="activity">Activity minutes/week</label>
                <input id="activity" type="number" min="0" max="5000" value="60" />
              </div>
            </div>

            <div class="row">
              <div>
                <label for="sleep">Sleep hours/night</label>
                <input id="sleep" type="number" min="0" max="24" step="0.1" value="6" />
              </div>
              <div>
                <label for="alcohol">Alcohol drinks/week</label>
                <input id="alcohol" type="number" min="0" max="200" value="6" />
              </div>
            </div>

            <div class="row">
              <div>
                <label for="bp_sys">Systolic BP</label>
                <input id="bp_sys" type="number" min="60" max="260" value="148" />
              </div>
              <div>
                <label for="bp_dia">Diastolic BP</label>
                <input id="bp_dia" type="number" min="30" max="160" value="92" />
              </div>
            </div>

            <div class="row">
              <div>
                <label for="glu_fast">Fasting glucose (mg/dL)</label>
                <input id="glu_fast" type="number" min="40" max="400" value="118" />
              </div>
              <div>
                <label for="spo2">Resting SpO2 (%)</label>
                <input id="spo2" type="number" min="50" max="100" value="94" />
              </div>
            </div>

            <label for="family">Family history (comma separated)</label>
            <input id="family" value="heart_disease, diabetes" placeholder="heart_disease, diabetes" />
            <div class="hint">Allowed: heart_disease, diabetes, asthma, copd</div>

            <label for="conditions">Conditions (comma separated)</label>
            <input id="conditions" value="hypertension" placeholder="hypertension, high_cholesterol" />
            <div class="hint">Allowed: hypertension, high_cholesterol, diabetes, prediabetes, asthma, copd, sleep_apnea</div>

            <label for="symptoms">Symptoms (comma separated)</label>
            <textarea id="symptoms" placeholder="chest_pain, shortness_of_breath">chest_pain, shortness_of_breath, fatigue</textarea>
            <div class="hint">Examples: chest_pain, shortness_of_breath, palpitations, frequent_urination, excess_thirst, wheezing, fever</div>

            <div class="btnrow">
              <button class="primary" id="run" type="submit">Run risk screening</button>
              <button id="loadExample" type="button">Load example</button>
              <span id="status" class="muted" style="font-size:12px;"></span>
            </div>

            <details style="margin-top:10px;">
              <summary class="muted">Show request JSON</summary>
              <pre id="reqjson" style="white-space:pre-wrap; margin:10px 0 0 0;"></pre>
            </details>

            <details class="explain">
              <summary>How to use this</summary>
              <div class="callout">
                <strong>Goal:</strong> quick screening for <em>risk</em> (not diagnosis). Use it to decide what to check next and what lifestyle actions may help.
              </div>
              <div class="legend">
                <div class="item">
                  <div class="h"><strong>Low</strong><span class="badge b-low">low</span></div>
                  <p class="p">No strong flags detected from the provided inputs. Keep routine care and healthy habits.</p>
                </div>
                <div class="item">
                  <div class="h"><strong>Moderate</strong><span class="badge b-moderate">moderate</span></div>
                  <p class="p">Some risk factors are present. Consider a clinician visit and basic labs/vitals if available.</p>
                </div>
                <div class="item">
                  <div class="h"><strong>High</strong><span class="badge b-high">high</span></div>
                  <p class="p">Multiple risk factors or concerning measurements. A clinician review is recommended.</p>
                </div>
                <div class="item">
                  <div class="h"><strong>Urgent</strong><span class="badge b-urgent">urgent</span></div>
                  <p class="p"><strong>Seek urgent care</strong> if symptoms are severe, sudden, or worsening (especially chest pain or serious breathing difficulty).</p>
                </div>
              </div>
              <div class="callout" style="margin-top:12px;">
                <strong>Privacy note:</strong> this runs locally on your machine. Your inputs are sent only to this local server.
              </div>
            </details>
          </form>

          <div class="footer">
            Endpoint used: <code>POST /predict</code>. Prefer the docs at <code>/docs</code> for full schema.
          </div>
        </div>

        <div class="card">
          <h2 style="margin:0 0 8px 0; font-size:16px;">Results</h2>
          <div id="insights" class="insights"></div>
          <div class="btnrow" style="margin-top:0; margin-bottom:10px;">
            <button id="copyResults" type="button">Copy results</button>
            <span class="muted" id="copyStatus" style="font-size:12px;"></span>
          </div>
          <div id="quality" class="callout" style="display:none;"></div>
          <div id="results" class="kvs">
            <div class="muted">Run the screening to see results here.</div>
          </div>
          <div class="hr"></div>
          <div class="muted" style="font-size:12px;">
            Note: a higher score does not confirm disease. This demo uses simple rules to help you prototype product UX.
          </div>
        </div>
      </div>
    </div>

    <script>
      const el = (id) => document.getElementById(id);
      const parseList = (s) =>
        (s || "")
          .split(",")
          .map(x => x.trim())
          .filter(Boolean);

      function bmiFrom(payload) {
        const h = payload.height_cm;
        const w = payload.weight_kg;
        if (!h || !w) return null;
        const hm = h / 100.0;
        if (hm <= 0) return null;
        const bmi = w / (hm * hm);
        if (!Number.isFinite(bmi)) return null;
        return bmi;
      }

      function bmiLabel(bmi) {
        if (bmi === null) return { label: "BMI", value: "—", cls: "chip" };
        if (bmi >= 30) return { label: "BMI", value: `${bmi.toFixed(1)} (obese)`, cls: "chip bad" };
        if (bmi >= 25) return { label: "BMI", value: `${bmi.toFixed(1)} (overweight)`, cls: "chip warn" };
        if (bmi >= 18.5) return { label: "BMI", value: `${bmi.toFixed(1)} (healthy)`, cls: "chip ok" };
        return { label: "BMI", value: `${bmi.toFixed(1)} (underweight)`, cls: "chip warn" };
      }

      function renderInsights(payload, resp) {
        const root = el("insights");
        const bmi = bmiFrom(payload);
        const b = bmiLabel(bmi);

        const activity = Number(payload.activity_minutes_per_week || 0);
        const sleep = Number(payload.sleep_hours || 0);

        const activityChip =
          activity >= 150 ? { text: `${activity} min/wk`, cls: "chip ok" } :
          activity >= 75 ? { text: `${activity} min/wk`, cls: "chip warn" } :
          { text: `${activity} min/wk`, cls: "chip bad" };

        const sleepChip =
          sleep >= 7 && sleep <= 9 ? { text: `${sleep} hrs`, cls: "chip ok" } :
          sleep >= 6 ? { text: `${sleep} hrs`, cls: "chip warn" } :
          { text: `${sleep} hrs`, cls: "chip bad" };

        // Simple “next step” summary: show highest risk level present.
        const levelOrder = { low: 0, moderate: 1, high: 2, urgent: 3 };
        let worst = { k: null, level: "low", score: 0 };
        for (const [k, v] of Object.entries((resp && resp.risks) || {})) {
          const lvl = v.level || "low";
          if (levelOrder[lvl] > levelOrder[worst.level]) worst = { k, level: lvl, score: v.score || 0 };
          else if (levelOrder[lvl] === levelOrder[worst.level] && (v.score || 0) > worst.score) worst = { k, level: lvl, score: v.score || 0 };
        }

        const summaryText = worst.k
          ? `Highest flagged: ${titleCase(worst.k)} (${worst.level}, ${Math.round((worst.score || 0) * 100)}%)`
          : "Fill the form and run screening.";

        root.innerHTML = `
          <div class="insight">
            <div class="t">Quick insights</div>
            <div class="v">${summaryText}</div>
            <div class="s">
              <span class="${b.cls}">${b.label}: <strong>${b.value}</strong></span>
              <span style="display:inline-block; width:6px;"></span>
              <span class="${activityChip.cls}">Activity: <strong>${activityChip.text}</strong></span>
              <span style="display:inline-block; width:6px;"></span>
              <span class="${sleepChip.cls}">Sleep: <strong>${sleepChip.text}</strong></span>
            </div>
          </div>
          <div class="insight">
            <div class="t">Helpful next steps</div>
            <div class="v">${(worst.level === "urgent") ? "Seek urgent care if symptoms are severe." : "Use this to plan what to check next."}</div>
            <div class="s">Tip: click “Copy results” to share the output with a clinician or save it in notes.</div>
          </div>
        `;
      }

      function renderDataQuality(payload) {
        const missing = [];
        if (payload.height_cm == null || payload.weight_kg == null) missing.push("Height + weight (for BMI)");
        if (!payload.measurements || payload.measurements.systolic_bp == null || payload.measurements.diastolic_bp == null) missing.push("Blood pressure (systolic + diastolic)");
        if (!payload.measurements || payload.measurements.fasting_glucose_mg_dl == null) missing.push("Fasting glucose (or HbA1c)");
        if (!payload.measurements || payload.measurements.resting_spo2 == null) missing.push("Resting SpO2 (pulse oximeter)");

        const q = el("quality");
        if (!q) return;
        if (!missing.length) {
          q.style.display = "none";
          q.textContent = "";
          return;
        }
        q.style.display = "block";
        q.innerHTML = `<strong>Improve accuracy:</strong> add ${missing.join(", ")}.`;
      }

      function buildPayload() {
        const payload = {
          age: Number(el("age").value),
          sex: el("sex").value,
          height_cm: el("height").value === "" ? null : Number(el("height").value),
          weight_kg: el("weight").value === "" ? null : Number(el("weight").value),
          smoker: el("smoker").value === "true",
          alcohol_drinks_per_week: Number(el("alcohol").value || 0),
          activity_minutes_per_week: Number(el("activity").value || 0),
          sleep_hours: Number(el("sleep").value || 7),
          family_history: parseList(el("family").value),
          conditions: parseList(el("conditions").value),
          symptoms: parseList(el("symptoms").value),
          measurements: {
            systolic_bp: el("bp_sys").value === "" ? null : Number(el("bp_sys").value),
            diastolic_bp: el("bp_dia").value === "" ? null : Number(el("bp_dia").value),
            fasting_glucose_mg_dl: el("glu_fast").value === "" ? null : Number(el("glu_fast").value),
            resting_spo2: el("spo2").value === "" ? null : Number(el("spo2").value)
          }
        };
        el("reqjson").textContent = JSON.stringify(payload, null, 2);
        renderInsights(payload, null);
        renderDataQuality(payload);
        return payload;
      }

      function badgeClass(level) {
        if (level === "low") return "badge b-low";
        if (level === "moderate") return "badge b-moderate";
        if (level === "high") return "badge b-high";
        return "badge b-urgent";
      }

      function titleCase(s) {
        return (s || "").replace(/_/g, " ").replace(/\\b\\w/g, c => c.toUpperCase());
      }

      function meterClass(level) {
        if (level === "low") return "m-low";
        if (level === "moderate") return "m-moderate";
        if (level === "high") return "m-high";
        return "m-urgent";
      }

      function renderRisks(resp) {
        const root = el("results");
        root.innerHTML = "";

        const payload = buildPayload();
        renderInsights(payload, resp);
        renderDataQuality(payload);

        for (const [k, v] of Object.entries(resp.risks || {})) {
          const div = document.createElement("div");
          div.className = "risk";

          const h = document.createElement("h3");
          const left = document.createElement("div");
          left.textContent = titleCase(k);
          const right = document.createElement("span");
          right.className = badgeClass(v.level);
          right.textContent = `${v.level} • ${Math.round((v.score || 0) * 100)}%`;
          h.appendChild(left);
          h.appendChild(right);

          const meter = document.createElement("div");
          meter.className = "meter";
          const bar = document.createElement("div");
          bar.className = meterClass(v.level);
          bar.style.width = `${Math.max(0, Math.min(100, Math.round((v.score || 0) * 100)))}%`;
          meter.appendChild(bar);

          const consult = document.createElement("div");
          consult.className = "muted";
          consult.style.fontSize = "12px";
          consult.style.marginTop = "6px";
          consult.innerHTML = v.recommend_medical_consultation
            ? "<strong>Recommendation:</strong> consider medical consultation."
            : "<strong>Recommendation:</strong> self-care + routine follow-up.";

          const explain = document.createElement("div");
          explain.className = "muted";
          explain.style.fontSize = "12px";
          explain.style.marginTop = "8px";
          if (k === "heart_disease") {
            explain.innerHTML = "<strong>What this means:</strong> influenced by age, smoking, blood pressure, symptoms (chest pain/shortness of breath), and known conditions.";
          } else if (k === "diabetes") {
            explain.innerHTML = "<strong>What this means:</strong> influenced by BMI, family history, glucose readings, activity, sleep, and symptoms (thirst/urination/weight loss).";
          } else {
            explain.innerHTML = "<strong>What this means:</strong> influenced by smoking, oxygen level (SpO2), respiratory conditions, and symptoms (wheeze/cough/shortness of breath).";
          }

          const cHead = document.createElement("div");
          cHead.style.marginTop = "10px";
          cHead.innerHTML = "<strong>Top contributors</strong>";
          const cList = document.createElement("ul");
          cList.className = "list";
          (v.top_contributors || ["—"]).forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            cList.appendChild(li);
          });

          const tHead = document.createElement("div");
          tHead.style.marginTop = "10px";
          tHead.innerHTML = "<strong>Preventive measures</strong>";
          const tList = document.createElement("ul");
          tList.className = "list";
          (v.preventive_measures || ["—"]).forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            tList.appendChild(li);
          });

          div.appendChild(h);
          div.appendChild(meter);
          div.appendChild(consult);
          div.appendChild(explain);
          div.appendChild(cHead);
          div.appendChild(cList);
          div.appendChild(tHead);
          div.appendChild(tList);
          root.appendChild(div);
        }

        if (resp.disclaimer) {
          const d = document.createElement("div");
          d.className = "warn";
          d.style.marginTop = "12px";
          d.innerHTML = `<strong>Disclaimer:</strong> ${resp.disclaimer}`;
          root.appendChild(d);
        }
      }

      async function runPredict() {
        const runBtn = el("run");
        const status = el("status");
        status.textContent = "";
        runBtn.disabled = true;

        try {
          const payload = buildPayload();
          status.textContent = "Running...";
          const r = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          const data = await r.json();
          if (!r.ok) {
            throw new Error((data && data.detail && JSON.stringify(data.detail)) || `HTTP ${r.status}`);
          }
          renderRisks(data);
          status.textContent = "Done.";
        } catch (e) {
          el("results").innerHTML = `<div class="warn"><strong>Error:</strong> ${String(e.message || e)}</div>`;
          status.textContent = "Failed.";
        } finally {
          runBtn.disabled = false;
        }
      }

      el("f").addEventListener("submit", (ev) => {
        ev.preventDefault();
        runPredict();
      });

      ["age","sex","height","weight","smoker","activity","sleep","alcohol","bp_sys","bp_dia","glu_fast","spo2","family","conditions","symptoms"].forEach(id => {
        const node = el(id);
        if (!node) return;
        node.addEventListener("input", () => buildPayload());
      });
      buildPayload();

      el("copyResults").addEventListener("click", async () => {
        const s = el("copyStatus");
        s.textContent = "";
        try {
          const payload = buildPayload();
          const resText = el("results").textContent || "";
          const output = {
            request: payload,
            copied_at: new Date().toISOString(),
            note: "Informational only, not a diagnosis.",
            results_text: resText.trim()
          };
          await navigator.clipboard.writeText(JSON.stringify(output, null, 2));
          s.textContent = "Copied.";
        } catch (e) {
          s.textContent = "Copy failed (browser blocked clipboard).";
        }
      });

      el("loadExample").addEventListener("click", async () => {
        const status = el("status");
        status.textContent = "Loading example...";
        try {
          const r = await fetch("/example");
          const ex = await r.json();
          el("age").value = ex.age ?? 52;
          el("sex").value = ex.sex ?? "male";
          el("height").value = ex.height_cm ?? "";
          el("weight").value = ex.weight_kg ?? "";
          el("smoker").value = String(!!ex.smoker);
          el("activity").value = ex.activity_minutes_per_week ?? 0;
          el("sleep").value = ex.sleep_hours ?? 7.0;
          el("alcohol").value = ex.alcohol_drinks_per_week ?? 0;
          el("bp_sys").value = (ex.measurements && ex.measurements.systolic_bp) ?? "";
          el("bp_dia").value = (ex.measurements && ex.measurements.diastolic_bp) ?? "";
          el("glu_fast").value = (ex.measurements && ex.measurements.fasting_glucose_mg_dl) ?? "";
          el("spo2").value = (ex.measurements && ex.measurements.resting_spo2) ?? "";
          el("family").value = (ex.family_history || []).join(", ");
          el("conditions").value = (ex.conditions || []).join(", ");
          el("symptoms").value = (ex.symptoms || []).join(", ");
          buildPayload();
          status.textContent = "Example loaded.";
        } catch (e) {
          status.textContent = "Failed to load example.";
        }
      });
    </script>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return _HOME_HTML


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/example")
def example_request() -> dict:
    return {
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


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
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

