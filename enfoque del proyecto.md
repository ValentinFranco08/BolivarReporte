# ENFOQUE DEL PROYECTO — REPORTE BOLÍVAR

## 1. Visión general

**Reporte Bolívar** es una plataforma inteligente de participación ciudadana orientada a detectar, clasificar, priorizar y dar seguimiento a problemáticas de la ciudad de Bolívar.

El objetivo **NO** es crear otra red social donde los ciudadanos simplemente publiquen quejas.

El objetivo es convertir:

```text
Problema ciudadano
        ↓
Foto + descripción + ubicación
        ↓
Inteligencia Artificial
        ↓
Problema estructurado
        ↓
Clasificación
        ↓
Priorización
        ↓
Seguimiento
        ↓
Resolución
```

La plataforma debe transformar una queja informal en información útil y accionable.

---

## 2. Problema que se busca solucionar

Actualmente, un ciudadano puede publicar una problemática en:

- Facebook
- Instagram
- WhatsApp
- Grupos vecinales
- Mensajes privados
- Otras redes sociales

Sin embargo, una publicación en una red social generalmente **no está estructurada** como un reporte.

**Ejemplo:**
> *"Otra vez este bache enorme en la calle, hace meses que está así."*

La publicación puede generar comentarios y difusión, pero no necesariamente permite:

- Clasificar el problema.
- Determinar su ubicación exacta.
- Conocer su prioridad.
- Agruparlo con otros reportes.
- Asignarlo a un área.
- Hacer seguimiento.
- Saber si fue solucionado.
- Generar estadísticas.
- Detectar problemas recurrentes.

**Reporte Bolívar** debe resolver esa falta de estructura.

---

## 3. Diferencial frente a una red social

### Red Social
```text
Usuario
 ↓
Publicación
 ↓
Comentarios
 ↓
Reacciones
```

### Reporte Bolívar
```text
Usuario
 ↓
Foto + texto + ubicación
 ↓
IA multimodal
 ↓
Clasificación
 ↓
Prioridad
 ↓
Agrupación
 ↓
Asignación
 ↓
Seguimiento
 ↓
Resolución
```

El valor principal de la plataforma está en el **proceso posterior al reporte**.

---

## 4. Problemáticas iniciales

El sistema debe enfocarse inicialmente en problemáticas concretas de la ciudad:

### 🏗️ Infraestructura
- Baches.
- Calles deterioradas.
- Veredas dañadas.
- Señalización dañada.
- Semáforos con problemas.
- Luminarias dañadas.
- Árboles caídos.
- Pérdidas de agua.

### 🗑️ Higiene urbana
- Basura.
- Microbasurales.
- Residuos acumulados.
- Contenedores desbordados.

### 🌳 Espacios públicos
- Plazas deterioradas.
- Juegos infantiles dañados.
- Mobiliario urbano deteriorado.
- Problemas de mantenimiento.

### 🐾 Animales
El módulo de animales será una de las áreas principales y diferenciales del proyecto.
Categorías iniciales:
- Animal perdido.
- Animal encontrado.
- Animal suelto.
- Animal en riesgo.
- Posible animal herido.
- Posible abandono.

---

## 5. Módulo especializado de animales

El sistema debe contar con un módulo específico para problemáticas relacionadas con animales.

**Objetivo:**
Facilitar la identificación y gestión de situaciones relacionadas con animales encontrados, perdidos, abandonados, heridos o en riesgo.

**Ejemplo de flujo:**
```text
Ciudadano encuentra un perro
        ↓
Sube fotografía
        ↓
Escribe: "Encontré este perro solo cerca de la plaza"
        ↓
IA analiza imagen + texto
        ↓
Categoría: ANIMAL ENCONTRADO
        ↓
Ubicación
        ↓
Fecha
        ↓
Reporte público
```

---

## 6. Posible sistema de animales perdidos/encontrados

Cuando un usuario reporte un animal perdido o encontrado, el sistema podrá generar una ficha:

```text
Animal
├── Fotografía
├── Descripción
├── Ubicación
├── Fecha
├── Categoría
└── Estado
```

**Estados posibles:**
- `REPORTADO`
- `EN INVESTIGACIÓN`
- `IDENTIFICADO`
- `ENCONTRADO`
- `RESUELTO`

En futuras versiones se podrá incorporar búsqueda por similitud visual para detectar posibles coincidencias entre animales perdidos y encontrados.

**Ejemplo de futuro flujo:**
```text
Animal perdido
      ↓
Base de datos
      ↓
Comparación visual
      ↓
Posibles coincidencias
      ↓
Revisión humana
```
> [!NOTE]
> Esta funcionalidad debe considerarse una futura extensión y no una obligación del MVP.

---

## 7. Inteligencia Artificial

La IA debe analizar conjuntamente: **Imagen + Texto**

La arquitectura principal será:

```text
                    IMAGEN
                       │
                       ▼
                  ViT-Base/16
                       │
                       ▼
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
                       │
                       ▼
                Fusion Features
                       │
                       ▼
                Classification Head
                       │
                       ▼
                  Categoría
```

---

## 8. Función de cada modelo

