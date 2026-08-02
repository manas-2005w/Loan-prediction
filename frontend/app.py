import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configurations
st.set_page_config(
    page_title="Elite Loan Approval Predictor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium UI CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        text-align: center;
        animation: fadeIn 1s ease-in-out;
    }
    
    .main-header h1 {
        font-weight: 800;
        font-size: 2.8rem;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .main-header p {
        font-weight: 300;
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
        margin-bottom: 1.5rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        border-radius: 30px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(56, 239, 125, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100%;
        font-size: 1.1rem !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(56, 239, 125, 0.5) !important;
    }
    
    .result-approved {
        background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
        border-left: 10px solid #27ae60;
        padding: 2rem;
        border-radius: 12px;
        color: #1e4620;
        font-weight: 600;
        font-size: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.2);
    }
    
    .result-rejected {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        border-left: 10px solid #c0392b;
        padding: 2rem;
        border-radius: 12px;
        color: #5c1d1d;
        font-weight: 600;
        font-size: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(192, 57, 43, 0.2);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/clouds/200/bank.png", width=120)
st.sidebar.markdown("### ⚙️ System Settings")

# Configure API Endpoint (can point to Render or localhost)
DEFAULT_BACKEND = os.getenv("BACKEND_URL", "http://localhost:8080")
backend_url = st.sidebar.text_input("FastAPI Backend URL:", value=DEFAULT_BACKEND)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 🧠 About the ML Model
- **Algorithm:** Decision Tree Classifier
- **Features Trained:** 13 variables
- **Hyperparameters:**
  - `max_depth = 4`
  - `min_samples_leaf = 50`
  - `min_samples_split = 300`
- **Output:** Binary Approval Prediction
""")

# Check Backend API Health on Load
try:
    health_resp = requests.get(f"{backend_url}/health", timeout=3)
    if health_resp.status_code == 200:
        db_type = health_resp.json().get("database_type", "mysql")
        st.sidebar.success(f"🟢 Connected to Backend API\nDatabase: {db_type.upper()}")
    else:
        st.sidebar.warning("⚠️ Backend online, but returned abnormal health status.")
except Exception:
    st.sidebar.error("🔴 Disconnected from Backend API. Please check your backend is running or update the URL.")

# Main Page Header
st.markdown("""
<div class="main-header">
    <h1>🏦 ELITE LOAN APPROVAL PREDICTOR</h1>
    <p>Empowered by Machine Learning. Instantly predict and analyze mortgage loan applications.</p>
</div>
""", unsafe_allow_html=True)

# Tabs structure
tab1, tab2 = st.tabs(["📝 Apply & Predict", "📊 Prediction Analytics Dashboard"])

with tab1:
    st.markdown("### 📋 Customer Demographics & Loan Details")
    
    # Setup form
    with st.form("loan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Applicant Profile")
            age = st.slider("Applicant Age", min_value=18, max_value=100, value=35, help="Select customer age.")
            gender = st.selectbox("Gender", options=["Male", "Female"], index=0)
            married = st.selectbox("Marital Status", options=["Yes", "No"], index=0)
            dependents = st.selectbox("Number of Dependents", options=["0", "1", "2", "3", "4", "5+"], index=0)
            education = st.selectbox("Is Graduate?", options=["Yes (Graduate)", "No (Not Graduate)"], index=0)
            self_employed = st.selectbox("Self Employed?", options=["Yes", "No"], index=1)
            
        with col2:
            st.markdown("#### 💰 Financials & Requirements")
            income = st.number_input("Monthly Applicant Income ($)", min_value=0, value=45000, step=1000, help="Gross monthly income.")
            loan_amount = st.number_input("Requested Loan Amount ($)", min_value=0, value=250000, step=5000, help="Total mortgage amount requested.")
            cibil = st.slider("CIBIL Score", min_value=300, max_value=900, value=720, help="Credit scoring index.")
            tenure = st.slider("Loan Tenure (in Months)", min_value=1, max_value=360, value=24, help="Timeframe to repay the loan.")
            prev_loan = st.selectbox("Has Previous Loan History?", options=["Yes", "No"], index=0)
            property_area = st.selectbox("Property Area Type", options=["Rural", "Semiurban", "Urban"], index=2)
            bandwidth = st.selectbox("Customer Bandwidth Category", options=["Good", "Medium", "Bad"], index=0)

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_key = st.form_submit_button("Predict Approval Status")

    # Form Submission Logic
    if submit_btn:
        # Encodings mapping
        # Dependents: 5+ maps to 5
        dep_val = 5 if dependents == "5+" else int(dependents)
        
        # Binary variables mapping
        gen_val = 1 if gender == "Male" else 0
        mar_val = 1 if married == "Yes" else 0
        edu_val = 1 if "Yes" in education else 0
        emp_val = 1 if self_employed == "Yes" else 0
        prev_val = 1 if prev_loan == "Yes" else 0
        
        # Property mapping: Rural=0, Semiurban=1, Urban=2
        prop_map = {"Rural": 0, "Semiurban": 1, "Urban": 2}
        prop_val = prop_map[property_area]
        
        # Bandwidth mapping: Bad=0, Good=1, Medium=2
        band_map = {"Bad": 0, "Good": 1, "Medium": 2}
        band_val = band_map[bandwidth]

        payload = {
            "Age": age,
            "Dependents": dep_val,
            "ApplicantIncome": income,
            "LoanAmount": loan_amount,
            "Cibil_Score": cibil,
            "Tenure": tenure,
            "Gender": gen_val,
            "Married": mar_val,
            "Education": edu_val,
            "Self_Employed": emp_val,
            "Previous_Loan_Taken": prev_val,
            "Property_Area": prop_val,
            "Customer_Bandwith": band_val
        }

        with st.spinner("Analyzing creditworthiness & generating prediction..."):
            try:
                resp = requests.post(f"{backend_url}/predict", json=payload)
                if resp.status_code == 200:
                    res_json = resp.json()
                    pred_class = res_json.get("prediction")
                    pred_text = res_json.get("prediction_text")
                    db_saved = res_json.get("db_saved", False)

                    st.markdown("### 🎯 Evaluation Verdict")
                    if pred_class != 0:
                        # Success Approval Box
                        st.markdown(f"""
                        <div class="result-approved">
                            🎉 LOAN APPROVED SUCCESSFULLY! <br>
                            <span style="font-size:1.1rem; font-weight:300;">The applicant meets the ML algorithm criteria for credit approval.</span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    else:
                        # Rejection Box
                        st.markdown(f"""
                        <div class="result-rejected">
                            ❌ LOAN REJECTED <br>
                            <span style="font-size:1.1rem; font-weight:300;">The applicant does not satisfy the requirements of the Decision Tree model.</span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.warning("💡 Recommend increasing the CIBIL score or reducing the requested Loan Amount.")

                    # Visual Gauges / Score breakdown
                    col_gauge1, col_gauge2 = st.columns(2)
                    with col_gauge1:
                        # CIBIL Score gauge
                        fig_cibil = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = cibil,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "CIBIL score strength", 'font': {'size': 18}},
                            gauge = {
                                'axis': {'range': [300, 900], 'tickwidth': 1, 'tickcolor': "darkblue"},
                                'bar': {'color': "#2c3e50"},
                                'bgcolor': "white",
                                'borderwidth': 2,
                                'bordercolor': "gray",
                                'steps': [
                                    {'range': [300, 550], 'color': '#ff9a9e'},
                                    {'range': [550, 700], 'color': '#fecfef'},
                                    {'range': [700, 900], 'color': '#96e6a1'}
                                ]
                            }
                        ))
                        fig_cibil.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig_cibil, use_container_width=True)
                        
                    with col_gauge2:
                        # Debt to Income Ratio estimate
                        dti = (loan_amount / tenure) / (income if income > 0 else 1) * 100
                        fig_dti = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = round(dti, 1),
                            number = {'suffix': "%"},
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Estimated Monthly Installment to Income Ratio", 'font': {'size': 18}},
                            gauge = {
                                'axis': {'range': [0, 100], 'tickwidth': 1},
                                'bar': {'color': "#2980b9"},
                                'steps': [
                                    {'range': [0, 35], 'color': '#96e6a1'},
                                    {'range': [35, 50], 'color': '#fecfef'},
                                    {'range': [50, 100], 'color': '#ff9a9e'}
                                ]
                            }
                        ))
                        fig_dti.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig_dti, use_container_width=True)

                    if db_saved:
                        st.caption("✅ Transaction successfully logged to database.")
                    else:
                        st.caption("⚠️ Prediction generated offline or server failed to connect to MySQL database.")

                else:
                    st.error(f"Error from server backend: {resp.status_code} - {resp.text}")
            except Exception as e:
                st.error(f"Connection failure: Could not reach backend API at {backend_url}. Verify service is live. Details: {e}")

with tab2:
    st.markdown("### 📈 Live Database Records & Visual Analytics")
    
    # Reload button
    if st.button("🔄 Refresh Analytics from DB"):
        st.rerun()

    # Fetch History
    try:
        hist_resp = requests.get(f"{backend_url}/predictions", timeout=3)
        if hist_resp.status_code == 200:
            hist_data = hist_resp.json()
            
            if len(hist_data) > 0:
                df = pd.DataFrame(hist_data)
                
                # Show key KPIs
                total_runs = len(df)
                approvals = len(df[df['prediction_result'] == 'Loan is Approved'])
                rejections = total_runs - approvals
                approval_rate = (approvals / total_runs) * 100 if total_runs > 0 else 0
                
                kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
                kpi_col1.metric("Total Evaluation Logs", total_runs)
                kpi_col2.metric("Approvals", approvals)
                kpi_col3.metric("Rejections", rejections)
                kpi_col4.metric("Approval Success Rate", f"{approval_rate:.1f}%")
                
                # Display charts
                st.markdown("#### 📊 Metric Visualizations")
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    # Pie chart for approvals
                    pie_data = df['prediction_result'].value_counts().reset_index()
                    pie_data.columns = ['Result', 'Count']
                    fig_pie = px.pie(
                        pie_data, 
                        names='Result', 
                        values='Count',
                        color='Result',
                        color_discrete_map={'Loan is Approved': '#2ecc71', 'Loan is Rejected': '#e74c3c'},
                        title='Overall Approval Distribution',
                        hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with chart_col2:
                    # Cibil score by approval
                    fig_box = px.box(
                        df, 
                        x='prediction_result', 
                        y='cibil_score', 
                        color='prediction_result',
                        color_discrete_map={'Loan is Approved': '#2ecc71', 'Loan is Rejected': '#e74c3c'},
                        title='CIBIL Score vs Approval Status',
                        labels={'prediction_result': 'Result', 'cibil_score': 'CIBIL Score'}
                    )
                    st.plotly_chart(fig_box, use_container_width=True)

                st.markdown("#### 🔍 Scatter Matrix (Income vs Loan Amount vs CIBIL)")
                fig_scatter = px.scatter(
                    df, 
                    x='income', 
                    y='loan_amount', 
                    color='prediction_result',
                    size='cibil_score',
                    hover_data=['age', 'gender', 'property_area'],
                    color_discrete_map={'Loan is Approved': '#2ecc71', 'Loan is Rejected': '#e74c3c'},
                    title='Income vs Requested Loan Amount (Sized by CIBIL Score)',
                    labels={'income': 'Monthly Income ($)', 'loan_amount': 'Requested Loan ($)'}
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

                # Show table of logs
                st.markdown("#### 📜 Raw Prediction Logs (Newest First)")
                # Formatting and cleaning columns for user facing tables
                df_display = df.rename(columns={
                    "id": "Log ID",
                    "age": "Age",
                    "dependents": "Dependents",
                    "income": "Income ($)",
                    "loan_amount": "Loan Amount ($)",
                    "cibil_score": "CIBIL Score",
                    "tenure": "Tenure (Mo)",
                    "gender": "Gender",
                    "married": "Married",
                    "education": "Education",
                    "self_employed": "Self Employed",
                    "previous_loan_taken": "Prev Loan Taken",
                    "property_area": "Property Area",
                    "customer_bandwidth": "Customer Bandwidth",
                    "prediction_result": "Verdict",
                    "created_at": "Timestamp"
                })
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("ℹ️ Connected to Database, but no prediction history records exist yet. Submit some predictions on the first tab!")
        else:
            st.error("Failed to load records from database backend.")
    except Exception as e:
        st.warning(f"Unable to load prediction history analytics. Establish backend connection. Details: {e}")
