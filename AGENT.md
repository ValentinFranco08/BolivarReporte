# Guía de Contexto para Agentes de IA — Bolívar Responde

Este documento describe el rol, arquitectura, convenciones y comandos esenciales para cualquier Agente de IA que interactúe o continúe el desarrollo de este repositorio.

---

## 🎯 Misión del Proyecto
**Bolívar Responde** es una plataforma ciudadana integral para San Carlos de Bolívar que utiliza Inteligencia Artificial Multimodal (Vision Transformer + RoBERTa en Español con Cross-Attention) para clasificar y priorizar reportes urbanos, de bienestar animal y de tránsito/estacionamiento en una taxonomía objetivo de 23 etiquetas hoja.

---

## 📂 Mapa de la Arquitectura

```text
proyecto redes neuronales/
├── ml/                       # Módulo de Machine Learning (PyTorch)
│   ├── datasets/             # Pipelines de datos (build_dataset.py, multimodal_dataset.py)
│   ├── models/               # Encoders (ViT, RoBERTa), CrossAttentionFusion y MultimodalClassifier
│   ├── training/             # Scripts de entrenamiento (train_vit.py, train_roberta.py, train_multimodal.py)
│   ├── evaluation/           # Evaluación y matriz de confusión (compare_results.py)
│   ├── inference/            # Módulo de inferencia en producción (predict.py)
│   └── checkpoints/          # Pesos entrenados (multimodal/best_fase3.pt)
│
├── backend/                  # API REST (FastAPI)
│   ├── app/
│   │   ├── main.py           # Endpoints de API, CORS y montaje estático de /uploads
│   │   ├── database.py       # Engine SQLAlchemy y sesión DB
│   │   ├── models.py         # 6 Modelos ORM (User, Category, Report, AIPrediction, ModelVersion, Feedback)
│   │   ├── schemas.py        # Esquemas Pydantic v2 de entrada y salida
│   │   ├── crud.py           # Consultas y mutaciones a la base de datos
│   │   ├── auth.py           # Autenticación JWT y hashing de contraseñas
│   │   └── ai_service.py     # Wrapper singleton para inferencia con el modelo PyTorch
│   ├── scripts/              # Utilidades (seed.py, update_coords.py, export_dataset.py)
│   ├── alembic/              # Control de versiones de la base de datos
│   └── requirements.txt      # Dependencias backend
│
├── frontend/                 # Aplicación Web (Next.js 16 App Router)
│   ├── app/
│   │   ├── page.tsx          # Landing page principal
│   │   ├── login/ & registro/ # Autenticación ciudadana / administrativa
│   │   ├── reportes/nuevo/   # Formulario con GPS, análisis multimodal y corrección
│   │   ├── reportes/         # Listado público de incidencias
│   │   ├── mapa/             # Mapa interactivo (Leaflet & OpenStreetMap)
│   │   └── dashboard/        # Panel de administración, filtros y panel de Feedback IA
│   └── components/ui/        # Componentes UI (AIResultCard, ImageUploader, Map, etc.)
│
├── docker-compose.yml        # PostgreSQL en puerto 5433
├── AGENT.md                  # Este archivo (Instrucciones para Agentes)
├── memoria.md                # Estado actual, métricas y decisiones técnicas
├── README.md                 # Documentación general del proyecto
└── PLAN_IMPLEMENTACION_TRANSITO.md # Estado y plan de cierre de Tránsito y Estacionamiento
```

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
   - `ml/taxonomy.py` es la fuente de verdad de las 23 etiquetas, áreas, jerarquía y prioridad.
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
- **Ciclo de Reentrenamiento:** Las correcciones exportadas alimentan directamente el script `ml/training/train_multimodal.py` para fine-tuning.

## 🚦 Módulo Tránsito y Estacionamiento

- La interfaz permite corregir manualmente las nueve etiquetas nuevas y muestra `classification` de la API (jerarquía, prioridad y revisión requerida).
- El checkpoint disponible sigue siendo de 14 clases. No afirmar soporte de inferencia para tránsito hasta reunir ~100 imágenes por hoja, regenerar `dataset.json` y reentrenar el head de 23 clases.
- Consultar `PLAN_IMPLEMENTACION_TRANSITO.md` antes de modificar dataset, entrenamiento o UI del módulo.
