import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    uploads_dir: Path = Path(__file__).resolve().parents[2] / "uploads"
    cors_origins: tuple[str, ...] = tuple(
        value.strip() for value in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",") if value.strip()
    )

settings = Settings()
