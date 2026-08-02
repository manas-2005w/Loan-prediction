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

# Set page configuration matching Picture 1
st.set_page_config(
    page_title="Loan Prediction Studio",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS Injection for Picture 1 UI design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    .stApp {
        background-color: #f4f7fb !important;
    }
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }
    
    /* Hero Banner */
    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #2563eb 45%, #38bdf8 100%);
        color: #ffffff;
        padding: 32px;
        border-radius: 24px;
        display: flex;
        justify-content: space-between;
        gap: 24px;
        align-items: center;
        box-shadow: 0 18px 45px rgba(37, 99, 235, 0.22);
        margin-bottom: 24px;
    }
    
    .hero-eyebrow {
        font-size: 0.8rem;
        letter-spacing: 0.24em;
        text-transform: uppercase;
        font-weight: 700;
        opacity: 0.9;
        margin-bottom: 10px;
    }
    
    .hero-title {
        margin: 0 0 10px;
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.15;
    }
    
    .hero-copy {
        margin: 0;
        font-size: 1rem;
        line-height: 1.6;
        max-width: 620px;
        opacity: 0.95;
    }
    
    .hero-badges {
        display: flex;
        flex-direction: column;
        gap: 10px;
        min-width: 200px;
    }
    
    .hero-badge-pill {
        background: rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(8px);
        padding: 10px 16px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.9rem;
        text-align: center;
        color: white;
    }
    
    /* Side Card */
    .side-card {
        background: #ffffff;
        border: 1px solid #dbe5f0;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
    }
    
    .side-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #14213d;
        margin-bottom: 12px;
    }
    
    .feature-list {
        padding-left: 18px;
        color: #5f6f8f;
        display: grid;
        gap: 8px;
        margin: 0 0 18px;
        font-size: 0.95rem;
    }
    
    .db-status-pill {
        margin-top: 16px;
        font-weight: 600;
        font-size: 0.95rem;
    }

    /* Result Banner */
    .prediction-banner {
        padding: 16px;
        border-radius: 14px;
        font-weight: 700;
        text-align: center;
        font-size: 1.2rem;
        margin-top: 16px;
    }
    .prediction-banner.approved {
        background: #dcfce7;
        color: #047857;
    }
    .prediction-banner.rejected {
        background: #fee2e2;
        color: #b91c1c;
    }

    /* Form Container */
    div[data-testid="stForm"] {
        background: #ffffff !important;
        border: 1px solid #dbe5f0 !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06) !important;
    }

    /* Styled Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 12px 24px !important;
        border-radius: 999px !important;
        border: none !important;
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.18) !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 28px rgba(37, 99, 235, 0.25) !important;
    }
    
    /* Table Styling */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Hero Header Banner matching Picture 1
st.markdown("""
<div class="hero-card">
    <div>
        <div class="hero-eyebrow">AI-powered lending assistant</div>
        <div class="hero-title">Make better loan decisions with confidence.</div>
        <div class="hero-copy">
            A refined experience for reviewing applicant details and estimating approval outcomes in seconds.
        </div>
    </div>
    <div class="hero-badges">
        <div class="hero-badge-pill">⚡ Instant review</div>
        <div class="hero-badge-pill">📈 Clear insights</div>
        <div class="hero-badge-pill">🔐 Trustworthy screening</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Grid Layout (2 Columns matching Picture 1)
col_main, col_side = st.columns([2.2, 1.0])

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
    # Form Container
    st.markdown("### Applicant profile")
    st.caption("Fill in the financial and personal details below to generate a prediction.")

    with st.form("loan_form"):
        col1, col2 = st.columns(2)
        
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

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("Predict eligibility")

with col_side:
    # Right Side Card matching Picture 1
    st.markdown("""
    <div class="side-card">
        <div class="side-title">What this tool checks</div>
        <ul class="feature-list">
            <li>Applicant profile and income stability</li>
            <li>Credit and repayment history</li>
            <li>Loan amount and tenure suitability</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if db_connected:
        st.markdown(f'<p class="db-status-pill" style="color:#16a34a;">🟢 {db_type} Database Connected</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="db-status-pill" style="color:#d97706;">🟢 Local Database Active</p>', unsafe_allow_html=True)

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

        with st.spinner("Calculating decision..."):
            try:
                resp = requests.post(f"{backend_url}/predict", json=payload, timeout=5)
                if resp.status_code == 200:
                    res_json = resp.json()
                    pred_class = res_json.get("prediction")
                    pred_text = res_json.get("prediction_text")
                    db_saved = res_json.get("db_saved", False)

                    if pred_class != 0:
                        st.markdown("""
                        <div class="prediction-banner approved">
                            Loan is Approved
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.markdown("""
                        <div class="prediction-banner rejected">
                            Loan is Rejected
                        </div>
                        """, unsafe_allow_html=True)

                    if db_saved:
                        st.caption("✅ Saved to database.")
                else:
                    st.error("Prediction failed.")
            except Exception as e:
                st.error(f"Backend connection error: {e}")

# History Section (Show Past Entries)
st.markdown("<br>", unsafe_allow_html=True)
show_history = st.button("📜 Show Past Entries")

if show_history:
    st.markdown("### 📜 Previous User Entries")
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
