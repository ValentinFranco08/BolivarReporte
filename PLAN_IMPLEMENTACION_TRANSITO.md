# Plan de implementación — Tránsito y Estacionamiento

**Proyecto:** Reporte Bolívar (San Carlos de Bolívar)  
**Fuente de requisitos:** `MÓDULO: implementacion nuevo modulo TRÁNSITO Y ESTACIONAMIENTO.md`  
**Fuente de verdad de etiquetas:** `ml/taxonomy.py`  
**Fecha:** 21 ago 2026

---

## 1. Objetivo

Agregar un módulo que clasifique **situaciones** de tránsito y estacionamiento a partir de foto + texto, con salida jerárquica y prioridad operativa.

La IA **no determina infracción legal**. Eso queda fuera (rule engine / normativa municipal).

```text
Foto + descripción + ubicación
        ↓
ViT + RoBERTa-BNE + Cross-Attention
        ↓
{ category, subcategory, type, confidence, requires_review, priority }
        ↓
Revisión humana si confianza < 0.55
```

---

## 2. Principios (no negociables)

1. Clasificar situación visual/textual; **nunca** emitir “infracción”.
2. Confianza baja (`< 0.55`) → `requires_review: true`.
3. Prioridad operativa: `baja | media | alta | critica` (hoy: `alta` / `media` / `baja` en taxonomía).
4. Dataset: **100 fotos de calidad por hoja** (clases nuevas). Las 14 originales ya están ~100.
5. Fuentes de imágenes: Wikimedia Commons, Hugging Face (Road Issues, Illegal Parking, TACO). **No usar Bing como fuente principal.**
6. El checkpoint actual (`best_fase3.pt`) es de **14 clases**. Hasta reentrenar, el modelo **no puede predecir** las 9 hojas nuevas.

---

## 3. Taxonomía (23 hojas)

El modelo entrena con **una etiqueta plana** (leaf). La jerarquía se arma en `classify_label()`.

```text
TRÁNSITO_Y_ESTACIONAMIENTO
├── ESTACIONAMIENTO_INDEBIDO
│   ├── cordon_amarillo
│   ├── en_medio_de_calle
│   ├── obstruccion_de_entrada
│   ├── sobre_vereda
│   ├── lugar_reservado
│   └── lugar_prohibido
├── VEHICULO_ABANDONADO          → vehiculo_abandonado
├── OBSTRUCCION_DE_CIRCULACION   → obstruccion_de_circulacion
├── SENALIZACION_DE_TRANSITO     → senalizacion_danada (ya existía)
└── SEMAFORO                     → semaforo_danado
```

### Carpetas de imágenes (`local_images/{train,val,test}/`)

| Carpeta | Label |
|---|---|
| `transit_cordon_amarillo` | `cordon_amarillo` |
| `transit_en_medio_de_calle` | `en_medio_de_calle` |
| `transit_obstruccion_de_entrada` | `obstruccion_de_entrada` |
| `transit_sobre_vereda` | `sobre_vereda` |
| `transit_lugar_reservado` | `lugar_reservado` |
| `transit_lugar_prohibido` | `lugar_prohibido` |
| `transit_vehiculo_abandonado` | `vehiculo_abandonado` |
| `transit_obstruccion_de_circulacion` | `obstruccion_de_circulacion` |
| `transit_semaforo_danado` | `semaforo_danado` |
| `urban_senalizacion_danada` | `senalizacion_danada` (existente) |

### Prioridad sugerida

| Tipo | Prioridad |
|---|---|
| `cordon_amarillo`, `sobre_vereda`, `lugar_prohibido`, `vehiculo_abandonado`, `senalizacion_danada` | media |
| `en_medio_de_calle`, `obstruccion_de_entrada`, `lugar_reservado`, `obstruccion_de_circulacion`, `semaforo_danado` | alta |

### Contrato de salida de la IA

```json
{
  "category": "transito_y_estacionamiento",
  "subcategory": "estacionamiento_indebido",
  "type": "cordon_amarillo",
  "label": "cordon_amarillo",
  "confidence": 0.94,
  "requires_review": false,
  "priority": "media",
  "legal_status": "sin_calificacion_legal",
  "disclaimer": "La IA clasifica la situación a partir de la foto y el texto. No determina una infracción legal; eso corresponde a la normativa municipal."
}
```

---

## 4. Estado actual (checklist)

### Hecho

