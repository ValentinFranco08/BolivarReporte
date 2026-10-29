# Bolívar Animal

**Plataforma inteligente de rescate, reencuentro y protección animal para el Municipio de Bolívar, Buenos Aires.**

> Ecosistema integral de bienestar animal impulsado por una red neuronal multimodal propia (Visión por Computadora + Procesamiento de Lenguaje Natural en Español) para el reencuentro de mascotas, censo municipal con chapitas QR y prevención comunitaria de envenenamientos.

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![PyTorch](https://img.shields.io/badge/Deep%20Learning-PyTorch%20%2F%20Transformers-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

---

## Arquitectura MVC y programación orientada a objetos

El backend separa controladores FastAPI, servicios de negocio, repositorios SQLAlchemy e infraestructura. La vista es Next.js. ML cuenta con un `Trainer` común para ViT, RoBERTa y multimodal, una interfaz común de modelos, preprocesamiento compartido y checkpoints con metadatos.

La [guía de arquitectura](docs/ARQUITECTURA.md) explica las clases, principios de POO, diagramas UML, transacciones, comandos de mantenimiento y verificación. Para empezar, seguí los tres recorridos de lectura al inicio de esa guía: clasificar, crear un reporte y entrenar. `main.py` solo ensambla la aplicación; las migraciones, semillas y reindexación son comandos explícitos.

---

## 🐾 ¿Qué es Bolívar Animal?

Hoy en día, cuando una mascota se pierde o se rescata a un animal en la vía pública, la búsqueda se dispersa en publicaciones de Facebook, estados de WhatsApp y grupos vecinales: los avisos se pierden rápidamente, no hay cruce de datos geográfico ni trazabilidad oficial.

**Bolívar Animal** unifica la respuesta municipal y ciudadana en una sola plataforma inteligente articulada en cuatro pilares:

1. **Reencuentro Inteligente de Mascotas (Matching Bi-Modal con IA):**
   * Cruce automático en tiempo real entre avisos de animales **perdidos (`lost`)** y **encontrados (`found`)**.
   * Algoritmo híbrido que combina la similitud visual del animal (aislando el fondo mediante *Auto-Crop*), la descripción semántica en lenguaje natural (raza, tamaño, colores, marcas) y la proximidad geográfica mediante geolocalización.
2. **REMUM (Registro Municipal de Mascotas):**
   * Padrón digital de animales con dueño y animales comunitarios del partido de Bolívar.
   * Emisión de credenciales oficiales y generación automática de **códigos QR físicos** para imprimir y colocar en la chapita del collar, permitiendo que cualquier vecino que lo encuentre escanee el código y contacte al tutor al instante.
3. **Alertas Críticas SOS (Alerta Cebo):**
   * Mapeo georreferenciado y notificación comunitaria inmediata ante focos de envenenamiento o cebos tóxicos sospechosos en plazas y calles, protegiendo tanto a los animales como a los niños del barrio.
4. **Mesa Operativa y Zoonosis Municipal:**
   * Panel de control administrativo para el equipo de Zoonosis y rescatistas: seguimiento del ciclo de vida de los reportes (*reportado $\rightarrow$ en tránsito $\rightarrow$ reunido / adoptado*), validación de alertas y estadísticas poblacionales.

---

## 🧠 Arquitectura de la Inteligencia Artificial

Para que un vecino de a pie no tenga que completar formularios técnicos complejos, la plataforma cuenta con un modelo multimodal unificado propio (**`BolivarMultimodalModel`**, ~218,6 Millones de parámetros) entrenado para interpretar conjuntamente **la foto del animal y la descripción en español**:

```text
     FOTO DEL ANIMAL (Cámara / Galería)              DESCRIPCIÓN (Lenguaje natural)
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
         Diagnóstico & Prioridad                         Vector Embedding L2 (768d)
        (Clasificación de situación)                   (Matching de similitud de mascotas)
```

### Componentes Técnicos de Deep Learning
* **Rama Visual:** `google/vit-base-patch16-224` (12 bloques Transformer, 86,4M de parámetros).
* **Rama Textual:** `bertin-project/bertin-roberta-base-spanish` (12 bloques Transformer, 124,6M de parámetros).
* **Módulo de Fusión (Cross-Attention):** `CrossAttentionFusion` (8 cabezas de atención, proyección FFN a 3.072 neuronas, 7,1M de parámetros). El texto guía a la red hacia qué rasgo visual mirar (ej: *"manto negro con patas claras y collar rojo"*).
* **Auto-Crop Multi-Escala:** Detección y recorte focalizado automático del animal para extraer embeddings limpios sin interferencia del fondo de la calle o patio.
* **Score Híbrido de Coincidencia (Perdido vs Hallado):**
  $$\text{Score Final} = w_{\text{vis}} \cdot \text{Sim}_{\text{Coseno}} + w_{\text{sem}} \cdot \text{Sim}_{\text{Semántica}} + w_{\text{geo}} \cdot \text{Factor}_{\text{Proximidad}}$$
* **Aprendizaje Continuo (Active Learning Replay):** Entrenamiento en `ml/training/incremental.py` con *Experience Replay* que aprovecha las validaciones de Zoonosis para reajustar los pesos para reducir el riesgo de olvido catastrófico.

### Resultados en el Conjunto de Prueba (*Test Set*):
* **Accuracy:** **96.67%** (58 aciertos sobre 60 casos de prueba independientes).
* **Macro F1-Score:** **94.19%** (100% de efectividad en situaciones críticas: *animal herido, en riesgo y abandono*).

---

## 🏷️ Taxonomía de Zoonosis y Rescate

El modelo clasifica automáticamente los casos en las situaciones prioritarias para la comunidad:

| Categoría | Descripción de la Situación | Acción Sugerida |
|---|---|---|
| **`animal_perdido`** | Mascota con hogar extraviada por su dueño. | Búsqueda activa y cruce con reportes de hallazgo. |
| **`animal_encontrado`** | Animal retenido temporalmente por un vecino o visto desorientado. | Alerta a tutores de la zona e inicio de matching. |
| **`posible_animal_herido`** | Animal con traumatismos, renguera, hemorragia o dolor visible. | Intervención veterinaria de urgencia. |
| **`animal_en_riesgo`** | Animal atrapado, en autopista/ruta o cerca de peligros inminentes. | Despacho prioritario de rescate. |
| **`abandono`** | Animal desnutrido, atado o abandonado en la vía pública. | Rescate y derivación a hogar de tránsito. |
| **`animal_suelto`** | Perros o equinos deambulando que pueden ocasionar accidentes viales. | Notificación preventiva de zoonosis. |

---

## 🛠️ Stack Tecnológico

| Capa | Tecnologías |
|---|---|
| **Frontend** | **Next.js 15** (App Router, React 19, TypeScript), Sistema de Diseño "Rastro" (CSS Design Tokens con modo claro/oscuro), Leaflet & OpenStreetMap, Lucide Icons. |
| **Backend** | **Python (FastAPI)**, Pydantic v2, SQLAlchemy (Async/Sync pooling), Uvicorn, Pillow. |
| **Base de Datos** | **PostgreSQL** (Docker) con fallback SQLite para entornos livianos. Migraciones explícitas con Alembic. |
| **Deep Learning** | **PyTorch**, Hugging Face Transformers, Torchvision. Aceleración nativa en Apple Silicon (MPS), CUDA o CPU. |
| **Seguridad & Auth** | JWT (OAuth2 Password Bearer), Hashing de contraseñas Bcrypt/Passlib, roles `citizen` y `admin`. |

---

## 📂 Estructura del Repositorio

```text
backend/app/
├── main.py                  # Composición y ciclo de vida HTTP
├── controllers/             # Rutas y contratos HTTP
├── services/                # Casos de uso y políticas de negocio
├── repositories/            # Persistencia SQLAlchemy
├── infrastructure/          # Archivos, unidad de trabajo y carga diferida
├── core/                    # Configuración y errores
├── dependencies.py          # Inyección de dependencias
├── models.py                # Entidades ORM
└── schemas.py               # Contratos Pydantic
ml/
├── models/                  # Encoders, fusión, multimodal y baselines
├── data/                    # Dataset, validación y preparación
├── preprocessing/           # Imagen y texto
├── training/                # Preparación, Trainer e incremental
├── evaluation/              # Evaluator y métricas
├── inference/               # Predictor y checkpoints
├── configs/                 # Configuración de experimentos
└── cli.py                   # Entrada común de ML
frontend/                    # Vistas Next.js
backend/scripts/             # Migraciones, seed, exportación y reentrenamiento
backend/tests/               # Pruebas de API, servicios y migraciones
ml/tests/                    # Pruebas del pipeline neuronal
```

---

## 🚀 Inicio Rápido en Desarrollo

El proyecto incluye el script maestro [`./dev.sh`](dev.sh), que levanta la base de datos PostgreSQL en Docker, ejecuta migraciones y datos iniciales demo, arranca la API FastAPI y sirve el frontend Next.js en paralelo:

### 1. Requisitos Previos
* **Python 3.11+** (con entorno virtual en `./venv`)
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
pip install -r backend/requirements.txt -r ml/requirements.txt

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
* ⚡ **Backend API (FastAPI):** [http://localhost:8001](http://localhost:8001) *(Swagger en `/docs`)*
* 🌐 **Frontend (Next.js):** [http://localhost:3000](http://localhost:3000)

*(Para detener todos los servicios de forma limpia, presione `Ctrl + C` en la terminal).*

---

## 👥 Roles y Usuarios de Prueba

Al iniciar el sistema por primera vez, se configuran automáticamente dos cuentas de prueba:

| Rol | Email | Contraseña | Capacidades |
|---|---|---|---|
| **Administrador / Zoonosis** | `admin@bolivar.gob.ar` | `admin123` | Acceso a `/dashboard`, triage de animales en tránsito, verificación de alertas de cebo y feedback del modelo. |
| **Vecino / Tutor** | `vecino@bolivar.gob.ar` | `vecino123` | Publicar pérdidas y hallazgos, registrar mascotas en REMUM y generar chapitas QR. |

---

## 🧪 Pruebas Automatizadas

Para validar la suite completa de tests (matching vectorial, lógica de negocio y endpoints de FastAPI):

```bash
source venv/bin/activate
make test-python
```

---

## 📄 Ámbito del Proyecto

Proyecto de Deep Learning Multimodal enfocado en la modernización cívica, el rescate y el bienestar animal en el Partido de Bolívar, Provincia de Buenos Aires, Argentina.
