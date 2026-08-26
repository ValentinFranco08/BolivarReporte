# Memoria del Proyecto — Reporte Bolívar

---

## 📌 Estado Actual

- **Nombre del proyecto:** Reporte Bolívar (Bolívar Responde)
- **Fase:** Sistema End-to-End operativo; módulo Tránsito y Estacionamiento integrado en taxonomía, API y UI, pendiente de datos y reentrenamiento.
- **Fecha:** 21/08/2026
- **Propósito:** Plataforma inteligente de participación ciudadana para clasificar problemáticas urbanas y animales en riesgo usando Deep Learning Multimodal.

---

## 🧠 Arquitectura de Inteligencia Artificial

- **Tipo:** Clasificador Multimodal (Visión + Lenguaje Natural)
- **Vision Encoder:** `google/vit-base-patch16-224` (Visual Tokens: 197 × 768)
- **Text Encoder:** `bertin-project/bertin-roberta-base-spanish` (Text Tokens: L × 768)
- **Fusión:** `CrossAttentionFusion` (MHA con Q=Texto, K=V=Visual)
- **Head actual en producción:** MLP 768 → 512 → 256 → 14 clases.
- **Taxonomía objetivo:** 23 etiquetas hoja; el próximo entrenamiento debe inicializar un head 256 → 23.
- **Framework:** PyTorch (aceleración por `mps` en Apple Silicon / `cuda` en GPU / `cpu`)
- **Checkpoint en producción:** `ml/checkpoints/multimodal/best_fase3.pt`

### Comparativa de Modelos Experimentales

| Modelo | Arquitectura | Test Acc | Test Macro F1 | Estado |
|---|---|---|---|:---:|
| **A — Solo ViT** | Imagen pura (224x224) | 55.2% | 0.5448 | ✅ Finalizado |
| **B — Solo RoBERTa** | Texto puro (Español) | 86.6% | 0.8533 | ✅ Finalizado |
| **C — Multimodal** | ViT + RoBERTa + Cross-Attention | **88.1%** | **0.8720** | ✅ Checkpoint en API |

---

## 📊 Dataset & Categorías

- **Volumen:** 573 instancias estructuradas (`train`: 385 | `val`: 121 | `test`: 67)
- **Dataset/checkpoint actual:** 573 instancias y 14 etiquetas; no predice aún las clases nuevas.
- **Taxonomía oficial:** 23 etiquetas en 4 áreas:
  - **Infraestructura:** `bache`, `calle_deteriorada`, `luminaria_danada`, `arbol_caido`, `perdida_agua`
  - **Higiene Urbana:** `basura`, `microbasural`
  - **Animales:** `animal_perdido`, `animal_encontrado`, `animal_suelto`, `animal_en_riesgo`, `posible_animal_herido`, `abandono`
  - **Tránsito y Estacionamiento:** `senalizacion_danada`, seis tipos de estacionamiento indebido, `vehiculo_abandonado`, `obstruccion_de_circulacion` y `semaforo_danado`.

La salida de IA incluye jerarquía (`category`, `subcategory`, `type`), prioridad operativa, confianza y `requires_review` bajo 0.55. No califica infracciones legales.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologías / Librerías |
|---|---|
| **Frontend** | Next.js 16 (App Router), TypeScript, Tailwind CSS, Leaflet + React-Leaflet (OpenStreetMap) |
| **Backend** | Python 3.14 / 3.11, FastAPI, Uvicorn, SQLAlchemy 2.0, Alembic, Passlib + Bcrypt 3.2.2, PyJWT, Pydantic v2 |
| **Base de Datos** | PostgreSQL 15 en Docker (`localhost:5433`, db: `bolivar_responde`) |
| **Machine Learning** | PyTorch, Transformers (Hugging Face), Torchvision, Scikit-learn, PIL |
| **Geolocalización** | Browser Geolocation API + Nominatim Reverse Geocoding (OpenStreetMap) |

---

## 🔄 Human-in-the-Loop & Feedback Loop

El sistema cuenta con un circuito cerrado de aprendizaje continuo:
1. **Lado Ciudadano (`/reportes/nuevo`):** La IA sugiere una categoría al analizar foto + descripción. El usuario puede usar el botón **"Corregir categoría"** antes de enviar.
2. **Lado Administrador (`/dashboard`):** En el modal de detalle del reporte, el admin puede marcar si la predicción fue acertada o indicar la categoría real.
3. **Persistencia:** Las correcciones se guardan en la tabla `feedback` de PostgreSQL con `correct=False` y `correct_class`.
4. **Reentrenamiento Continuo:** Ejecutando `python backend/scripts/export_dataset.py`, se genera un dataset consolidado `retraining_dataset.json` con los ejemplos corregidos para reentrenar la red.

---

## 🗄️ Esquema de Base de Datos (PostgreSQL)

Tablas creadas y migradas con Alembic:
1. `users` (id, name, email, password_hash, role, created_at)
2. `categories` (id, name, area, description, active, created_at) — seed preparado para 23 etiquetas; ejecutar el seed en PostgreSQL para materializarlas.
3. `model_versions` (id, version, architecture, dataset_version, macro_f1, created_at)
4. `reports` (id, user_id, category_id, image_path, description, latitude, longitude, address, status, priority, created_at, updated_at)
5. `ai_predictions` (id, report_id, model_version_id, predicted_class, confidence, created_at)
6. `feedback` (id, prediction_id, correct, correct_class, reviewed_by, created_at)

---

## 🌐 Rutas y Páginas Frontend

- `/` — Landing page institucional de Bolívar Responde
- `/login` y `/registro` — Autenticación ciudadana / administrativa con JWT
- `/reportes/nuevo` — Formulario con subida de imagen, inferencia multimodal, GPS automático, corrección de categoría y confirmación
- `/reportes` — Grilla pública de reportes ciudadanos con visualización de estado y confianza IA
- `/mapa` — Mapa interactivo geoespacial con pines interactivos y popups informativos
- `/dashboard` — Panel de administración con KPIs, tabla de gestión, filtros en tiempo real y panel de feedback/corrección

---

## ⚙️ Decisiones Técnicas Clave

| Fecha | Decisión | Motivo |
|---|---|---|
| ago-2026 | Reemplazo de CNN clásica por ViT + RoBERTa | Captura dependencias cruzadas entre la imagen del problema y el texto del ciudadano |
| ago-2026 | Puerto Postgres 5433 en docker-compose | Evitar colisión con servicio PostgreSQL nativo en puerto 5432 del host |
| ago-2026 | Downgrade de bcrypt a 3.2.2 | Incompatibilidad conocida entre `passlib 1.7.4` y `bcrypt >= 4.0` |
| ago-2026 | OpenStreetMap + Leaflet | Solución open-source completa y sin costos de API keys (vs Google Maps) |
| ago-2026 | Reverse Geocoding vía Nominatim | Conversión transparente de coordenadas GPS a dirección legible (Calle y altura) |
