# Reporte Bolívar — Plan de Implementación

**Plataforma inteligente de participación ciudadana para Bolívar, Buenos Aires.**

---

## 1. Qué es Reporte Bolívar

Reporte Bolívar transforma una queja informal en información estructurada, clasificable y accionable mediante Inteligencia Artificial multimodal.

```text
Problema ciudadano
        ↓
Foto + descripción + ubicación
        ↓
Inteligencia Artificial (ViT + RoBERTa + Cross-Attention)
        ↓
Problema estructurado
        ↓
Clasificación + Confianza
        ↓
Priorización
        ↓
Seguimiento
        ↓
Resolución
```

**No es una red social de quejas.** Es un sistema de gestión de problemáticas ciudadanas donde el valor está en el proceso posterior al reporte.

---

## 2. Objetivo académico

Demostrar experimentalmente que un modelo multimodal que combina **imagen + texto** mediante **Cross-Attention** clasifica mejor los reportes ciudadanos que modelos unimodales (solo imagen o solo texto).

**Hipótesis:**
> La utilización conjunta de información visual y textual mediante Cross-Attention mejora la clasificación de reportes ciudadanos respecto a modelos que utilizan únicamente imágenes o únicamente texto.

**Experimentos a comparar:**

| Modelo | Entrada | Arquitectura |
|---|---|---|
| A — ViT | Imagen | ViT → Classifier |
| B — RoBERTa | Texto | RoBERTa → Classifier |
| C — Multimodal | Imagen + Texto | ViT + RoBERTa + Cross-Attention → Classifier |

**Métrica principal:** Macro F1

---

## 3. Stack tecnológico

### Frontend
- Next.js + React + TypeScript
- Tailwind CSS
- React Hook Form + Zod
- Leaflet (mapa)

### Backend
- Python + FastAPI
- Pydantic + SQLAlchemy + Alembic

### Base de datos
- PostgreSQL

### Machine Learning
- PyTorch (con soporte MPS para Apple Silicon)
- Hugging Face Transformers + Datasets
- TorchVision, scikit-learn, NumPy, Pandas, Pillow

### Modelos
- **Vision Encoder:** `google/vit-base-patch16-224`
- **Text Encoder:** `bertin-project/bertin-roberta-base-spanish` (RoBERTa especializado en español)
- **Fusión:** Cross-Attention (`nn.MultiheadAttention`)

### Infraestructura
- Docker + Docker Compose
- Git + GitHub
- Linux VPS (producción)

---

## 4. Arquitectura de la IA

### Arquitectura Multimodal (Modelo C)

```text
                         REPORTE
                            │
              ┌─────────────┴─────────────┐
              │                           │
           IMAGEN                       TEXTO
              │                           │
              ▼                           ▼
         ViT-Base/16                 RoBERTa-BNE
              │                           │
              ▼                           ▼
       Visual Tokens (197×768)      Text Tokens (L×768)
              │                           │
              └─────────────┬─────────────┘
                            ▼
                     CROSS-ATTENTION
                  Q=Text, K=V=Visual
                            │
                            ▼
                     Fusion Features
                            │
                            ▼
                       Mean Pooling
                            │
                            ▼
                           768
                            ↓
                    Linear 768→512
                            ↓
                          GELU
                            ↓
                       Dropout 0.30
                            ↓
                    Linear 512→256
                            ↓
                          GELU
                            ↓
                       Dropout 0.20
                            ↓
                     Linear 256→23*
                            ↓
                      23 ETIQUETAS HOJA*
```

### Entrenamiento progresivo (3 Fases)

| Fase | ViT | RoBERTa | Cross-Attention + Head |
|---|---|---|---|
| 1 | Congelado | Congelado | Entrenando (LR=1e-4) |
| 2 | Últimas 2 capas (LR=1e-5) | Congelado | Entrenando (LR=1e-4) |
| 3 | Últimas 2 capas (LR=1e-5) | Últimas 2 capas (LR=1e-5) | Entrenando (LR=1e-4) |

---

## 5. Categorías (23)

