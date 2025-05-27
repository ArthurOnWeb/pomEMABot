# database/connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de connexion : un fichier sqlite local
SQLALCHEMY_DATABASE_URL = "sqlite:///./ema_bot.db"

# L’engine SQLAlchemy, désactive le check_same_thread pour multi-threads
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()
