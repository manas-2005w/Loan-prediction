FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker layer cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and models
COPY main.py .
COPY database.py .
COPY build.pkl .

# Expose port (7860 for Hugging Face Spaces / default environments)
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
