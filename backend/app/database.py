import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BACKEND_DIR, "bolivar_dev.db")
DEFAULT_PG_URL = "postgresql://bolivar_user:bolivar_password@localhost:5433/bolivar_responde"
DEFAULT_SQLITE_URL = f"sqlite:///{DB_PATH}"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_PG_URL)


def create_resilient_engine():
    global SQLALCHEMY_DATABASE_URL
    url = SQLALCHEMY_DATABASE_URL
    
    if url.startswith("postgresql"):
        try:
            # Intento de conexión con timeout corto de 1 segundo
            test_engine = create_engine(url, connect_args={"connect_timeout": 1})
            with test_engine.connect():
                pass
            print(f"🐘 Conectado exitosamente a PostgreSQL (puerto 5433).")
            return test_engine
        except Exception as e:
            print(f"⚠️  PostgreSQL en puerto 5433 no disponible ({type(e).__name__}).")
            print(f"📦 Usando SQLite local automáticamente ({DEFAULT_SQLITE_URL}) para continuar sin errores.")
            SQLALCHEMY_DATABASE_URL = DEFAULT_SQLITE_URL
            return create_engine(DEFAULT_SQLITE_URL, connect_args={"check_same_thread": False})
            
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


engine = create_resilient_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
