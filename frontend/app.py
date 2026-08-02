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

# Set page configuration
st.set_page_config(
    page_title="LoanVision AI — Smart Lending Decisions",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Premium Dark-Mode Glassmorphism CSS ─────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #0f1629;
        --bg-card: rgba(15, 22, 41, 0.65);
        --bg-card-hover: rgba(20, 30, 55, 0.80);
        --glass-border: rgba(99, 130, 255, 0.12);
        --glass-border-hover: rgba(99, 130, 255, 0.28);
        --text-primary: #e8ecf4;
        --text-secondary: #8b97b8;
        --text-muted: #5a6583;
        --accent-primary: #6366f1;
        --accent-secondary: #818cf8;
        --accent-glow: rgba(99, 102, 241, 0.35);
        --success: #22c55e;
        --success-bg: rgba(34, 197, 94, 0.12);
        --success-border: rgba(34, 197, 94, 0.25);
        --danger: #ef4444;
        --danger-bg: rgba(239, 68, 68, 0.12);
        --danger-border: rgba(239, 68, 68, 0.25);
        --warning: #f59e0b;
        --cyan: #06b6d4;
        --radius-lg: 20px;
        --radius-md: 14px;
        --radius-sm: 10px;
        --radius-pill: 999px;
        --shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.35);
        --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.10);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    .stApp {
        background: var(--bg-primary) !important;
        background-image:
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99, 102, 241, 0.12), transparent),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(6, 182, 212, 0.08), transparent) !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 1280px !important;
    }

    /* ── Hide Streamlit default header/footer ── */
    header[data-testid="stHeader"] { background: transparent !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }

    /* ── Hero Section ── */
    .hero-wrap {
        position: relative;
        background: linear-gradient(135deg, #1a1040 0%, #0f1629 40%, #0c1a2e 70%, #0a1628 100%);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: 48px 44px;
        margin-bottom: 32px;
        overflow: hidden;
        box-shadow: var(--shadow-glass), var(--shadow-glow);
    }
    .hero-wrap::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-wrap::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.10) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--accent-secondary);
        background: rgba(99, 102, 241, 0.10);
        border: 1px solid rgba(99, 102, 241, 0.18);
        padding: 6px 16px;
        border-radius: var(--radius-pill);
        margin-bottom: 20px;
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 900;
        line-height: 1.1;
        color: var(--text-primary);
        margin: 0 0 14px;
        letter-spacing: -0.02em;
    }
    .hero-title span {
        background: linear-gradient(135deg, var(--accent-primary), var(--cyan));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-copy {
        font-size: 1.05rem;
        line-height: 1.7;
        color: var(--text-secondary);
        max-width: 640px;
        margin: 0;
    }
    .hero-stats {
        display: flex;
        gap: 12px;
        margin-top: 28px;
        flex-wrap: wrap;
    }
    .hero-stat {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: var(--radius-md);
        padding: 14px 22px;
        display: flex;
        align-items: center;
        gap: 10px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .hero-stat:hover {
        border-color: var(--glass-border-hover);
        background: rgba(255, 255, 255, 0.07);
        transform: translateY(-2px);
    }
    .hero-stat-icon {
        font-size: 1.3rem;
    }
    .hero-stat-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--text-secondary);
    }

    /* ── Glass Card ── */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: 32px;
        box-shadow: var(--shadow-glass);
        transition: border-color 0.3s ease;
    }
    .glass-card:hover {
        border-color: var(--glass-border-hover);
    }
    .card-header {
        margin-bottom: 24px;
    }
    .card-header h2 {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 6px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .card-header p {
        font-size: 0.88rem;
        color: var(--text-secondary);
        margin: 0;
    }

    /* ── Side Panel ── */
    .side-panel {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: 28px;
        box-shadow: var(--shadow-glass);
        margin-bottom: 20px;
    }
    .side-panel-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 20px;
    }
    .check-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    .check-item:last-child { border-bottom: none; }
    .check-icon {
        width: 28px;
        height: 28px;
        min-width: 28px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
    }
    .check-icon.purple {
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    .check-icon.cyan {
        background: rgba(6, 182, 212, 0.12);
        border: 1px solid rgba(6, 182, 212, 0.2);
    }
    .check-icon.amber {
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    .check-text {
        font-size: 0.9rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    .check-text strong {
        color: var(--text-primary);
        font-weight: 600;
    }

    /* ── DB Status Pill ── */
    .db-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 8px 16px;
        border-radius: var(--radius-pill);
        margin-top: 8px;
    }
    .db-pill.connected {
        background: var(--success-bg);
        border: 1px solid var(--success-border);
        color: var(--success);
    }
    .db-pill.local {
        background: rgba(245, 158, 11, 0.10);
        border: 1px solid rgba(245, 158, 11, 0.20);
        color: var(--warning);
    }

    /* ── Prediction Result Banners ── */
    .result-card {
        border-radius: var(--radius-lg);
        padding: 28px 32px;
        text-align: center;
        margin-top: 20px;
        position: relative;
        overflow: hidden;
    }
    .result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }
    .result-card.approved {
        background: var(--success-bg);
        border: 1px solid var(--success-border);
    }
    .result-card.approved::before {
        background: linear-gradient(90deg, var(--success), #4ade80);
    }
    .result-card.rejected {
        background: var(--danger-bg);
        border: 1px solid var(--danger-border);
    }
    .result-card.rejected::before {
        background: linear-gradient(90deg, var(--danger), #f87171);
    }
    .result-icon {
        font-size: 2.5rem;
        margin-bottom: 8px;
    }
    .result-label {
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: -0.01em;
    }
    .result-card.approved .result-label { color: var(--success); }
    .result-card.rejected .result-label { color: var(--danger); }
    .result-sub {
        font-size: 0.82rem;
        color: var(--text-muted);
        margin-top: 4px;
    }

    /* ── Streamlit form overrides ── */
    div[data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
    }

    /* Input / Select base styling */
    div[data-testid="stNumberInput"] label,
    div[data-testid="stSelectbox"] label {
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    div[data-testid="stNumberInput"] input:focus,
    div[data-baseweb="select"]:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }

    /* Submit button */
    div[data-testid="stForm"] button[type="submit"],
    div.stButton > button {
        background: linear-gradient(135deg, var(--accent-primary) 0%, #4f46e5 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 14px 36px !important;
        border-radius: var(--radius-pill) !important;
        border: none !important;
        box-shadow: 0 8px 24px var(--accent-glow) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.02em !important;
    }
    div[data-testid="stForm"] button[type="submit"]:hover,
    div.stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 14px 36px rgba(99, 102, 241, 0.35) !important;
    }

    /* Dataframe styling */
    div[data-testid="stDataFrame"] {
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
    }

    /* ── Section divider ── */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
        margin: 28px 0;
    }

    /* ── Animated dot ── */
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse-dot 2s ease-in-out infinite;
    }
    .pulse-dot.green { background: var(--success); }
    .pulse-dot.amber { background: var(--warning); }

    /* ── Footer ── */
    .app-footer {
        text-align: center;
        padding: 32px 0 16px;
        font-size: 0.78rem;
        color: var(--text-muted);
    }
    .app-footer a {
        color: var(--accent-secondary);
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">✦ AI-Powered Lending Intelligence</div>
    <h1 class="hero-title">Smarter Loan Decisions,<br><span>Built with Confidence.</span></h1>
    <p class="hero-copy">
        Instantly evaluate applicant profiles against our trained ML model.
        Get clear, data-driven approval predictions in seconds — no guesswork.
    </p>
    <div class="hero-stats">
        <div class="hero-stat">
            <span class="hero-stat-icon">⚡</span>
            <span class="hero-stat-label">Instant Predictions</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-icon">🎯</span>
            <span class="hero-stat-label">ML-Driven Accuracy</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-icon">🔒</span>
            <span class="hero-stat-label">Secure & Logged</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-icon">📊</span>
            <span class="hero-stat-label">Full Audit Trail</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Main Grid Layout ─────────────────────────────────────────────────────────
col_main, col_side = st.columns([2.4, 1.0], gap="large")

# Check DB / Backend Health
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

with col_main:
    # Form Card
    st.markdown("""
    <div class="glass-card">
        <div class="card-header">
            <h2>📋 Applicant Profile</h2>
            <p>Complete the financial and personal details below to generate a prediction.</p>
        </div>
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

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀  Predict Eligibility")

with col_side:
    # What This Tool Checks
    st.markdown("""
    <div class="side-panel">
        <div class="side-panel-title">What This Tool Checks</div>
        <div class="check-item">
            <div class="check-icon purple">📊</div>
            <div class="check-text"><strong>Income Stability</strong><br>Applicant profile and income assessment</div>
        </div>
        <div class="check-item">
            <div class="check-icon cyan">🏦</div>
            <div class="check-text"><strong>Credit History</strong><br>CIBIL score and repayment track record</div>
        </div>
        <div class="check-item">
            <div class="check-icon amber">⚖️</div>
            <div class="check-text"><strong>Loan Suitability</strong><br>Amount and tenure feasibility analysis</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # DB status
    if db_connected:
        st.markdown(f"""
        <div class="db-pill connected">
            <span class="pulse-dot green"></span> {db_type} Database Connected
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="db-pill local">
            <span class="pulse-dot amber"></span> Local Database Active
        </div>
        """, unsafe_allow_html=True)

    # Form Submission Execution & Verdict Display
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

        with st.spinner("Analyzing applicant profile..."):
            try:
                resp = requests.post(f"{backend_url}/predict", json=payload, timeout=5)
                if resp.status_code == 200:
                    res_json = resp.json()
                    pred_class = res_json.get("prediction")
                    pred_text = res_json.get("prediction_text")
                    db_saved = res_json.get("db_saved", False)

                    if pred_class != 0:
                        st.markdown("""
                        <div class="result-card approved">
                            <div class="result-icon">✅</div>
                            <div class="result-label">Loan is Approved</div>
                            <div class="result-sub">Applicant meets eligibility criteria</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.markdown("""
                        <div class="result-card rejected">
                            <div class="result-icon">❌</div>
                            <div class="result-label">Loan is Rejected</div>
                            <div class="result-sub">Applicant does not meet criteria at this time</div>
                        </div>
                        """, unsafe_allow_html=True)

                    if db_saved:
                        st.caption("✅ Result logged to database.")
                else:
                    st.error("Prediction failed.")
            except Exception as e:
                st.error(f"Backend connection error: {e}")

# ── History Section ───────────────────────────────────────────────────────────
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
show_history = st.button("📜  Show Past Entries")

if show_history:
    st.markdown("""
    <div class="glass-card" style="margin-top: 12px;">
        <div class="card-header">
            <h2>📜 Prediction History</h2>
            <p>Previously submitted applications and their verdicts.</p>
        </div>
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
                st.info("No previous user entries found in database.")
        else:
            st.warning("Unable to fetch history from database.")
    except Exception as ex:
        st.error(f"Error fetching history: {ex}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    Built with ❤️ using <a href="https://streamlit.io" target="_blank">Streamlit</a> &amp; FastAPI · LoanVision AI
</div>
""", unsafe_allow_html=True)
