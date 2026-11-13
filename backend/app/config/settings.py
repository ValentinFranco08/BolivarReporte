import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

BACKEND_DIR = Path(__file__).resolve().parents[2]


def get_pet_reid_checkpoint() -> str | None:
    configured = os.getenv("PET_REID_CHECKPOINT")
    if configured is not None:
        return configured or None
    local = dotenv_values(BACKEND_DIR / ".env", interpolate=False).get("PET_REID_CHECKPOINT")
    return str(BACKEND_DIR.parent / local) if local else None


@dataclass(frozen=True)
class Settings:
    pet_reid_checkpoint: str | None = get_pet_reid_checkpoint()
    legacy_pet_visual_threshold: float = float(os.getenv("LEGACY_PET_VISUAL_THRESHOLD", "0.35"))
    uploads_dir: Path = BACKEND_DIR / "uploads"
    cors_origins: tuple[str, ...] = tuple(
        value.strip() for value in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",") if value.strip()
    )

settings = Settings()
