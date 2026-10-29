"""Mantenimiento explícito: migraciones, seed y reindexación."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

def migrate(adopt_existing=False):
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect
    from app.database import engine
    config = Config(str(ROOT / "backend/alembic.ini"))
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if tables and "alembic_version" not in tables:
        if not adopt_existing:
            raise RuntimeError("Base sin historial Alembic: usar --adopt-existing para validar y adoptar el esquema histórico")
        required = {"users": {"id", "email", "password_hash", "role"},
                    "categories": {"id", "name", "area", "active"},
                    "reports": {"id", "image_path", "address", "category_id", "user_id"},
                    "model_versions": {"id", "name", "version"},
                    "ai_predictions": {"id", "report_id", "model_version_id", "confidence"},
                    "feedback": {"id", "prediction_id", "correct", "correct_class", "reviewed_by"}}
        for table, columns in required.items():
            if table not in tables or not columns.issubset({c["name"] for c in inspector.get_columns(table)}):
                raise RuntimeError(f"Esquema histórico incompleto en {table}; no se adoptó la base")
        command.stamp(config, "c5a83b8d4563")
    command.upgrade(config, "head")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("migrate", "seed", "reindex"))
    parser.add_argument("--adopt-existing", action="store_true")
    parser.add_argument("--demo-users", action="store_true")
    args = parser.parse_args()
    if args.command == "migrate":
        return migrate(args.adopt_existing)
    from app.database import SessionLocal
    from app.infrastructure.unit_of_work import UnitOfWork
    from app.repositories.categories import CategoryRepository
    from app.repositories.users import UserRepository
    from app.repositories.predictions import PredictionRepository
    from app.repositories.reports import ReportRepository
    from app.services.maintenance import BootstrapService, ReindexService
    with SessionLocal() as session:
        if args.command == "seed":
            BootstrapService(CategoryRepository(session), UserRepository(session),
                PredictionRepository(session), UnitOfWork(session)).seed(args.demo_users)
        else:
            from app.dependencies import get_predictor, get_storage
            print(ReindexService(ReportRepository(session), get_predictor(), get_storage(), UnitOfWork(session)).run())

if __name__ == "__main__":
    main()
