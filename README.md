# Reporte Bolívar & Bolívar Animal

**Plataforma cívica inteligente y ecosistema de rescate y registro animal para el Municipio de Bolívar, Buenos Aires.**

> Transforma reportes comunitarios informales en información estructurada, accionable y con seguimiento oficial mediante una red neuronal multimodal propia (Visión + Lenguaje).

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![PyTorch](https://img.shields.io/badge/Deep%20Learning-PyTorch%20%2F%20Transformers-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

---

## 🧭 ¿Qué es?

**Reporte Bolívar** es una solución integral diseñada para resolver dos desafíos críticos de la comunidad:

1. **Gestión de Problemáticas Urbanas:** Los vecinos reportan baches, fallas de luminarias, pérdidas de agua, acumulación de residuos o infracciones de tránsito mediante foto, ubicación georreferenciada y descripción en lenguaje natural. La IA multimodal deduce la categoría, sugiere la prioridad y organiza la cola de trabajo municipal.
2. **Bolívar Animal & REMUM (Registro Municipal de Mascotas):**
   * **Matching Bi-Modal Inteligente:** Cruce automático entre avisos de mascotas perdidas (`lost`) y encontradas (`found`) combinando embeddings visuales (ViT), similitud semántica (raza, pelaje, especie) y proximidad geográfica.
   * **REMUM:** Empadronamiento digital de mascotas y animales comunitarios con generación de credenciales y **códigos QR físicos** para chapitas identificatorias.
   * **Alertas Críticas SOS:** Detección y notificación en mapa de focos de cebos sospechosos o veneno en la vía pública (`alerta_cebo`).

---

## 🧠 Arquitectura de la Inteligencia Artificial

A diferencia de formularios convencionales donde el ciudadano debe clasificar manualmente su solicitud, la plataforma cuenta con un modelo profundo unificado propio (**`BolivarMultimodalModel`**, ~218,6 Millones de parámetros) que procesa la imagen y el texto de manera conjunta:

```text
       IMAGEN (Foto del vecino)                        TEXTO (Descripción en español)
                  │                                                  │
                  ▼                                                  ▼
      Vision Transformer (ViT-Base)                    RoBERTa en Español (bertin-roberta)
    google/vit-base-patch16-224                        bertin-project/bertin-roberta-base
                  │                                                  │
     Visual Tokens: [197 × 768]                          Text Tokens: [L × 768]
                  │                                                  │
                  └─────────────────────────┬────────────────────────┘
                                            │
                                            ▼
                                  Cross-Attention Fusion
                                  (Query = Texto, Key/Value = Imagen)
                                            │
                                            ▼
                                       Mean Pooling
                                            │
                                            ▼
                             MLP Classifier Head (768→512→256→N)
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
         Categoría & Prioridad                           Vector Embedding L2 (768d)
        (Top-3 scores de certeza)                    (Matching de mascotas & centroides)
```

### Componentes de Deep Learning
* **Rama Visual:** `google/vit-base-patch16-224` (12 bloques Transformer, 86,4M params).
* **Rama Textual:** `bertin-project/bertin-roberta-base-spanish` (12 bloques Transformer, 124,6M params).
* **Fusión:** `CrossAttentionFusion` (8 cabezas de atención, proyección FFN a 3.072 neuronas, 7,1M params).
* **Auto-Crop Multi-Escala:** Inferencia de mascotas con recorte focalizado automático para aislar al animal del fondo.
* **Score Híbrido de Coincidencia:**
  $$\text{Score} = w_{\text{vis}} \cdot \text{Sim}_{\text{Coseno}} + w_{\text{sem}} \cdot \text{Sim}_{\text{Semántica}} + w_{\text{geo}} \cdot \text{Factor}_{\text{Distancia}}$$
* **Aprendizaje Continuo (Active Learning Replay):** Pipeline (`train_incremental.py`) que aprovecha las correcciones del equipo municipal para reentrenar sin sufrir *olvido catastrófico*.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnologías |
|---|---|
| **Frontend** | **Next.js 15** (App Router, React 19, TypeScript), Sistema de Diseño "Rastro" (CSS Design Tokens, Dark/Light mode), Leaflet & OpenStreetMap, Lucide Icons. |
| **Backend** | **Python (FastAPI)**, Pydantic v2, SQLAlchemy (Async/Sync pooling), Uvicorn, Pillow. |
| **Base de Datos** | **PostgreSQL** (Docker) con fallback SQLite para entornos ligeros. Migración y sincronización automática de esquema con `sync_db.py`. |
| **Deep Learning** | **PyTorch**, Hugging Face Transformers, Torchvision. Aceleración nativa en Apple Silicon (MPS), CUDA o CPU. |
| **Seguridad & Auth** | JWT (OAuth2 Password Bearer), Hash de contraseñas Bcrypt/Passlib, roles `citizen` y `admin`. |

---

## 📂 Estructura del Repositorio

```
proyecto-redes-neuronales/
├── backend/                  ← API REST FastAPI
│   ├── app/
│   │   ├── ai_service.py     ← Carga del modelo PyTorch, auto-crop y embeddings
│   │   ├── auth.py           ← Gestión de tokens JWT y hashing
│   │   ├── crud.py           ← Lógica de base de datos y algoritmos de matching
│   │   ├── database.py       ← Conexión PostgreSQL / SQLite
│   │   ├── main.py           ← Endpoints públicos, auth, reportes, REMUM y SOS
│   │   ├── models.py         ← Modelos SQLAlchemy (Report, Category, Remum, Feedback)
│   │   └── schemas.py        ← Esquemas Pydantic v2
│   ├── scripts/
│   │   └── sync_db.py        ← Migración y sincronización de columnas de base de datos
│   └── tests/                ← Suite de tests automatizados (Pytest)
├── frontend/                 ← Aplicación Web Next.js 15
│   ├── app/
│   │   ├── page.tsx          ← Feed ciudadano, mapa rápido y buscador interactivo
│   │   ├── reportes/         ← Listado con filtros avanzados y galería
│   │   ├── mapa/             ← Mapa georreferenciado en pantalla completa
│   │   ├── remum/            ← Registro Municipal de Mascotas y carnet digital
│   │   ├── qr/               ← Escáner y generador de chapitas identificatorias QR
│   │   ├── sos/              ← Módulo de Alerta Cebo y emergencias veterinarias
│   │   └── dashboard/        ← Panel administrativo municipal (triage, feedback y métricas)
│   └── components/           ← Componentes modulares accesibles y responsivos
├── ml/                       ← Núcleo de Machine Learning
│   ├── checkpoints/          ← Pesos entrenados (.pt) multimodal y baselines
│   ├── datasets/             ← dataset.json (547 muestras) y cargadores PyTorch
│   ├── models/               ← vit_encoder.py, roberta_encoder.py, multimodal.py
│   └── training/             ← train_multimodal.py, train_incremental.py, train_vit.py
├── local_images/             ← Dataset de imágenes locales organizadas por splits y clases
├── dev.sh                    ← Script automatizado de inicio para desarrollo
└── docker-compose.yml        ← Contenedor de base de datos PostgreSQL
```

---

## 🚀 Inicio Rápido en Desarrollo

El proyecto incluye el script maestro [`./dev.sh`](dev.sh), que levanta la base de datos PostgreSQL en Docker, sincroniza tablas/esquemas, arranca la API FastAPI y sirve el frontend Next.js en paralelo:

### 1. Requisitos Previos
* **Python 3.11+** (con entorno virtual configurado en `./venv`)
* **Node.js 20+** y `npm`
* **Docker** (opcional pero recomendado para PostgreSQL local)

### 2. Configuración Inicial
```bash
# 1. Clonar el repositorio y entrar al directorio
git clone https://github.com/ValentinFranco08/BolivarReporte.git
cd BolivarReporte

# 2. Configurar entorno virtual de Python
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 3. Instalar dependencias del frontend
cd frontend && npm install && cd ..
```

### 3. Levantar Todo con un Solo Comando
```bash
chmod +x dev.sh
./dev.sh
```

El script iniciará automáticamente:
* 🐘 **PostgreSQL (Docker):** Puerto `5433`
* ⚡ **Backend API (FastAPI):** [http://localhost:8001](http://localhost:8001) *(Documentación interactiva en `/docs`)*
* 🌐 **Frontend (Next.js):** [http://localhost:3000](http://localhost:3000)

*(Para apagar todos los procesos de forma limpia, simplemente presione `Ctrl + C` en la terminal).*

---

## 👥 Usuarios de Prueba por Defecto

Al inicializar la base de datos, el backend genera automáticamente las credenciales iniciales de prueba:

| Rol | Email | Contraseña | Permisos |
|---|---|---|---|
| **Administrador Municipal** | `admin@bolivar.gob.ar` | `admin123` | Acceso a `/dashboard`, triage de reportes, cambio de estados, validación y fusión de categorías. |
| **Vecino Ciudadano** | `vecino@bolivar.gob.ar` | `vecino123` | Creación de reportes, registro de mascotas en REMUM, alertas y seguimiento personal. |

---

## 🏷️ Taxonomía de Problemáticas (23 Categorías)

El sistema soporta 23 etiquetas en 4 grandes áreas urbanas:

1. **Infraestructura:** `bache`, `calle_deteriorada`, `luminaria_danada`, `arbol_caido`, `perdida_agua`.
2. **Higiene Urbana:** `basura`, `microbasural`.
3. **Animales & Zoonosis:** `animal_perdido`, `animal_encontrado`, `animal_suelto`, `animal_en_riesgo`, `posible_animal_herido`, `abandono`.
4. **Tránsito y Estacionamiento:** `senalizacion_danada`, `cordon_amarillo`, `en_medio_de_calle`, `obstruccion_de_entrada`, `sobre_vereda`, `lugar_reservado`, `lugar_prohibido`, `vehiculo_abandonado`, `obstruccion_de_circulacion`, `semaforo_danado`.

---

## 🧪 Pruebas Automatizadas

Para ejecutar la suite de pruebas del backend y verificar la integridad de la base de datos, similitud vectorial y rutas:

```bash
source venv/bin/activate
pytest backend/tests/ -v
```

---

## 📄 Licencia y Ámbito del Proyecto

Desarrollado como proyecto avanzado de Inteligencia Artificial Aplicada y Deep Learning Multimodal enfocado en la modernización de servicios ciudadanos y protección animal para Bolívar, Provincia de Buenos Aires, Argentina.
