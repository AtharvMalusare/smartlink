from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

raw_url = os.getenv("DATABASE_URL")

if not raw_url or raw_url.strip() == "" or raw_url == "${{Postgres.DATABASE_URL}}":
    print("WARNING: Railway did not provide a DATABASE_URL. Falling back to local URL.")
    raw_url = "sqlite:///./fallback.db"

DATABASE_URL = raw_url

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if "rlwy.net" in DATABASE_URL:
    connect_args = {"sslmode": "require"}
elif DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    **( 
        {"pool_pre_ping": True, "pool_recycle": 300, "pool_size": 5, "max_overflow": 10} 
        if not DATABASE_URL.startswith("sqlite") else {} 
    )
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()