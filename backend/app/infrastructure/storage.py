from pathlib import Path
from typing import Protocol
from uuid import uuid4

class FileStorage(Protocol):
    def save(self, data: bytes, filename: str = "image.jpg") -> str: ...
    def read(self, public_path: str) -> bytes: ...
    def delete(self, public_path: str) -> None: ...

class LocalFileStorage:
    """Encapsula el acceso al directorio de imágenes públicas."""
    def __init__(self, directory: Path):
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, filename: str = "image.jpg") -> str:
        suffix = Path(filename).suffix.lower() or ".jpg"
        name = f"{uuid4()}{suffix}"
        (self._directory / name).write_bytes(data)
        return f"/uploads/{name}"

    def read(self, public_path: str) -> bytes:
        return (self._directory / Path(public_path).name).read_bytes()

    def delete(self, public_path: str) -> None:
        (self._directory / Path(public_path).name).unlink(missing_ok=True)