- [x] Taxonomía 23 clases, jerarquía, prioridad, disclaimer (`ml/taxonomy.py`)
- [x] `MultimodalDataset` y `BolivarMultimodalModel` leen `NUM_CLASSES` desde taxonomía
- [x] Plantillas de texto sintético para las 9 carpetas `transit_*` (`ml/datasets/build_dataset.py`)
- [x] `ai_service` carga el **número de clases del checkpoint** (sigue siendo 14) y adjunta `classification`
- [x] `backend/scripts/seed.py` usa `SEED_CATEGORIES`
- [x] Dataset original de 14 hojas ~100 fotos/clase (`local_images/`)
- [x] Entrenamiento 14 clases: test acc ~96.09%, macro F1 ~0.9575 (`ml/checkpoints/multimodal/results.json`)

### Pendiente (orden de ejecución)

- [x] **Fase A — Frontend:** listas de categorías, dashboard, tarjeta IA (jerarquía, prioridad, disclaimer, `requires_review`)
- [ ] **Fase B — Dataset:** script `ml/datasets/collect_transito_100.py` + 100 fotos/clase × 9 hojas
- [ ] **Fase C — Seed DB:** `python backend/scripts/seed.py` (Postgres `localhost:5433`)
- [ ] **Fase D — Rebuild:** `python ml/datasets/build_dataset.py` → `dataset.json` 23 clases
- [ ] **Fase E — Reentrenar:** `python ml/training/train_multimodal.py` (head 23 clases; no reutilizar el head de 14)
- [ ] **Fase F — Evaluar:** confusion matrix, macro F1; comparar con el modelo 14-way solo como referencia histórica
- [ ] **Fase G — Integración:** reiniciar uvicorn, probar `/api/ai/predict` con foto de tránsito

---

## 5. Plan por fases

### Fase A — UI (sin reentrenar) ✅

El usuario ya puede **elegir a mano** las categorías nuevas; la IA seguirá prediciendo solo las 14 viejas hasta la Fase E.

**Archivos**

- `frontend/components/ui/AIResultCard.tsx` — `CATEGORIES_LIST` (23) + mostrar `classification`
- `frontend/app/dashboard/page.tsx` — `ALL_CATEGORIES`
- Formulario / landing: área **Tránsito y Estacionamiento**; mover `senalizacion_danada` de Infraestructura a Tránsito
- Mostrar disclaimer fijo en la tarjeta de resultado

**Implementado:** el select de corrección ciudadana y el feedback del dashboard listan las 23 hojas; el dashboard incorpora el filtro del área; `AIResultCard` consume `classification` y muestra jerarquía, prioridad, disclaimer y “requiere revisión”.

**Criterio de done:** cumplido en la interfaz. La inferencia de las nueve hojas nuevas continúa bloqueada hasta la Fase E.

---

### Fase B — 100 imágenes por clase de tránsito

**Script nuevo:** `ml/datasets/collect_transito_100.py`

Reutilizar helpers de `ml/datasets/fill_missing_to_100.py`:

- fingerprint (evitar duplicados)
- mínimo ~220 px
- rechazar fondos de estudio blancos
- split **70 / 15 / 15** en `train` / `val` / `test`

**Fuentes (prioridad)**

1. Wikimedia Commons (consultas en español + inglés por tipo)
2. Hugging Face: `Programmer-RD-AI/road-issues-detection-dataset` (ya en `ml/datasets/_cache/road_issues/` si está cacheado)
3. Dataset de illegal parking en HF (si está cacheado; no Bing)
4. TACO solo si aporta obstrucción / basura en calzada (no mezclar con `basura` urbana)
5. Roboflow si existe `ROBOFLOW_API_KEY`

**Consultas orientativas**

| Clase | Queries (ejemplo) |
|---|---|
| `cordon_amarillo` | yellow curb parking, no parking yellow kerb, cordón amarillo estacionado |
| `en_medio_de_calle` | car parked in middle of street, vehicle blocking lane |
| `obstruccion_de_entrada` | car blocking driveway, vehicle blocking garage entrance |
| `sobre_vereda` | car parked on sidewalk, vehicle on pavement sidewalk |
| `lugar_reservado` | parking in handicap space, disabled parking violation |
| `lugar_prohibido` | no parking zone car, estacionamiento prohibido |
| `vehiculo_abandonado` | abandoned car street, wrecked abandoned vehicle roadside |
| `obstruccion_de_circulacion` | road blocked by vehicle, street obstruction car |
| `semaforo_danado` | broken traffic light, damaged traffic signal, semáforo roto |

**Calidad**

- Foto urbana real, no stock de estudio
- El objeto de la clase debe ser el sujeto (auto + contexto, no solo un close-up de rueda)
- Cap en **100 por clase** (no inflar con HF sin tope)
- Backup opcional de `local_images` antes de copiar, como se hizo con `local_images_before_100/`

