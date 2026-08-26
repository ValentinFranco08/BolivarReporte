from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuramos el puerto en 5433 porque el 5432 estaba ocupado en el host
SQLALCHEMY_DATABASE_URL = "postgresql://bolivar_user:bolivar_password@localhost:5433/bolivar_responde"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
