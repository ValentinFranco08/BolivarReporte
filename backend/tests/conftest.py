import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.dependencies import get_storage
from app.infrastructure.storage import LocalFileStorage

# Base de datos en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    # SQLite necesita BEGIN explícito para que los SAVEPOINT participen del rollback exterior.
    connection.exec_driver_sql("BEGIN")
    session = TestingSessionLocal(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture()
def client(db, tmp_path):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage] = lambda: LocalFileStorage(tmp_path)
    yield TestClient(app)
    del app.dependency_overrides[get_db]
    app.dependency_overrides.pop(get_storage, None)
