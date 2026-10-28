"""Operaciones explícitas de datos, fuera del arranque HTTP."""
import json
from .. import models
from ml.taxonomy import SEED_CATEGORIES

class BootstrapService:
    def __init__(self, categories, users, predictions, passwords, unit_of_work):
        self.categories = categories
        self.users = users
        self.predictions = predictions
        self.passwords = passwords
        self.unit_of_work = unit_of_work

    def seed(self, demo_users=False):
        with self.unit_of_work:
            for data in SEED_CATEGORIES:
                if self.categories.by_name(data["name"]) is None:
                    self.categories.add(models.Category(**data, active=True, is_verified=True, sample_count=1))
            if self.predictions.model_version() is None:
                self.predictions.add_version(models.ModelVersion(name="multimodal-v1", version="1.0",
                    architecture="ViT + RoBERTa + Cross-Attention"))
            if demo_users:
                for name, email, password, role in (
                    ("Administrador Municipal", "admin@bolivar.gob.ar", "admin123", models.UserRole.ADMIN),
                    ("Vecino Bolívar", "vecino@bolivar.gob.ar", "vecino123", models.UserRole.CITIZEN),
                ):
                    if self.users.by_email(email) is None:
                        self.users.add(models.User(name=name, email=email, role=role,
                            password_hash=self.passwords.get_password_hash(password)))

class ReindexService:
    def __init__(self, reports, predictor, storage, unit_of_work):
        self.reports = reports
        self.predictor = predictor
        self.storage = storage
        self.unit_of_work = unit_of_work

    def run(self):
        updated = 0
        with self.unit_of_work:
            for report in self.reports.with_images():
                try:
                    vector = json.loads(report.embedding or "null")
                except ValueError:
                    vector = None
                if isinstance(vector, list) and len(vector) == 768:
                    continue
                try:
                    image = self.storage.read(report.image_path)
                except FileNotFoundError:
                    continue
                report.embedding = json.dumps(self.predictor.extract_pet_embedding(image))
                updated += 1
        return updated
