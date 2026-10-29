# Guía de Contexto para Agentes de IA — Bolívar Responde

Este documento describe el rol, arquitectura, convenciones y comandos esenciales para cualquier Agente de IA que interactúe o continúe el desarrollo de este repositorio.

---

## 🎯 Misión del Proyecto
**Bolívar Responde** es una plataforma ciudadana integral para San Carlos de Bolívar que utiliza Inteligencia Artificial Multimodal (Vision Transformer + RoBERTa en Español con Cross-Attention) para clasificar y priorizar reportes urbanos, de bienestar animal y de tránsito/estacionamiento con una taxonomía activa de 6 clases animales. Los planes históricos de 23 etiquetas no describen el modelo actual.

---

## 📂 Mapa de la Arquitectura

Consultar `docs/ARQUITECTURA.md` para diagramas UML y comandos.

```text
backend/app/
├── main.py             # Configuración HTTP y ciclo de vida
├── controllers/        # APIRouter: transporte HTTP
├── services/           # Casos de uso y políticas de negocio
├── repositories/       # Consultas e inserciones; flush, sin commit
├── infrastructure/     # FileStorage, LazyPredictor y UnitOfWork
├── core/               # Configuración y errores
├── dependencies.py     # Composición de objetos
├── models.py           # Entidades SQLAlchemy
├── schemas.py          # Contratos Pydantic
└── auth.py             # Dependencias HTTP de autenticación
ml/
├── models/             # Encoders, fusión, clasificador y baselines
├── data/               # Dataset, validación y preparación
├── preprocessing/      # Imagen y texto compartidos
├── training/           # train.py, trainer.py e incremental.py
├── evaluation/         # Evaluator y métricas
├── inference/          # Predictor, checkpoints y sugerencias
├── configs/            # Experimentos JSON
└── cli.py              # Comandos de ML
frontend/               # Vista Next.js
backend/scripts/        # Mantenimiento explícito y puente de feedback
```

Las fachadas históricas `crud.py`, `ai_service.py` y `llm_categorizer.py` fueron retiradas tras migrar sus consumidores. Usar servicios, repositorios o `ml.inference.category_suggester` directamente. `dependencies.get_predictor()` y `get_storage()` son los proveedores compartidos. Las funciones de contraseñas y JWT están en `infrastructure/security.py`; `auth.py` contiene las dependencias HTTP.

Los servicios coordinan transacciones con `UnitOfWork`. Los controladores no consultan la base ni ejecutan lógica neuronal. ML no debe importar FastAPI, SQLAlchemy ni módulos del backend. Los tres modelos comparten una interfaz de entradas por nombre y se entrenan directamente con `Trainer`, sin adaptadores ni fábricas adicionales.

Las migraciones y datos iniciales se ejecutan con `backend/scripts/manage.py migrate` y `seed`. No reintroducir creación de tablas, usuarios o reindexación en el startup HTTP. `dev.sh` ya ejecuta mantenimiento explícito y no sincroniza/trunca bases.

---

## ⚡ Reglas del Entorno & Convenciones Críticas

1. **Entorno Virtual Python:**  
   Siempre activar el entorno virtual desde la raíz:
   ```bash
   source venv/bin/activate
   ```
2. **Base de Datos PostgreSQL:**  
   - Corre en Docker en el puerto **`5433`** (para evitar conflictos con puertos 5432 del host).
   - URI de conexión: `postgresql://postgres:postgres@localhost:5433/bolivar_responde`
   - Migraciones: siempre usar Alembic (`alembic revision --autogenerate -m "..." && alembic upgrade head`).
3. **Hardware & Dispositivos de ML:**  
   - En macOS Apple Silicon, priorizar `device = "mps"`.
   - Soporta fallback automático a `cuda` o `cpu`.
4. **Dependencias de Autenticación:**  
   - Usar `bcrypt==3.2.2` con `passlib[bcrypt]` para evitar incompatibilidades de longitud de hash.
5. **Esquemas y Tipos Pydantic:**  
   - Todos los esquemas de API deben residir en `backend/app/schemas.py`.
6. **Taxonomía y legalidad:**
   - `ml/taxonomy.py` es la fuente de verdad de las 6 etiquetas activas, áreas y prioridad.
   - La IA clasifica situaciones; nunca declara una infracción legal. La aplicación debe conservar el disclaimer y enviar casos de confianza menor a `0.55` a revisión humana.

---

## 🚀 Comandos Rápidos de Ejecución

### 1. Iniciar Base de Datos
```bash
docker-compose up -d
```

### 2. Iniciar Backend (FastAPI)
```bash
source venv/bin/activate
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Iniciar Frontend (Next.js)
```bash
cd frontend
npm run dev
```

### 4. Exportar Feedback para Reentrenamiento
```bash
source venv/bin/activate
python backend/scripts/export_dataset.py --output dataset_correcciones.json
```

---

## 🧠 Flujo de Feedback (Human-in-the-Loop)
- **Ciudadano (`/reportes/nuevo`):** Si la IA sugiere una categoría errónea, el usuario puede corregirla antes de confirmar. El backend guarda la corrección en `feedback` con `correct=False`.
- **Administrador (`/dashboard`):** Puede evaluar cualquier reporte y cambiar su clasificación o prioridad en tiempo real.
- **Ciclo de Reentrenamiento:** Las correcciones exportadas se consumen con `python -m ml.cli incremental --feedback archivo.json`; `backend/scripts/retrain.py` coordina el marcado de feedback procesado.

## 🚦 Módulo Tránsito y Estacionamiento

- La interfaz permite corregir manualmente las nueve etiquetas nuevas y muestra `classification` de la API (jerarquía, prioridad y revisión requerida).
- La taxonomía activa contiene 6 clases animales. No afirmar soporte de inferencia para tránsito: requiere actualizar explícitamente taxonomía, dataset, cabeza y metadatos del checkpoint.
- Consultar `PLAN_IMPLEMENTACION_TRANSITO.md` antes de modificar dataset, entrenamiento o UI del módulo.