| # | Categoría | Área |
|---|---|---|
| 01 | `bache` | Infraestructura |
| 02 | `calle_deteriorada` | Infraestructura |
| 03 | `luminaria_danada` | Infraestructura |
| 04 | `arbol_caido` | Infraestructura |
| 05 | `perdida_agua` | Infraestructura |
| 06 | `basura` | Higiene Urbana |
| 07 | `microbasural` | Higiene Urbana |
| 08 | `animal_perdido` | Animales |
| 09 | `animal_encontrado` | Animales |
| 10 | `animal_suelto` | Animales |
| 11 | `animal_en_riesgo` | Animales |
| 12 | `posible_animal_herido` | Animales |
| 13 | `abandono` | Animales |
| 14 | `senalizacion_danada` | Tránsito y Estacionamiento |
| 15–20 | `cordon_amarillo`, `en_medio_de_calle`, `obstruccion_de_entrada`, `sobre_vereda`, `lugar_reservado`, `lugar_prohibido` | Tránsito — Estacionamiento indebido |
| 21 | `vehiculo_abandonado` | Tránsito y Estacionamiento |
| 22 | `obstruccion_de_circulacion` | Tránsito y Estacionamiento |
| 23 | `semaforo_danado` | Tránsito y Estacionamiento |

\* Es el objetivo del próximo entrenamiento. El checkpoint actual sigue siendo 14-way y no puede inferir las nueve clases nuevas hasta completar el dataset y reentrenar. La IA entrega clasificación de situación, prioridad operativa y revisión humana bajo confianza; no determina infracciones legales.

---

## 6. Dataset

- **Formato:** `imagen + texto + label` (multimodal)
- **Objetivo:** 500–1000 ejemplos por categoría
- **División:** 70% train / 15% val / 15% test
- **Estado actual:** 573 ejemplos y checkpoint de 14 etiquetas. Para Tránsito: reunir ~100 imágenes por cada una de las nueve hojas nuevas, regenerar el dataset y reentrenar con 23 clases. Ver `PLAN_IMPLEMENTACION_TRANSITO.md`.
- **Fuentes futuras:** Hugging Face Datasets, APIs públicas, datos propios anotados

---

## 7. Estructura del repositorio

```text
bolivar-responde/
│
├── frontend/
│   ├── app/                    ← Páginas Next.js
│   ├── components/             ← Componentes React
│   └── lib/                    ← Servicios y utilidades
│
├── backend/
│   └── app/
│       ├── api/                ← Endpoints FastAPI
│       ├── models/             ← SQLAlchemy models
│       ├── schemas/            ← Pydantic schemas
│       ├── services/           ← Lógica de negocio
│       └── main.py
│
├── ml/
│   ├── datasets/
│   │   ├── build_dataset.py    ← Genera dataset.json
│   │   └── multimodal_dataset.py ← PyTorch Dataset
│   ├── models/
│   │   ├── vit_encoder.py      ← Encoder visual
│   │   ├── roberta_encoder.py  ← Encoder textual
│   │   ├── cross_attention.py  ← Fusión Cross-Attention
│   │   └── multimodal.py       ← Modelo completo
│   ├── training/
│   │   ├── train_vit.py        ← Baseline A (solo imagen)
│   │   ├── train_roberta.py    ← Baseline B (solo texto)
│   │   └── train_multimodal.py ← Modelo C (multimodal)
│   ├── evaluation/             ← Comparación de resultados
│   ├── inference/              ← Módulo de inferencia para FastAPI
│   └── checkpoints/            ← Pesos guardados por experimento
│
├── database/                   ← Seeds y migraciones SQL
├── docs/
├── README.md
├── AGENT.md
├── nuevo plan de implementacion.md
├── enfoque del proyecto.md
└── docker-compose.yml
```

---

## 8. API (FastAPI)

### Endpoints MVP

```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me

POST   /api/reports              ← Crear reporte (imagen + texto + ubicación)
GET    /api/reports              ← Listar reportes
GET    /api/reports/{id}         ← Detalle de reporte
PUT    /api/reports/{id}/status  ← Actualizar estado

POST   /api/ai/predict           ← Predicción IA (imagen + texto)
POST   /api/ai/feedback          ← Corrección humana

GET    /api/categories
GET    /api/statistics
GET    /api/health
```

---

## 9. Base de datos (PostgreSQL)

### Tablas principales

**users**
```
id | name | email | password_hash | role | created_at | updated_at
```

**reports**
```
id | user_id | category_id | description | latitude | longitude |
image_path | status | priority | created_at | updated_at
```