### 👁️ ViT (Vision Transformer)
**Responsabilidad:** Imagen → características visuales.
La imagen permite detectar características relacionadas con:
- Perro, Gato, Bache, Basura, Árbol caído, Luminaria, Calle deteriorada, etc.

### 📝 RoBERTa-BNE
Modelo de lenguaje especializado en español.
**Responsabilidad:** Texto → características semánticas.
**Ejemplo:** *"Encontré un perro solo y parece perdido."*
El modelo debe extraer información relacionada con: *animal, perro, encontrado, solo, posible perdido*.

### 🔗 Cross-Attention
**Responsabilidad:** Fusionar información visual y textual.
La arquitectura debe permitir que el modelo relacione lo que aparece en la imagen con lo que describe el usuario.

**Ejemplo:**
```text
Imagen: perro en una plaza
Texto: "Encontré este perro y parece perdido"
        ↓
 Cross-Attention
        ↓
ANIMAL_ENCONTRADO
```
> [!WARNING]
> No utilizar simplemente la concatenación de embeddings como arquitectura principal.

---

## 9. Clasificación

El modelo debe producir: **Categoría + Confianza**

**Ejemplo:**
```json
{
  "category": "animal_encontrado",
  "confidence": 0.94
}
```

La confianza **NO** debe interpretarse como certeza absoluta. Cuando la confianza sea baja, el sistema debe permitir: **REVISIÓN HUMANA**.

---

## 10. Priorización

Una segunda funcionalidad importante será determinar la prioridad del reporte.

**Ejemplos de prioridad:**
- Animal herido → **Alta**
- Animal encontrado → **Media**
- Bache → **Media**
- Cable peligroso → **Crítica**

La prioridad podrá utilizar:
`Categoría + Texto + Información visual + Ubicación + Cantidad de reportes similares + Antigüedad`

La primera versión puede utilizar reglas simples. Posteriormente podrá evolucionar a un modelo predictivo.

---

## 11. Agrupación de reportes

La plataforma debe detectar reportes potencialmente relacionados.

**Ejemplo:**
- *Reporte 1:* "Hay un bache en esta calle."
- *Reporte 2:* "El pozo de esta esquina está cada vez peor."
- *Reporte 3:* "Otro accidente por el bache."

El sistema puede detectar:
```text
3 reportes
      ↓
Problema relacionado
      ↓
INCIDENTE AGRUPADO
```
Esto permite evitar que cada publicación sea tratada como un problema completamente independiente.

---

## 12. Mapa de problemas

Los reportes deben poder visualizarse geográficamente.

**Ejemplo conceptual:**
```text
                    MAPA DE BOLÍVAR

              🔴 Bache
       🟡 Basura

                    🔴 Luminaria

          🐾 Animal encontrado

                         🔴 Bache
```

El mapa permitirá identificar:
- Zonas con muchos reportes.
- Problemas recurrentes.
- Concentración de determinadas categorías.
- Problemas pendientes y resueltos.

---

## 13. Estado del reporte

Cada reporte debe tener un ciclo de vida:

```text
REPORTADO
    ↓
CLASIFICADO
    ↓
PENDIENTE
    ↓
EN PROCESO
    ↓
RESUELTO
```

**Estados adicionales:** `RECHAZADO`, `DUPLICADO`, `REQUIERE INFORMACIÓN`.

---

## 14. Seguimiento ciudadano

El ciudadano debe poder consultar qué ocurrió con su reporte.

**Ejemplo:**
- **Reporte:** #1842
- **Problema:** Luminaria dañada
- **Estado:** 🟢 RESUELTO
- **Reportado:** 15/08/2026
- **Resuelto:** 18/08/2026

Esto diferencia al sistema de una publicación tradicional en redes sociales.

---

## 15. Dashboard administrativo

La plataforma deberá contar con un dashboard para visualizar:
- Total de reportes
- Reportes pendientes, en proceso, resueltos
- Problemas por categoría, por zona, por período

**Ejemplo:**
```text
REPORTES
------------------
Total       1.284
Pendientes    312
En proceso    147
Resueltos     825
```

---

## 16. Estadísticas

La información acumulada permitirá obtener estadísticas.

**Ejemplo de problemas registrados:**
- Baches: 342
- Basura: 218
- Animales: 187
- Alumbrado: 96
- Pérdidas de agua: 74
- Árboles: 51

También permitirá analizar: problemas por zona, por mes, tiempo promedio de resolución, cantidad de reportes repetidos.

---

## 17. IA como sistema de apoyo

La IA **NO** debe tomar decisiones críticas de manera completamente autónoma. La arquitectura debe seguir el principio:

```text
IA
 ↓
Sugerencia
 ↓
Revisión / validación
 ↓
Decisión
```

Especialmente para:
- Casos de animales heridos.
- Posibles abandonos.
- Prioridades críticas.
- Reportes ambiguos.

---

## 18. Feedback Loop

Las correcciones humanas deberán poder convertirse en nuevos datos de entrenamiento.

