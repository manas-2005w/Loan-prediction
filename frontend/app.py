import os
import streamlit as st
import requests
import pandas as pd
import threading
import time
import sys

# Auto-start FastAPI backend in a background thread if it is set to localhost/127.0.0.1
# and no server is currently listening on that port.
DEFAULT_BACKEND = os.getenv("BACKEND_URL", "http://localhost:8080")

if "localhost" in DEFAULT_BACKEND or "127.0.0.1" in DEFAULT_BACKEND:
    port = 8080
    try:
        port = int(DEFAULT_BACKEND.split(":")[-1].split("/")[0])
    except Exception:
        pass
    
    try:
        requests.get(f"http://127.0.0.1:{port}/health", timeout=1)
    except Exception:
        try:
            backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
            if backend_dir not in sys.path:
                sys.path.append(backend_dir)
            
            from main import app as fastapi_app
            import uvicorn
            
            def run_fastapi():
                uvicorn.run(fastapi_app, host="127.0.0.1", port=port)
                
            t = threading.Thread(target=run_fastapi, daemon=True)
            t.start()
            time.sleep(2)
        except Exception:
            pass

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LoanVision AI — Smart Lending Decisions",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS — Midnight Ember Dark Theme ──────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --bg-deep: #07080d;
        --bg-surface: #0d0f17;
        --bg-elevated: #13161f;
        --bg-card: #161923;
        --border-dim: rgba(255, 255, 255, 0.04);
        --border-subtle: rgba(255, 255, 255, 0.07);
        --border-accent: rgba(251, 146, 60, 0.20);
        --text-white: #f1f3f8;
        --text-light: #c4c9d8;
        --text-mid: #8890a4;
        --text-dim: #525a72;
        --ember: #fb923c;
        --ember-deep: #ea580c;
        --ember-glow: rgba(251, 146, 60, 0.18);
        --teal: #2dd4bf;
        --teal-glow: rgba(45, 212, 191, 0.12);
        --violet: #a78bfa;
        --green: #4ade80;
        --green-bg: rgba(74, 222, 128, 0.08);
        --green-border: rgba(74, 222, 128, 0.18);
        --red: #f87171;
        --red-bg: rgba(248, 113, 113, 0.08);
        --red-border: rgba(248, 113, 113, 0.18);
        --r-xl: 24px;
        --r-lg: 18px;
        --r-md: 12px;
        --r-sm: 8px;
    }

    html, body, [class*="css"] {
        font-family: 'Outfit', 'Space Grotesk', sans-serif !important;
    }

    /* ── Global Background ── */
    .stApp {
        background: var(--bg-deep) !important;
        background-image:
            radial-gradient(ellipse 70% 55% at 20% -10%, rgba(251, 146, 60, 0.06), transparent),
            radial-gradient(ellipse 50% 50% at 85% 110%, rgba(45, 212, 191, 0.04), transparent) !important;
    }

    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 4rem !important;
        max-width: 1320px !important;
    }

    /* ── Hide defaults ── */
    header[data-testid="stHeader"] { background: transparent !important; }
    footer, #MainMenu { display: none !important; }

    /* ──────────────── HERO ──────────────── */
    .lv-hero {
        position: relative;
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-xl);
        padding: 0;
        overflow: hidden;
        margin-bottom: 28px;
        display: flex;
    }
    .lv-hero-left {
        flex: 1;
        padding: 44px 48px;
        z-index: 1;
    }
    .lv-hero-right {
        width: 340px;
        min-height: 100%;
        background: linear-gradient(160deg, rgba(251, 146, 60, 0.08) 0%, rgba(45, 212, 191, 0.05) 100%);
        border-left: 1px solid var(--border-dim);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 36px 32px;
        gap: 16px;
        z-index: 1;
    }
    /* ambient glow */
    .lv-hero::before {
        content: '';
        position: absolute;
        top: -60%;
        left: -15%;
        width: 450px;
        height: 450px;
        background: radial-gradient(circle, var(--ember-glow) 0%, transparent 70%);
        pointer-events: none;
    }
    .lv-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--ember);
        background: var(--ember-glow);
        border: 1px solid rgba(251, 146, 60, 0.15);
        padding: 5px 14px;
        border-radius: 999px;
        margin-bottom: 18px;
    }
    .lv-hero-title {
        font-size: 2.6rem;
        font-weight: 900;
        line-height: 1.08;
        color: var(--text-white);
        margin: 0 0 14px;
        letter-spacing: -0.03em;
    }
    .lv-hero-title em {
        font-style: normal;
        background: linear-gradient(135deg, var(--ember) 0%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .lv-hero-sub {
        font-size: 1rem;
        line-height: 1.7;
        color: var(--text-mid);
        margin: 0;
        max-width: 560px;
    }

    /* hero right metric chips */
    .lv-chip {
        width: 100%;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--border-dim);
        border-radius: var(--r-md);
        padding: 14px 18px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.3s ease;
    }
    .lv-chip:hover {
        border-color: var(--border-accent);
        background: rgba(255, 255, 255, 0.05);
        transform: translateX(-4px);
    }
    .lv-chip-icon {
        width: 36px;
        height: 36px;
        min-width: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .lv-chip-icon.ember { background: var(--ember-glow); }
    .lv-chip-icon.teal  { background: var(--teal-glow); }
    .lv-chip-icon.violet { background: rgba(167, 139, 250, 0.12); }
    .lv-chip-text {
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--text-light);
    }

    /* ──────────────── FORM CARD ──────────────── */
    .lv-form-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-xl);
        padding: 36px;
    }
    .lv-form-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 8px;
    }
    .lv-form-icon {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        background: var(--ember-glow);
        border: 1px solid rgba(251, 146, 60, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    .lv-form-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-white);
        margin: 0;
    }
    .lv-form-sub {
        font-size: 0.85rem;
        color: var(--text-dim);
        margin: 4px 0 0 58px;
        padding-bottom: 24px;
        border-bottom: 1px solid var(--border-dim);
        margin-bottom: 4px;
    }

    /* ──────────────── SIDE PANEL ──────────────── */
    .lv-side {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-xl);
        padding: 28px;
        margin-bottom: 20px;
    }
    .lv-side-label {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--text-dim);
        margin-bottom: 20px;
    }
    .lv-feature {
        display: flex;
        gap: 14px;
        padding: 14px 0;
        border-bottom: 1px solid var(--border-dim);
        align-items: flex-start;
    }
    .lv-feature:last-child { border-bottom: none; }
    .lv-f-icon {
        width: 34px;
        height: 34px;
        min-width: 34px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
    }
    .lv-f-icon.a { background: var(--ember-glow); border: 1px solid rgba(251, 146, 60, 0.12); }
    .lv-f-icon.b { background: var(--teal-glow); border: 1px solid rgba(45, 212, 191, 0.12); }
    .lv-f-icon.c { background: rgba(167, 139, 250, 0.10); border: 1px solid rgba(167, 139, 250, 0.12); }
    .lv-f-title {
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--text-light);
        margin: 0 0 2px;
    }
    .lv-f-desc {
        font-size: 0.78rem;
        color: var(--text-dim);
        margin: 0;
        line-height: 1.5;
    }

    /* ──────────────── STATUS PILL ──────────────── */
    .lv-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.76rem;
        font-weight: 600;
        padding: 7px 16px;
        border-radius: 999px;
        margin-top: 6px;
    }
    .lv-status.ok {
        background: var(--green-bg);
        border: 1px solid var(--green-border);
        color: var(--green);
    }
    .lv-status.warn {
        background: var(--ember-glow);
        border: 1px solid rgba(251, 146, 60, 0.18);
        color: var(--ember);
    }
    @keyframes blink {
        0%,100% { opacity:1; }
        50% { opacity:0.3; }
    }
    .lv-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        display: inline-block;
        animation: blink 2s ease-in-out infinite;
    }
    .lv-dot.g { background: var(--green); }
    .lv-dot.o { background: var(--ember); }

    /* ──────────────── RESULT BANNER ──────────────── */
    .lv-result {
        border-radius: var(--r-lg);
        padding: 26px;
        text-align: center;
        margin-top: 20px;
        position: relative;
        overflow: hidden;
    }
    .lv-result::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
    }
    .lv-result.pass {
        background: var(--green-bg);
        border: 1px solid var(--green-border);
    }
    .lv-result.pass::after { background: linear-gradient(90deg, var(--green), var(--teal)); }
    .lv-result.fail {
        background: var(--red-bg);
        border: 1px solid var(--red-border);
    }
    .lv-result.fail::after { background: linear-gradient(90deg, var(--red), #fb923c); }
    .lv-res-icon { font-size: 2.2rem; margin-bottom: 6px; }
    .lv-res-text {
        font-size: 1.3rem;
        font-weight: 800;
        letter-spacing: -0.01em;
    }
    .lv-result.pass .lv-res-text { color: var(--green); }
    .lv-result.fail .lv-res-text { color: var(--red); }
    .lv-res-sub {
        font-size: 0.78rem;
        color: var(--text-dim);
        margin-top: 4px;
    }

    /* ──────────────── STREAMLIT WIDGET OVERRIDES ──────────────── */
    div[data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
    }

    /* labels */
    div[data-testid="stNumberInput"] label p,
    div[data-testid="stSelectbox"] label p {
        color: var(--text-mid) !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
    }

    /* inputs */
    div[data-testid="stNumberInput"] input {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--r-sm) !important;
        color: var(--text-white) !important;
        font-family: 'Space Grotesk', monospace !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    div[data-testid="stNumberInput"] input:focus {
        border-color: var(--ember) !important;
        box-shadow: 0 0 0 3px var(--ember-glow) !important;
    }

    /* selectbox */
    div[data-baseweb="select"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--r-sm) !important;
        color: var(--text-white) !important;
    }
    div[data-baseweb="select"]:focus-within {
        border-color: var(--ember) !important;
        box-shadow: 0 0 0 3px var(--ember-glow) !important;
    }

    /* Submit & Action buttons */
    div[data-testid="stForm"] button[type="submit"],
    div.stButton > button {
        background: linear-gradient(135deg, var(--ember-deep) 0%, var(--ember) 100%) !important;
        color: #fff !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        padding: 14px 40px !important;
        border-radius: 999px !important;
        border: none !important;
        box-shadow: 0 6px 24px var(--ember-glow) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.03em !important;
    }
    div[data-testid="stForm"] button[type="submit"]:hover,
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 36px rgba(251, 146, 60, 0.30) !important;
    }

    /* history section header */
    .lv-hist-header {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--r-xl);
        padding: 28px 36px;
        margin-top: 12px;
        margin-bottom: 8px;
    }
    .lv-hist-header h2 {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-white);
        margin: 0 0 4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .lv-hist-header p {
        font-size: 0.82rem;
        color: var(--text-dim);
        margin: 0;
    }

    /* dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: var(--r-md) !important;
        overflow: hidden !important;
    }

    /* section break */
    .lv-break {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-subtle), transparent);
        margin: 32px 0;
    }

    /* footer */
    .lv-footer {
        text-align: center;
        padding: 36px 0 12px;
        font-size: 0.75rem;
        color: var(--text-dim);
    }
    .lv-footer a {
        color: var(--ember);
        text-decoration: none;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  HERO SECTION
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="lv-hero">
    <div class="lv-hero-left">
        <div class="lv-tag">✦ AI-Powered Lending Engine</div>
        <h1 class="lv-hero-title">Predict Loan Approvals<br>with <em>Confidence.</em></h1>
        <p class="lv-hero-sub">
            Feed applicant data into our trained ML model and get instant,
            data-driven eligibility verdicts — no guesswork, just results.
        </p>
    </div>
    <div class="lv-hero-right">
        <div class="lv-chip">
            <div class="lv-chip-icon ember">⚡</div>
            <span class="lv-chip-text">Real-time Predictions</span>
        </div>
        <div class="lv-chip">
            <div class="lv-chip-icon teal">🎯</div>
            <span class="lv-chip-text">ML-Driven Accuracy</span>
        </div>
        <div class="lv-chip">
            <div class="lv-chip-icon violet">🔒</div>
            <span class="lv-chip-text">Secure Audit Trail</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════
col_main, col_side = st.columns([2.4, 1.0], gap="large")

# Backend / DB health
backend_url = os.getenv("BACKEND_URL", "http://localhost:8080")
db_connected = False
db_type = "MySQL"

try:
    health_resp = requests.get(f"{backend_url}/health", timeout=2)
    if health_resp.status_code == 200:
        db_type_res = health_resp.json().get("database_type", "mysql")
        db_type = "MySQL" if "mysql" in db_type_res else "SQLite"
        db_connected = True
except Exception:
    db_connected = False

# ── Left Column — Form ───────────────────────────────────────────────────────
with col_main:
    st.markdown("""
    <div class="lv-form-card">
        <div class="lv-form-header">
            <div class="lv-form-icon">📋</div>
            <h3 class="lv-form-title">Applicant Profile</h3>
        </div>
        <p class="lv-form-sub">Fill in all financial &amp; personal details to generate a prediction.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("loan_form"):
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            age = st.number_input("Customer Age", min_value=18, max_value=100, value=35, step=1)
            income = st.number_input("Applicant Income (₹)", min_value=0, value=45000, step=1000)
            cibil = st.number_input("CIBIL Score", min_value=300, max_value=900, value=720, step=5)
            gender = st.selectbox("Gender", options=["Male", "Female"], index=0)
            education = st.selectbox("Education", options=["Graduate", "Not Graduate"], index=0)
            prev_loan = st.selectbox("Previous Loan Taken", options=["Yes", "No"], index=0)
            bandwidth = st.selectbox("Customer Bandwith", options=["Good", "Medium", "Bad"], index=0)

        with col2:
            dependents = st.number_input("Dependents", min_value=0, max_value=5, value=2, step=1)
            loan_amount = st.number_input("Loan Amount (₹)", min_value=0, value=250000, step=5000)
            tenure = st.number_input("Tenure (months)", min_value=1, max_value=360, value=24, step=1)
            married = st.selectbox("Married", options=["Yes", "No"], index=0)
            self_employed = st.selectbox("Self Employed", options=["Yes", "No"], index=1)
            property_area = st.selectbox("Property Area", options=["Rural", "Semiurban", "Urban"], index=0)

        st.markdown('<div class="lv-break"></div>', unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀  Predict Eligibility")

# ── Right Column — Info Panel ─────────────────────────────────────────────────
with col_side:
    st.markdown("""
    <div class="lv-side">
        <div class="lv-side-label">Evaluation Criteria</div>
        <div class="lv-feature">
            <div class="lv-f-icon a">📊</div>
            <div>
                <p class="lv-f-title">Income Stability</p>
                <p class="lv-f-desc">Evaluates income level and employment type</p>
            </div>
        </div>
        <div class="lv-feature">
            <div class="lv-f-icon b">🏦</div>
            <div>
                <p class="lv-f-title">Credit History</p>
                <p class="lv-f-desc">CIBIL score and repayment track record</p>
            </div>
        </div>
        <div class="lv-feature">
            <div class="lv-f-icon c">⚖️</div>
            <div>
                <p class="lv-f-title">Loan Suitability</p>
                <p class="lv-f-desc">Amount vs tenure feasibility analysis</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # DB status
    if db_connected:
        st.markdown(f"""
        <div class="lv-status ok">
            <span class="lv-dot g"></span> {db_type} Connected
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="lv-status warn">
            <span class="lv-dot o"></span> Local DB Active
        </div>
        """, unsafe_allow_html=True)

    # ── Prediction execution ──────────────────────────────────────────────────
    if submit_btn:
        dep_val = int(dependents)
        gen_val = 1 if gender == "Male" else 0
        mar_val = 1 if married == "Yes" else 0
        edu_val = 1 if "Graduate" in education else 0
        emp_val = 1 if self_employed == "Yes" else 0
        prev_val = 1 if prev_loan == "Yes" else 0

        prop_map = {"Rural": 0, "Semiurban": 1, "Urban": 2}
        prop_val = prop_map[property_area]

        band_map = {"Bad": 0, "Good": 1, "Medium": 2}
        band_val = band_map[bandwidth]

        payload = {
            "Age": int(age),
            "Dependents": dep_val,
            "ApplicantIncome": int(income),
            "LoanAmount": int(loan_amount),
            "Cibil_Score": int(cibil),
            "Tenure": int(tenure),
            "Gender": gen_val,
            "Married": mar_val,
            "Education": edu_val,
            "Self_Employed": emp_val,
            "Previous_Loan_Taken": prev_val,
            "Property_Area": prop_val,
            "Customer_Bandwith": band_val
        }

        with st.spinner("Analyzing applicant profile…"):
            try:
                resp = requests.post(f"{backend_url}/predict", json=payload, timeout=5)
                if resp.status_code == 200:
                    res_json = resp.json()
                    pred_class = res_json.get("prediction")
                    pred_text = res_json.get("prediction_text")
                    db_saved = res_json.get("db_saved", False)

                    if pred_class != 0:
                        st.markdown("""
                        <div class="lv-result pass">
                            <div class="lv-res-icon">✅</div>
                            <div class="lv-res-text">Loan Approved</div>
                            <div class="lv-res-sub">Applicant meets all eligibility criteria</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.markdown("""
                        <div class="lv-result fail">
                            <div class="lv-res-icon">❌</div>
                            <div class="lv-res-text">Loan Rejected</div>
                            <div class="lv-res-sub">Applicant does not meet criteria at this time</div>
                        </div>
                        """, unsafe_allow_html=True)

                    if db_saved:
                        st.caption("✅ Result saved to database.")
                else:
                    st.error("Prediction failed.")
            except Exception as e:
                st.error(f"Backend connection error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
#  HISTORY SECTION
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="lv-break"></div>', unsafe_allow_html=True)
show_history = st.button("📜  Show Past Entries")

if show_history:
    st.markdown("""
    <div class="lv-hist-header">
        <h2>📜 Prediction History</h2>
        <p>All previously submitted applications and their verdicts.</p>
    </div>
    """, unsafe_allow_html=True)
    try:
        hist_resp = requests.get(f"{backend_url}/predictions", timeout=3)
        if hist_resp.status_code == 200:
            hist_data = hist_resp.json()
            if len(hist_data) > 0:
                df = pd.DataFrame(hist_data)
                df_display = df.rename(columns={
                    "id": "ID",
                    "prediction_result": "Verdict",
                    "age": "Age",
                    "income": "Income (₹)",
                    "loan_amount": "Loan Amount (₹)",
                    "cibil_score": "CIBIL Score",
                    "tenure": "Tenure (Mo)",
                    "gender": "Gender",
                    "married": "Married",
                    "education": "Education",
                    "self_employed": "Self Employed",
                    "previous_loan_taken": "Prev Loan",
                    "property_area": "Property Area",
                    "customer_bandwidth": "Bandwidth",
                    "created_at": "Timestamp"
                })
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("No previous entries found in database.")
        else:
            st.warning("Unable to fetch history from database.")
    except Exception as ex:
        st.error(f"Error fetching history: {ex}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lv-footer">
    Built with ❤️ using <a href="https://streamlit.io" target="_blank">Streamlit</a> &amp; FastAPI · LoanVision AI
</div>
""", unsafe_allow_html=True)