Estados del ciclo de vida:
`REPORTADO → CLASIFICADO → PENDIENTE → EN_PROCESO → RESUELTO`
Adicionales: `RECHAZADO | DUPLICADO | REQUIERE_INFORMACIÓN`

**categories**
```
id | name | area | description | active | created_at
```

**ai_predictions**
```
id | report_id | model_version_id | predicted_class | confidence | created_at
```

**feedback**
```
id | prediction_id | correct | correct_class | reviewed_by | created_at
```

**model_versions**
```
id | name | version | architecture | dataset_version | accuracy | macro_f1 | created_at
```

---

## 10. Frontend (Next.js)

### Páginas del MVP

```
/                    ← Landing page
/login               ← Autenticación
/register            ← Registro
/reportes            ← Listado de reportes
/reportes/nuevo      ← Crear reporte (imagen + texto → IA)
/reportes/[id]       ← Detalle + estado
/mapa                ← Mapa de Bolívar con todos los reportes
/dashboard           ← Dashboard administrativo
/animales            ← Módulo específico de animales
```

### Módulo de animales
Cuando un reporte se clasifica como animal (`animal_perdido`, `animal_encontrado`, etc.) se genera una ficha adicional con:
- Fotografía
- Descripción
- Ubicación + fecha
- Estado: `REPORTADO → EN_INVESTIGACIÓN → IDENTIFICADO → RESUELTO`

---

## 11. Orden de implementación

### ML (en curso)
- [x] Estructura `ml/`
- [x] Dataset multimodal (573 ejemplos)
- [x] `MultimodalDataset` + DataLoaders
- [x] `ViTEncoder`, `RoBERTaEncoder`, `CrossAttentionFusion`, `BolivarMultimodalModel`
- [x] Scripts `train_vit.py`, `train_roberta.py`, `train_multimodal.py`
- [ ] Correr Baseline A (ViT) — en curso
- [ ] Correr Baseline B (RoBERTa)
- [ ] Correr Modelo C (Multimodal)
- [ ] `evaluation/compare_results.py`
- [ ] `inference/predict.py`
- [ ] Dataset y reentrenamiento de las 9 hojas nuevas de Tránsito y Estacionamiento (head 23-way)

### Backend
- [x] FastAPI base con CORS
- [ ] PostgreSQL + SQLAlchemy modelos
- [ ] Endpoints CRUD de reportes
- [ ] Autenticación JWT
- [ ] Endpoint `/api/ai/predict` conectado al modelo entrenado
- [ ] Endpoint de feedback

### Frontend
- [x] Landing page (Next.js + Tailwind glassmorphism)
- [x] Formulario `/reportes/nuevo` con IA en tiempo real
- [ ] Autenticación (login / register)
- [ ] Listado de reportes
- [ ] Mapa (Leaflet)
- [ ] Dashboard

---

## 12. Principios del proyecto

1. La IA asiste, no decide de forma autónoma. Siempre hay revisión humana disponible.
2. Cuando la confianza es baja, el sistema marca el reporte para revisión.
3. Las correcciones humanas alimentan el dataset para el siguiente ciclo de entrenamiento.
4. No agregar funcionalidades que no respondan a: ¿esto ayuda a detectar, comprender, gestionar o resolver una problemática real de Bolívar?
5. Prioridad: calidad del dataset > arquitectura del modelo > features de la aplicación.

---

## 13. Métricas de evaluación del modelo

- Accuracy
- Precision / Recall / F1 por clase
- **Macro F1** ← métrica principal
- Weighted F1
- Confusion Matrix por clase
- Tiempo de inferencia por imagen

---

## 14. Feedback Loop

```text
Reporte ciudadano
      ↓
Predicción IA + Confianza
      ↓
¿Confianza alta?
   ↙          ↘
  Sí            No
  ↓              ↓
Validar      Revisión humana
                  ↓
              Corrección
                  ↓
           Dataset validado
                  ↓
          Nuevo entrenamiento
                  ↓
             Modelo v2
```

> No entrenar automáticamente con datos sin validar.

---

*Este documento integra el `nuevo plan de implementacion.md` y el `enfoque del proyecto.md`.  
Para el qué y el por qué: ver `enfoque del proyecto.md`.  
Para el cómo técnico detallado (Cross-Attention, hiperparámetros, fases): ver `nuevo plan de implementacion.md`.*
