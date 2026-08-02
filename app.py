import os
import pickle
import numpy as np
import pymysql
from flask import Flask, request, render_template, jsonify
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__, template_folder="template", static_folder="staticfiles")

import sqlite3

MODEL_PATH = os.path.join(os.path.dirname(__file__), "build.pkl")
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "loan_predictions_local.db")

def get_mysql_connection():
    db_url = os.getenv("MYSQL_PUBLIC_URL") or os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL")
    
    host = os.getenv("MYSQLHOST", "mysql.railway.internal")
    port = int(os.getenv("MYSQLPORT", "3306"))
    user = os.getenv("MYSQLUSER", "root")
    password = os.getenv("MYSQLPASSWORD", os.getenv("MYSQL_ROOT_PASSWORD", ""))
    database = os.getenv("MYSQLDATABASE", os.getenv("MYSQL_DATABASE", "railway"))

    if db_url and "@" in db_url:
        if db_url.startswith("mysql+pymysql://"):
            db_url = db_url.replace("mysql+pymysql://", "mysql://", 1)
        parsed = urlparse(db_url)
        if parsed.hostname:
            host = parsed.hostname
        if parsed.port:
            port = parsed.port
        if parsed.username:
            user = parsed.username
        if parsed.password:
            password = parsed.password
        if parsed.path and parsed.path.lstrip("/"):
            database = parsed.path.lstrip("/")

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=3
    )

def get_db_driver():
    try:
        conn = get_mysql_connection()
        return conn, "mysql"
    except Exception as e:
        # Fallback to local SQLite database so data is saved & history works locally
        conn = sqlite3.connect(LOCAL_DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

def init_db():
    try:
        conn, driver = get_db_driver()
        cursor = conn.cursor()
        if driver == "mysql":
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
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            conn.commit()
        conn.close()
        print(f"Database ({driver.upper()}) initialized successfully.")
        return True
    except Exception as exc:
        print(f"Database init failed: {exc}")
        return False

# Attempt initial DB setup
DB_READY = init_db()

try:
    with open(MODEL_PATH, "rb") as handle:
        model = pickle.load(handle)
except Exception as exc:
    print(f"Model load failed: {exc}")
    model = None

def save_prediction(payload, prediction_text):
    try:
        conn, driver = get_db_driver()
        cursor = conn.cursor()
        placeholder = "%s" if driver == "mysql" else "?"
        
        # Ensure table exists
        if driver == "mysql":
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
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

        query = f"""
            INSERT INTO predictions (
                age, dependents, income, loan_amount, cibil_score, tenure,
                gender, married, education, self_employed, previous_loan_taken,
                property_area, customer_bandwidth, prediction_result
            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """
        params = (
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
        )
        cursor.execute(query, params)
        if driver == "sqlite":
            conn.commit()
        conn.close()
        return True
    except Exception as exc:
        print(f"Database save failed: {exc}")
        return False

def get_prediction_history(limit=50):
    try:
        conn, driver = get_db_driver()
        cursor = conn.cursor()
        if driver == "mysql":
            cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT %s", (limit,))
            rows = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,))
            raw_rows = cursor.fetchall()
            rows = [dict(r) for r in raw_rows]
        conn.close()

        for row in rows:
            if "created_at" in row and row["created_at"]:
                row["created_at"] = str(row["created_at"])
        return rows
    except Exception as exc:
        print(f"Database history fetch failed: {exc}")
        return []

@app.route("/", methods=["GET"])
def home():
    show_history = request.args.get("show_history") == "1"
    history_entries = get_prediction_history() if show_history else []
    is_live = init_db()
    return render_template(
        "index.html",
        prediction_text=None,
        show_history=show_history,
        history_entries=history_entries,
        db_ready=is_live,
    )

@app.route("/api/history", methods=["GET"])
def api_history():
    history_entries = get_prediction_history()
    return jsonify({
        "success": True,
        "count": len(history_entries),
        "data": history_entries
    })

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
    is_live = init_db()

    return render_template(
        "index.html",
        prediction_text=prediction_text,
        db_saved=db_saved,
        show_history=show_history,
        history_entries=history_entries,
        db_ready=is_live,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5002")))