**Criterio de done:** `find local_images -type d -name 'transit_*' | xargs -I{} sh -c 'echo {} $(find {} -type f | wc -l)'` muestra ~100 por split total (70+15+15).

---

### Fase C — PostgreSQL

```bash
source venv/bin/activate
python backend/scripts/seed.py
```

Conexión: `postgresql://postgres:postgres@localhost:5433/bolivar_responde`

**Criterio de done:** `GET /api/categories` lista las 23 hojas; `senalizacion_danada` con área Tránsito.

---

### Fase D — Regenerar dataset JSON

```bash
source venv/bin/activate
python ml/datasets/build_dataset.py
```

Verificar que `dataset.json` tenga 23 labels y textos para `transit_*`.

**Nota:** los textos sintéticos **filtran la etiqueta**. Eso sube accuracy de train (llegó a 100% en 14 clases). Para evaluación honesta, el test set visual importa más que el texto plantilla.

---

### Fase E — Reentrenamiento (23 clases)

**No** cargar el head lineal 256→14. Instanciar modelo con `NUM_CLASSES=23`. Se pueden copiar encoders de `best_fase3.pt` e **inicializar el head nuevo** (recomendado) o entrenar las 3 fases desde encoders Hugging Face.

Comando habitual:

```bash
source venv/bin/activate
python ml/training/train_multimodal.py
```

Ajustar el script si asume 14 clases o un checkpoint incompatible.

**Fases (igual que el plan original)**

| Fase | ViT | RoBERTa | Head + Cross-Attn |
|---|---|---|---|
| 1 | Congelado | Congelado | LR 1e-4 |
| 2 | Últimas 2 capas, 1e-5 | Congelado | 1e-4 |
| 3 | Últimas 2 capas, 1e-5 | Últimas 2 capas, 1e-5 | 1e-4 |

Device: MPS (Apple Silicon).

**Criterio de done:** `ml/checkpoints/multimodal/best_fase3.pt` con head 23; `results.json` con macro F1 test. Revisar confusiones entre hojas de estacionamiento (muy similares visualmente).

---

### Fase F — Evaluación

Métricas: accuracy, P/R/F1 por clase, **macro F1**, matriz de confusión, tiempo de inferencia.

Comparar (si hay tiempo académico): ViT solo / RoBERTa solo / multimodal. El texto sintético sesga RoBERTa; reportarlo.

Clases difíciles esperadas: `lugar_prohibido` vs `lugar_reservado` vs `cordon_amarillo`; `en_medio_de_calle` vs `obstruccion_de_circulacion`.

---

### Fase G — API y producto

1. Reiniciar el proceso de uvicorn en `:8000` para recargar el checkpoint 23-way.
2. Probar `POST /api/ai/predict` con imagen de tránsito + texto.
3. Confirmar que la respuesta incluye `classification` completa.
4. Feedback humano (`/api/ai/feedback`) debe aceptar las 23 labels.

---

## 6. Comandos de entorno (recordatorio)

```bash
cd "/Users/francovalentin/proyecto redes neuronales"
source venv/bin/activate
# DB: Docker Postgres puerto 5433
# API: uvicorn en 8000 (proceso aparte; no es el entrenamiento)
```

---

## 7. Riesgos

| Riesgo | Mitigación |
|---|---|
| Checkpoint 14-way en producción | `ai_service` ya adapta el head al checkpoint; UI debe avisar “corrección manual” hasta reentrenar |
| Hojas de parking casi idénticas | 100 fotos bien etiquetadas; no mezclar queries; revisar val a mano |
| Textos plantilla con leak de label | No usar accuracy de train como métrica de paper; mirar test visual |
| Bing 403 | No usar Bing |
| Head 23 vs pesos 14 | Nunca `load_state_dict` estricto del clasificador viejo |

---

## 8. Fuera de alcance de este plan

- Rule engine de infracciones municipales
- Multas, actas, identificación de patente
- Recolección en la calle de Bolívar (dataset propio anotado: ciclo 2)
- Publicar el modelo o el dataset

---

## 9. Relación con otros docs

| Documento | Rol |
|---|---|
| `PLAN_IMPLEMENTACION.md` | Plan general del producto (desactualizado en nº de clases) |
| `enfoque del proyecto.md` | Qué y por qué |
| `MÓDULO: implementacion nuevo modulo TRÁNSITO Y ESTACIONAMIENTO.md` | Requisitos del módulo |
| `ml/taxonomy.py` | Implementación canónica de labels |
| Este archivo | Orden de trabajo para cerrar el módulo |

Cuando Termine la Fase E, actualizar `PLAN_IMPLEMENTACION.md` sección 4–5 (head `Linear 256→23`, tabla de 23 categorías).
