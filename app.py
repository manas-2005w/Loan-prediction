import os
import pickle
import numpy as np
import pymysql
from flask import Flask, request, render_template
from urllib.parse import urlparse

app = Flask(__name__, template_folder="template", static_folder="staticfiles")

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "loan_predictions")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

MODEL_PATH = os.path.join(os.path.dirname(__file__), "build.pkl")


def get_db_connection():
    if DATABASE_URL:
        parsed = urlparse(DATABASE_URL)
        host = parsed.hostname or DB_HOST
        port = parsed.port or DB_PORT
        user = parsed.username or DB_USER
        password = parsed.password or DB_PASSWORD
        database = parsed.path.lstrip("/") or DB_NAME
        return pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )

    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )


def init_db():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    age INT NOT NULL,
                    dependents INT NOT NULL,
                    income INT NOT NULL,
                    loan_amount INT NOT NULL,
                    cibil_score INT NOT NULL,
                    tenure INT NOT NULL,
                    gender VARCHAR(20) NOT NULL,
                    married VARCHAR(20) NOT NULL,
                    education VARCHAR(20) NOT NULL,
                    self_employed VARCHAR(20) NOT NULL,
                    previous_loan_taken VARCHAR(20) NOT NULL,
                    property_area VARCHAR(50) NOT NULL,
                    customer_bandwidth VARCHAR(50) NOT NULL,
                    prediction_result VARCHAR(30) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        conn.close()
        return True
    except Exception as exc:
        print(f"MySQL init failed: {exc}")
        return False


DB_READY = init_db()

try:
    with open(MODEL_PATH, "rb") as handle:
        model = pickle.load(handle)
except Exception as exc:
    print(f"Model load failed: {exc}")
    model = None


def save_prediction(payload, prediction_text):
    if not DB_READY:
        return False

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO predictions (
                    age, dependents, income, loan_amount, cibil_score, tenure,
                    gender, married, education, self_employed, previous_loan_taken,
                    property_area, customer_bandwidth, prediction_result
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload["Age"],
                    payload["Dependents"],
                    payload["ApplicantIncome"],
                    payload["LoanAmount"],
                    payload["Cibil_Score"],
                    payload["Tenure"],
                    payload["Gender"],
                    payload["Married"],
                    payload["Education"],
                    payload["Self_Employed"],
                    payload["Previous_Loan_Taken"],
                    payload["Property_Area"],
                    payload["Customer_Bandwith"],
                    prediction_text,
                ),
            )
        conn.close()
        return True
    except Exception as exc:
        print(f"MySQL save failed: {exc}")
        return False


def get_prediction_history(limit=10):
    if not DB_READY:
        return []

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM predictions ORDER BY id DESC LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as exc:
        print(f"MySQL history fetch failed: {exc}")
        return []


@app.route("/", methods=["GET"])
def home():
    show_history = request.args.get("show_history") == "1"
    history_entries = get_prediction_history() if show_history else []
    return render_template(
        "index.html",
        prediction_text=None,
        show_history=show_history,
        history_entries=history_entries,
        db_ready=DB_READY,
    )


@app.route("/predict", methods=["POST"])
def predict():
    show_history = request.form.get("show_history") == "1"

    payload = {
        "Age": int(request.form.get("Age", 0)),
        "Dependents": int(request.form.get("Dependents", 0)),
        "ApplicantIncome": int(request.form.get("ApplicantIncome", 0)),
        "LoanAmount": int(request.form.get("LoanAmount", 0)),
        "Cibil_Score": int(request.form.get("Cibil_Score", 0)),
        "Tenure": int(request.form.get("Tenure", 0)),
        "Gender": request.form.get("Gender", "1"),
        "Married": request.form.get("Married", "1"),
        "Education": request.form.get("Education", "1"),
        "Self_Employed": request.form.get("Self_Employed", "1"),
        "Previous_Loan_Taken": request.form.get("Previous_Loan_Taken", "1"),
        "Property_Area": request.form.get("Property_Area", "0"),
        "Customer_Bandwith": request.form.get("Customer_Bandwith", "1"),
    }

    feature_vector = np.array(
        [
            payload["Age"],
            payload["Dependents"],
            payload["ApplicantIncome"],
            payload["LoanAmount"],
            payload["Cibil_Score"],
            payload["Tenure"],
            int(payload["Gender"]),
            int(payload["Married"]),
            int(payload["Education"]),
            int(payload["Self_Employed"]),
            int(payload["Previous_Loan_Taken"]),
            int(payload["Property_Area"]),
            int(payload["Customer_Bandwith"]),
        ]
    ).reshape(1, -1)

    if model is None:
        prediction_text = "Unable to load model"
        prediction_value = 0
    else:
        prediction_value = int(model.predict(feature_vector)[0])
        prediction_text = "Loan is Approved" if prediction_value != 0 else "Loan is Rejected"

    db_saved = save_prediction(payload, prediction_text)
    history_entries = get_prediction_history() if show_history else []

    return render_template(
        "index.html",
        prediction_text=prediction_text,
        db_saved=db_saved,
        show_history=show_history,
        history_entries=history_entries,
        db_ready=DB_READY,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)