```text
Predicción IA
      ↓
Revisión humana
      ↓
  ¿Correcta?
  ↙       ↘
 Sí        No
 ↓          ↓
Validar    Corregir
              ↓
         Dataset validado
              ↓
          Reentrenamiento
              ↓
            Modelo v2
```
> [!IMPORTANT]
> No entrenar automáticamente con información sin validar.

---

## 19. Objetivo del proyecto de IA

El objetivo académico **NO** es simplemente *"Crear una aplicación que use IA"*.

El objetivo es demostrar:
**Que un modelo multimodal que combina información visual y textual puede clasificar mejor los reportes ciudadanos que utilizar únicamente una de las dos modalidades.**

Por eso se deberán comparar:
`ViT` vs `RoBERTa` vs `ViT + RoBERTa + Cross-Attention`

---

## 20. Experimentos

- **Modelo A:** Imagen → ViT → Clasificación
- **Modelo B:** Texto → RoBERTa → Clasificación
- **Modelo C:** Imagen (ViT) + Texto (RoBERTa) → Cross-Attention → Clasificación

**Comparar métricas:** Accuracy, Precision, Recall, F1, Macro F1, Confusion Matrix.
La métrica principal será: **Macro F1**.

---

## 21. MVP (Minimum Viable Product)

La primera versión funcional debe incluir solamente:

1. Registro de usuario.
2. Crear reporte.
3. Subir imagen.
4. Escribir descripción.
5. Obtener ubicación.
6. Clasificación automática.
7. Mostrar categoría y confianza.
8. Estado del reporte.
9. Listado de reportes.
10. Mapa.
11. Dashboard básico.

> [!TIP]
> No implementar inicialmente funcionalidades complejas que no sean necesarias para demostrar el concepto.

---

## 22. Futuras extensiones

Una vez terminado el MVP:
- Detección de reportes duplicados.
- Agrupación mediante embeddings.
- Búsqueda visual de animales.
- Sistema avanzado de prioridad.
- Predicción de tiempo de resolución.
- Detección de tendencias.
- Notificaciones.
- Aplicación móvil.
- Integración con organismos municipales.
- Modelo de lenguaje para generar resúmenes.

---

## 23. Posicionamiento del proyecto

La plataforma debe presentarse como:
> *"Un sistema inteligente de gestión de problemáticas ciudadanas que transforma reportes informales en información estructurada, clasificable y accionable mediante Inteligencia Artificial multimodal."*

**No presentarla como:** *"Una red social de quejas."*

---

## 24. Diferencial principal

| RED SOCIAL | REPORTE BOLÍVAR |
|---|---|
| Publicar<br>Compartir<br>Comentar<br>Reaccionar | Reportar → Entender → Clasificar → Priorizar → Agrupar → Asignar → Hacer seguimiento → Resolver → Generar estadísticas |

---

## 25. Principio general de desarrollo

Todas las funcionalidades deben responder a esta pregunta:
**¿Esta funcionalidad ayuda a detectar, comprender, gestionar o resolver una problemática real de Bolívar?**

Si la respuesta es no, no debe ser una prioridad del MVP. El proyecto debe mantenerse enfocado en:

`PROBLEMA REAL → DATOS → IA → DECISIÓN → ACCIÓN → RESOLUCIÓN`

---

## 26. Resultado esperado

Al finalizar, Reporte Bolívar deberá demostrar que una persona puede:
1. Encontrar un problema.
2. Sacarle una foto.
3. Describirlo.
4. Enviar el reporte.
5. Obtener una clasificación automática.
6. Ver su ubicación.
7. Consultar el estado.
8. Recibir una resolución o actualización.

Mientras que el sistema podrá:
1. Analizar imagen.
2. Analizar texto.
3. Fusionar ambas modalidades.
4. Clasificar el problema.
5. Estimar confianza.
6. Detectar posibles duplicados.
7. Priorizar.
8. Agrupar información.
9. Generar estadísticas.
10. Aprender de correcciones humanas.

---

## 27. Tecnologías

- **Frontend:** Next.js + TypeScript
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL
- **Deep Learning:** PyTorch
- **Vision:** ViT
- **Language:** RoBERTa-BNE
- **Multimodal:** Cross-Attention
- **ML:** Hugging Face Transformers, Datasets, scikit-learn
- **Deployment:** Docker, Linux VPS
- **Version Control:** Git + GitHub

---

## 28. Regla para el agente de desarrollo

El agente deberá priorizar siempre:
- Funcionalidad real.
- Simplicidad del MVP.
- Calidad del dataset.
- Evaluación científica del modelo.
- Reproducibilidad del entrenamiento.
- Seguridad.
- Trazabilidad de las predicciones.
- Feedback humano.
- Documentación.
- Escalabilidad futura.

> [!WARNING]
> No agregar funcionalidades solamente para aumentar la cantidad de características del sistema.

Cada funcionalidad debe tener una relación clara con una problemática real de Bolívar.

**Este archivo debería ser complementario al `PLAN_IMPLEMENTACION.md`**: el plan explica *cómo construirlo*, mientras que este archivo le indica al agente **qué problema debe resolver, cuál es el diferencial y hacia dónde debe orientar todas las decisiones del proyecto**.