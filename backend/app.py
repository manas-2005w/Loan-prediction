import os
import pickle
import logging
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List

from database import get_db, init_db, PredictionRecord, is_sqlite_fallback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Initialize DB on start
init_db()

# Load ML Model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "build.pkl")
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info("Machine learning model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading model from {MODEL_PATH}: {e}")
    # Initialize a dummy model if file is missing (to prevent crash, but log error)
    model = None

# Initialize FastAPI
app = FastAPI(
    title="Loan Prediction API",
    description="FastAPI service for loan approval classification with database history tracking",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request validation schemas
class LoanPredictionInput(BaseModel):
    Age: int = Field(..., ge=18, le=100, example=43)
    Dependents: int = Field(..., ge=0, le=20, example=3)
    ApplicantIncome: int = Field(..., ge=0, example=54005)
    LoanAmount: int = Field(..., ge=0, example=334113)
    Cibil_Score: int = Field(..., ge=300, le=900, example=668)
    Tenure: int = Field(..., ge=1, le=360, example=43)
    Gender: int = Field(..., ge=0, le=1, description="1: Male, 0: Female", example=1)
    Married: int = Field(..., ge=0, le=1, description="1: Yes, 0: No", example=0)
    Education: int = Field(..., ge=0, le=1, description="1: Yes, 0: No", example=1)
    Self_Employed: int = Field(..., ge=0, le=1, description="1: Yes, 0: No", example=0)
    Previous_Loan_Taken: int = Field(..., ge=0, le=1, description="1: Yes, 0: No", example=1)
    Property_Area: int = Field(..., ge=0, le=2, description="0: Rural, 1: Semiurban, 2: Urban", example=2)
    Customer_Bandwith: int = Field(..., ge=0, le=2, description="0: Bad, 1: Good, 2: Medium", example=1)

class PredictionResponse(BaseModel):
    prediction: int
    prediction_text: str
    db_saved: bool

class HistoryResponse(BaseModel):
    id: int
    age: int
    dependents: int
    income: int
    loan_amount: int
    cibil_score: int
    tenure: int
    gender: str
    married: str
    education: str
    self_employed: str
    previous_loan_taken: str
    property_area: str
    customer_bandwidth: str
    prediction_result: str
    created_at: str

    class Config:
        from_attributes = True

# Helper mappings for human-readable DB fields
GENDER_MAP = {1: "Male", 0: "Female"}
MARRIED_MAP = {1: "Yes", 0: "No"}
EDUCATION_MAP = {1: "Yes", 0: "No"}
EMPLOYED_MAP = {1: "Yes", 0: "No"}
PREV_LOAN_MAP = {1: "Yes", 0: "No"}
PROPERTY_MAP = {0: "Rural", 1: "Semiurban", 2: "Urban"}
BANDWIDTH_MAP = {0: "Bad", 1: "Good", 2: "Medium"}

@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
def predict_loan(payload: LoanPredictionInput, db: Session = Depends(get_db)):
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML Model not available."
        )
    
    # 1. Prepare features as DataFrame in the precise sequence of training variables
    # This prevents the 'X does not have valid feature names' warning from sklearn
    features_df = pd.DataFrame([{
        'Age': payload.Age,
        'Dependents': payload.Dependents,
        'ApplicantIncome': payload.ApplicantIncome,
        'LoanAmount': payload.LoanAmount,
        'Cibil_Score': payload.Cibil_Score,
        'Tenure': payload.Tenure,
        'Gender': payload.Gender,
        'Married': payload.Married,
        'Education': payload.Education,
        'Self_Employed': payload.Self_Employed,
        'Previous_Loan_Taken': payload.Previous_Loan_Taken,
        'Property_Area': payload.Property_Area,
        'Customer_Bandwith': payload.Customer_Bandwith
    }])

    # 2. Run model prediction
    try:
        prediction_val = int(model.predict(features_df)[0])
        prediction_text = "Loan is Approved" if prediction_val != 0 else "Loan is Rejected"
    except Exception as e:
        logger.error(f"Inference prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing prediction model: {str(e)}"
        )

    # 3. Log results to database
    db_saved = False
    try:
        record = PredictionRecord(
            age=payload.Age,
            dependents=payload.Dependents,
            income=payload.ApplicantIncome,
            loan_amount=payload.LoanAmount,
            cibil_score=payload.Cibil_Score,
            tenure=payload.Tenure,
            gender=GENDER_MAP.get(payload.Gender, "Unknown"),
            married=MARRIED_MAP.get(payload.Married, "Unknown"),
            education=EDUCATION_MAP.get(payload.Education, "Unknown"),
            self_employed=EMPLOYED_MAP.get(payload.Self_Employed, "Unknown"),
            previous_loan_taken=PREV_LOAN_MAP.get(payload.Previous_Loan_Taken, "Unknown"),
            property_area=PROPERTY_MAP.get(payload.Property_Area, "Unknown"),
            customer_bandwidth=BANDWIDTH_MAP.get(payload.Customer_Bandwith, "Unknown"),
            prediction_result=prediction_text
        )
        db.add(record)
        db.commit()
        db_saved = True
        logger.info(f"Prediction log saved successfully (ID: {record.id}).")
    except Exception as e:
        logger.error(f"Failed to log prediction to DB: {e}")
        # Note: Do not crash/raise error, return inference result anyway
        db.rollback()

    return {
        "prediction": prediction_val,
        "prediction_text": prediction_text,
        "db_saved": db_saved
    }

@app.get("/predictions", response_model=List[HistoryResponse])
def get_prediction_history(limit: int = 50, db: Session = Depends(get_db)):
    try:
        records = db.query(PredictionRecord).order_by(PredictionRecord.id.desc()).limit(limit).all()
        # Convert records to include serialized datetime
        response = []
        for r in records:
            response.append({
                "id": r.id,
                "age": r.age,
                "dependents": r.dependents,
                "income": r.income,
                "loan_amount": r.loan_amount,
                "cibil_score": r.cibil_score,
                "tenure": r.tenure,
                "gender": r.gender,
                "married": r.married,
                "education": r.education,
                "self_employed": r.self_employed,
                "previous_loan_taken": r.previous_loan_taken,
                "property_area": r.property_area,
                "customer_bandwidth": r.customer_bandwidth,
                "prediction_result": r.prediction_result,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
            })
        return response
    except Exception as e:
        logger.error(f"Failed to fetch history from DB: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history logs."
        )

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "database_type": "sqlite_fallback" if is_sqlite_fallback else "mysql"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
