# MÓDULO: TRÁNSITO Y ESTACIONAMIENTO

## Objetivo

Agregar a Reporte Bolívar un módulo especializado para detectar y clasificar problemas relacionados con vehículos, tránsito y estacionamiento utilizando IA multimodal.

El usuario podrá enviar:

- Foto.
- Descripción.
- Ubicación.

La IA combinará:

```text
Imagen → ViT
Texto → RoBERTa-BNE
          ↓
   Cross-Attention
          ↓
 Clasificación


 Taxonomía
TRÁNSITO_Y_ESTACIONAMIENTO
│
├── ESTACIONAMIENTO_INDEBIDO
│   ├── CORDON_AMARILLO
│   ├── EN_MEDIO_DE_CALLE
│   ├── OBSTRUCCION_DE_ENTRADA
│   ├── SOBRE_VEREDA
│   ├── LUGAR_RESERVADO
│   └── LUGAR_PROHIBIDO
│
├── VEHICULO_ABANDONADO
├── OBSTRUCCION_DE_CIRCULACION
├── SENALIZACION_DE_TRANSITO
└── SEMAFORO
Arquitectura
              IMAGEN
                 ↓
                ViT
                 ↓
         Visual Features
                 │
                 ▼
          Cross-Attention
                 ▲
                 │
          Text Features
                 ▲
                 │
            RoBERTa-BNE
                 ▲
                 │
               TEXTO
                 ↓
          Fused Features
                 ↓
        Classification Head
                 ↓
          Categoría final

La clasificación será jerárquica:

Tránsito
   ↓
Estacionamiento indebido
   ↓
Cordón amarillo
Dataset

Cada registro debe contener:

imagen
texto
categoría
subcategoría
tipo

Ejemplo:

{
  "image": "auto_001.jpg",
  "text": "Auto estacionado sobre cordón amarillo",
  "category": "transito_y_estacionamiento",
  "subcategory": "estacionamiento_indebido",
  "type": "cordon_amarillo"
}

Incluir casos positivos, negativos y ambiguos.

Salida de la IA
{
  "category": "transito_y_estacionamiento",
  "subcategory": "estacionamiento_indebido",
  "type": "cordon_amarillo",
  "confidence": 0.94,
  "requires_review": false
}

Si la confianza es baja:

REQUIERE_REVISION_HUMANA
Prioridad

Agregar una prioridad:

BAJA
MEDIA
ALTA
CRÍTICA

Ejemplo:

Vehículo estacionado incorrectamente → MEDIA
Obstrucción de entrada → MEDIA/ALTA
Calle completamente bloqueada → ALTA
Regla importante

La IA debe detectar y clasificar situaciones, pero no determinar automáticamente una infracción legal.

Separar:

IA
↓
Clasificación visual/textual
↓
Rule Engine
↓
Normativa municipal
↓
Resultado
Evaluación

Comparar:

ViT
RoBERTa-BNE
ViT + RoBERTa
ViT + RoBERTa + Cross-Attention

Evaluar con:

Precision
Recall
F1-score
Macro F1
Confusion Matrix
Implementación
Definir taxonomía.
Crear/obtener dataset.
Etiquetar imagen + texto.
Implementar ViT.
Implementar RoBERTa-BNE.
Implementar Cross-Attention.
Entrenar modelo multimodal.
Evaluar y corregir errores.
Implementar API FastAPI.
Integrar con Next.js.
Mostrar categoría, confianza y prioridad.
Incorporar feedback humano.
Tecnologías
Python
PyTorch
Hugging Face Transformers
ViT
RoBERTa-BNE
FastAPI
PostgreSQL
Next.js


Este módulo después se puede integrar con **Animales, Infraestructura, Limpieza, Alumbrado, etc.**, 