#!/usr/bin/env bash

# Colores para la terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}==============================================${NC}"
echo -e "${CYAN}       🚀 REPORTE BOLÍVAR — DEV SERVER        ${NC}"
echo -e "${BLUE}==============================================${NC}"

# Detectar entorno virtual de Python
if [ -f "$ROOT_DIR/venv/bin/uvicorn" ]; then
    UVICORN_BIN="$ROOT_DIR/venv/bin/uvicorn"
elif command -v uvicorn &> /dev/null; then
    UVICORN_BIN="uvicorn"
else
    echo -e "${YELLOW}⚠️  No se encontró uvicorn en ./venv ni en el PATH del sistema.${NC}"
    exit 1
fi

# Iniciar contenedor de base de datos si Docker está instalado y activo
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo -e "${GREEN}🐘 Verificando PostgreSQL (Docker compose)...${NC}"
    (cd "$ROOT_DIR" && docker compose up -d db 2>/dev/null || true)
    if [ -f "$ROOT_DIR/backend/scripts/sync_db.py" ]; then
        (cd "$ROOT_DIR" && "$ROOT_DIR/venv/bin/python" backend/scripts/sync_db.py 2>/dev/null || true)
    fi
fi

# Manejo de apagado limpio con Ctrl + C
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Apagando servidores Backend y Frontend...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null
    fi
    wait 2>/dev/null
    echo -e "${GREEN}✅ Servidores detenidos correctamente.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

BACKEND_PORT="${PORT:-8001}"

# 1. Iniciar Backend (FastAPI en http://localhost:8001)
echo -e "${GREEN}⚡ Iniciando Backend en http://localhost:${BACKEND_PORT} ...${NC}"
(cd "$ROOT_DIR/backend" && PYTHONPATH=. "$UVICORN_BIN" app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT") &
BACKEND_PID=$!

# 2. Iniciar Frontend (Next.js en http://localhost:3000)
echo -e "${GREEN}🌐 Iniciando Frontend en http://localhost:3000 ...${NC}"
(cd "$ROOT_DIR/frontend" && npm run dev) &
FRONTEND_PID=$!

echo -e "${BLUE}----------------------------------------------${NC}"
echo -e "${GREEN}✨ Ambos servidores están corriendo en simultáneo:${NC}"
echo -e "   • Frontend:          ${CYAN}http://localhost:3000${NC}"
echo -e "   • Backend API:       ${CYAN}http://localhost:${BACKEND_PORT}${NC}"
echo -e "   • Swagger Docs:      ${CYAN}http://localhost:${BACKEND_PORT}/docs${NC}"
echo -e "${BLUE}----------------------------------------------${NC}"
echo -e "Presioná ${YELLOW}Ctrl + C${NC} en esta terminal para detener ambos."
echo ""

# Esperar a los procesos
wait "$BACKEND_PID" "$FRONTEND_PID"
