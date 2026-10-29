"""Punto de composición HTTP: configuración, ciclo de vida y controladores."""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Compatibilidad con `cd backend && uvicorn app.main:app`.
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .core.errors import ApplicationError
from .controllers import public, authentication, reports, feedback, categories, remum
from .dependencies import get_predictor, get_storage

@asynccontextmanager
async def lifespan(app):
    from starlette.concurrency import run_in_threadpool
    # Usar el mismo proveedor que las rutas, también al inyectar un predictor de prueba.
    provider = app.dependency_overrides.get(get_predictor, get_predictor)
    model = provider()
    initialize = getattr(model, "initialize", None)
    if initialize is not None:
        await run_in_threadpool(initialize)
    yield

def create_app():
    application = FastAPI(title="Reporte Bolívar — API",
        description="API para la plataforma inteligente de participación ciudadana de Bolívar.",
        version="2.0.0", lifespan=lifespan)
    application.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins),
        allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    get_storage()  # Preparar el directorio que sirve StaticFiles.
    application.mount("/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")
    for controller in (public, authentication, reports, feedback, categories, remum):
        application.include_router(controller.router)

    @application.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, error: ApplicationError):
        return JSONResponse(status_code=error.status_code, content={"detail": str(error)})

    return application

app = create_app()
