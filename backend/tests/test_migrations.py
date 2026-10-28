import os
from pathlib import Path
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

def run_manage(database, *arguments):
    result = subprocess.run([sys.executable, str(ROOT / "backend/scripts/manage.py"), *arguments],
        cwd=ROOT, env={**os.environ, "DATABASE_URL": f"sqlite:///{database}"},
        capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_migrate_and_seed_empty_database_are_repeatable(tmp_path):
    database = tmp_path / "fresh.db"
    run_manage(database, "migrate")
    run_manage(database, "seed", "--demo-users")
    run_manage(database, "migrate")
    run_manage(database, "seed", "--demo-users")
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM model_versions").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 6
        assert connection.execute("SELECT COUNT(*) FROM remum_records").fetchone()[0] == 0


def test_adopting_legacy_schema_preserves_data(tmp_path):
    from sqlalchemy import create_engine
    from app.database import Base
    database = tmp_path / "legacy.db"
    engine = create_engine(f"sqlite:///{database}")
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql("INSERT INTO users (name,email,password_hash,role) VALUES ('Tutor','legacy@test.com','hash','CITIZEN')")
    engine.dispose()
    run_manage(database, "migrate", "--adopt-existing")
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT email FROM users").fetchone()[0] == "legacy@test.com"
        assert connection.execute("SELECT version_num FROM alembic_version").fetchone()[0] == "d6e9f03a2710"
