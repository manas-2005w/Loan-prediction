import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database")

# Database URL construction
# Order of preference: 
# 1. MYSQL_PUBLIC_URL env var
# 2. DATABASE_URL env var
# 3. MYSQL_URL env var
# 4. Reconstructed MySQL URL from DB_HOST, DB_USER, etc.
# 5. Fallback to local SQLite DB

DATABASE_URL = os.getenv("MYSQL_PUBLIC_URL") or os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")

if DATABASE_URL:
    # Automatically rewrite mysql:// to mysql+pymysql:// for SQLAlchemy compatibility
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
else:
    db_host = os.getenv("MYSQLHOST", os.getenv("DB_HOST", "localhost"))
    db_user = os.getenv("MYSQLUSER", os.getenv("DB_USER", "root"))
    db_password = os.getenv("MYSQLPASSWORD", os.getenv("DB_PASSWORD", "password"))
    db_name = os.getenv("MYSQLDATABASE", os.getenv("DB_NAME", "railway"))
    db_port = os.getenv("MYSQLPORT", os.getenv("DB_PORT", "3306"))
    
    # We will use pymysql as our driver for MySQL
    DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

Base = declarative_base()

class PredictionRecord(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer, nullable=False)
    dependents = Column(Integer, nullable=False)
    income = Column(Integer, nullable=False)
    loan_amount = Column(Integer, nullable=False)
    cibil_score = Column(Integer, nullable=False)
    tenure = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    married = Column(String(20), nullable=False)
    education = Column(String(20), nullable=False)
    self_employed = Column(String(20), nullable=False)
    previous_loan_taken = Column(String(20), nullable=False)
    property_area = Column(String(50), nullable=False)
    customer_bandwidth = Column(String(50), nullable=False)
    prediction_result = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Engine and Session initialization
engine = None
SessionLocal = None
is_sqlite_fallback = False

def init_db():
    global engine, SessionLocal, is_sqlite_fallback
    try:
        logger.info(f"Attempting to connect to database at: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
        # Try connecting with a small timeout so we don't hang indefinitely on startup if DB is down
        engine = create_engine(
            DATABASE_URL, 
            pool_pre_ping=True, 
            connect_args={"connect_timeout": 5} if "mysql" in DATABASE_URL else {}
        )
        # Test connection
        with engine.connect() as conn:
            pass
        logger.info("Successfully connected to MySQL database.")
    except Exception as e:
        logger.warning(f"Failed to connect to MySQL database: {e}. Falling back to SQLite.")
        sqlite_path = "sqlite:////tmp/loan_predictions_fallback.db"
        engine = create_engine(sqlite_path, connect_args={"check_same_thread": False})
        is_sqlite_fallback = True
        logger.info(f"SQLite fallback engine created at {sqlite_path}.")
        
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

def get_db():
    if SessionLocal is None:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
