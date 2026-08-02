# Loan Prediction Application Deployment Setup

This project is a full-stack, production-grade Machine Learning deployment system for a Loan Approval Prediction model. It has been restructured from a basic Flask app into a modern microservice architecture consisting of a FastAPI backend and a Streamlit frontend, containerized with Docker and integrated with a MySQL database.

---

## 🏗️ Architecture

```
                  User
                   |
                   v
           Streamlit Cloud (Frontend UI)
                   |
                   | (HTTP REST API Request)
                   v
             Render (FastAPI Backend)
                   |
         +---------+---------+
         |                   |
         v                   v
   ML Model (build.pkl)    Railway MySQL (predictions Table)
```

---

## 📂 Project Structure

- **`backend/`**:
  - `app.py`: FastAPI server containing `/predict`, `/predictions` (history), and `/health` endpoints.
  - `database.py`: SQLAlchemy setup with connection pooling, schemas, and a local SQLite fallback if MySQL is unreachable.
  - `build.pkl`: The trained Decision Tree Classifier.
  - `requirements.txt`: Python package requirements for backend execution.
  - `Dockerfile`: Multi-stage build runner for backend containerization.
- **`frontend/`**:
  - `app.py`: Premium Streamlit dashboard featuring intuitive slider inputs, visual indicators (like CIBIL gauges), and live database metrics and graphs.
  - `requirements.txt`: Python package requirements for Streamlit.
  - `Dockerfile`: Runner for the frontend web application.
- **`docker-compose.yml`**: Multi-container orchestrator that spins up a local MySQL instance, the FastAPI backend, and the Streamlit frontend simultaneously.

---

## 🚀 Local Run (Single Command via Docker)

You can run the database, backend, and frontend locally without installing any Python dependencies or MySQL on your host machine:

1. Make sure you have **Docker** and **Docker Compose** installed and running on your system.
2. In the root of the `Deployment` folder, execute:
   ```bash
   docker compose up --build
   ```
3. Once running:
   - **Streamlit Frontend** is available at: [http://localhost:8501](http://localhost:8501)
   - **FastAPI Documentation** is available at: [http://localhost:8080/docs](http://localhost:8080/docs)
   - **MySQL Database** is running on: `localhost:3306`

---

## 🐍 Local Run (Without Docker)

If you prefer to run services manually using your system python:

### 1. Backend Setup:
```bash
cd backend
pip install -r requirements.txt
# (Optional) Set MySQL connection environment details. If unset, it automatically falls back to a local SQLite database.
export DATABASE_URL="mysql+pymysql://root:password@localhost:3306/loan_predictions"
python3 app.py
```

### 2. Frontend Setup:
In a new terminal window:
```bash
cd frontend
pip install -r requirements.txt
export BACKEND_URL="http://localhost:8080"
streamlit run app.py
```

---

## ☁️ Cloud Deployment Process (Summary of the Steps)

### Step 1: Push Code to GitHub
Ensure the entire directory structure is committed and pushed to a GitHub repository.

### Step 2: Database Setup (Railway MySQL)
1. Log in to [Railway.app](https://railway.app/).
2. Create a new project and select **Provision MySQL**.
3. Under the database settings, copy the **Connection URL** (looks like `mysql://root:password@host:port/dbname`).
4. Keep the credentials handy; our FastAPI app will automatically create the `predictions` table structure upon first connection!

### Step 3: Backend Deployment (Render)
1. Log in to [Render](https://render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository.
4. Configure the settings:
   - **Runtime**: Select `Docker` (Render will automatically locate the `./backend/Dockerfile`).
   - Note: Since the Dockerfile is in the `backend` subdirectory, set the **Root Directory** setting to `backend/` or configure the Docker Path to `backend/Dockerfile` in Render settings.
5. Under **Environment Variables**, add:
   - `DATABASE_URL`: Set this to the connection URL from Railway (replace `mysql://` with `mysql+pymysql://` at the beginning).
6. Click **Deploy**. Render will build the container and provide you with a public API URL (e.g. `https://loan-prediction-fastapi-wzge.onrender.com`).

### Step 4: Frontend Deployment (Streamlit Cloud)
1. Log in to [Streamlit Community Cloud](https://streamlit.io/cloud).
2. Click **New App** and select your GitHub repository.
3. Configure the settings:
   - **Main file path**: `frontend/app.py`
4. Under **Advanced Settings**, add the environment variable:
   - `BACKEND_URL`: `https://your-backend-api-url.onrender.com` (use your actual Render live API url).
5. Click **Deploy**. Your Streamlit frontend will be online publicly!
