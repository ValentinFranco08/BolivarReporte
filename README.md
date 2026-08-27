# Reporte Bolívar

**Sistema inteligente de gestión de problemáticas ciudadanas para Bolívar, Buenos Aires.**

> Transforma reportes informales en información estructurada, clasificable y accionable mediante Inteligencia Artificial multimodal.

---

## ¿Qué es?

**Reporte Bolívar** es una plataforma web donde los ciudadanos reportan problemáticas mediante foto + descripción + ubicación. Una red neuronal multimodal (ViT + RoBERTa + Cross-Attention) analiza conjuntamente la imagen y el texto para clasificar automáticamente el reporte y asignarle una prioridad.

A diferencia de publicar en una red social, cada reporte tiene un ciclo de vida gestionable. La IA describe y prioriza situaciones; no determina infracciones legales ni reemplaza la normativa municipal.

```
REPORTADO → CLASIFICADO → PENDIENTE → EN_PROCESO → RESUELTO
```

---

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | Next.js + TypeScript + Tailwind CSS |
| Backend | Python + FastAPI + SQLAlchemy |
| Base de datos | PostgreSQL |
| Deep Learning | PyTorch + Hugging Face Transformers |
| Vision | `google/vit-base-patch16-224` |
| Lenguaje | `bertin-project/bertin-roberta-base-spanish` |
| Fusión | Cross-Attention (`nn.MultiheadAttention`) |
| Infra | Docker + Linux VPS |

---

## Arquitectura de la IA

```text
IMAGEN + TEXTO
      │
      ├── ViT-Base/16  → Visual Tokens (197 × 768)
      │                          │
      │                    Cross-Attention
      │                    Q=Text, K=V=Visual
      └── RoBERTa-BNE  → Text Tokens (L × 768)
                                 │
                           Mean Pooling
                                 │
                           MLP Head (768→512→256→23*)
                                 │
                           23 etiquetas hoja*
```

### Experimentos comparativos (objetivo académico)

| Modelo | Test Macro F1 |
|---|---|
| A — Solo ViT | 0.5448 ✅ |
| B — Solo RoBERTa | En curso... |
| C — Multimodal (ViT + RoBERTa + Cross-Att.) | Pendiente |

**Hipótesis:** El modelo Multimodal (C) debe superar a los unimodales (A y B).

---

## Categorías (23)

| Área | Categorías |
|---|---|
| Infraestructura | bache, calle_deteriorada, luminaria_danada, arbol_caido, perdida_agua |
| Higiene Urbana | basura, microbasural |
| Animales | animal_perdido, animal_encontrado, animal_suelto, animal_en_riesgo, posible_animal_herido, abandono |
| Tránsito y Estacionamiento | senalizacion_danada, cordon_amarillo, en_medio_de_calle, obstruccion_de_entrada, sobre_vereda, lugar_reservado, lugar_prohibido, vehiculo_abandonado, obstruccion_de_circulacion, semaforo_danado |

\* La taxonomía y la interfaz ya admiten 23 etiquetas. El checkpoint distribuido aún fue entrenado con 14, por lo que las nueve clases nuevas requieren dataset y reentrenamiento antes de ser inferidas automáticamente.

---

## Estructura del proyecto

```
bolivar-responde/
├── frontend/          ← Next.js (TypeScript + Tailwind)
├── backend/           ← FastAPI (Python)
├── ml/
│   ├── datasets/      ← build_dataset.py + multimodal_dataset.py
│   ├── models/        ← vit_encoder.py, roberta_encoder.py, cross_attention.py, multimodal.py
│   ├── training/      ← train_vit.py, train_roberta.py, train_multimodal.py
│   ├── evaluation/    ← compare_results.py
│   ├── inference/     ← predict.py
│   └── checkpoints/   ← Pesos de los 3 modelos
├── PLAN_IMPLEMENTACION.md
├── enfoque del proyecto.md
└── nuevo plan de implementacion.md
```

---

## Instalación y ejecución local

### Requisitos
- Python 3.11+
- Node.js 20+
- PostgreSQL


### Backend
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Entrenamiento ML
```bash
# Generar dataset multimodal
python3 ml/datasets/build_dataset.py

# Entrenar los 3 modelos para comparación
python3 ml/training/train_vit.py
python3 ml/training/train_roberta.py
python3 ml/training/train_multimodal.py
```

---

## Estado del proyecto

- [x] Arquitectura multimodal implementada en PyTorch
- [x] Taxonomía, API y UI preparadas para 23 etiquetas, incluido Tránsito y Estacionamiento
- [x] Dataset y checkpoint actuales de 14 etiquetas (referencia histórica)
- [x] Baseline A (ViT): test Macro F1 = 0.5448
- [ ] Baseline B (RoBERTa): en entrenamiento
- [ ] Modelo C (Multimodal): pendiente
- [ ] PostgreSQL + endpoints CRUD
- [ ] Autenticación JWT
- [ ] Mapa (Leaflet)
- [ ] Dashboard administrativo

---

## Documentación

- [`PLAN_IMPLEMENTACION.md`](PLAN_IMPLEMENTACION.md) — Plan técnico detallado
- [`PLAN_IMPLEMENTACION_TRANSITO.md`](PLAN_IMPLEMENTACION_TRANSITO.md) — Plan específico, estado y criterios de cierre del módulo
- [`enfoque del proyecto.md`](enfoque%20del%20proyecto.md) — Visión y diferencial del producto
- [`nuevo plan de implementacion.md`](nuevo%20plan%20de%20implementacion.md) — Especificaciones técnicas de la arquitectura IA

---

*Proyecto académico de Deep Learning Multimodal 
