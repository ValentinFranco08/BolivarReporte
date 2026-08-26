# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Primario: vecinos de Bolívar, Buenos Aires.** No técnicos. Reportan de pie en la calle, desde el teléfono, con una mano, frente al problema que acaban de encontrar: un bache, una luminaria apagada, un animal suelto, un auto sobre la vereda. Están apurados, a veces con mala señal, a veces de noche. Su trabajo es simple: dejar constancia de algo y saber que alguien lo va a mirar.

**Secundario: personal municipal (rol `admin`).** Trabaja en escritorio, revisa el flujo entrante, prioriza, cambia estados y corrige la clasificación cuando la IA se equivocó. Su trabajo es triage: convertir un caudal desordenado de reportes en una cola de trabajo accionable.

Los dos roles ya existen en el modelo de datos (`UserRole.CITIZEN` / `UserRole.ADMIN`, `backend/app/models.py:8-10`).

## Product Purpose

Convertir reportes informales de vecinos en información estructurada, clasificable y con seguimiento.

Hoy un vecino que ve un bache lo publica en un grupo de Facebook: se diluye, nadie lo cuenta, nadie lo cierra. Reporte Bolívar le da a cada reporte un ciclo de vida gestionable, una categoría, una prioridad y una ubicación.

**Éxito:** un vecino reporta en menos de un minuto sin elegir categorías de un menú, y puede ver después que su reporte cambió de estado. Para el municipio: una cola priorizada en vez de un buzón.

## Positioning

El vecino **no clasifica nada**. Saca una foto, escribe una línea si quiere, y listo.

Una red neuronal multimodal (ViT + RoBERTa + Cross-Attention) analiza **imagen y texto en conjunto** —no por separado— y deduce la categoría entre 23 y una prioridad sugerida. Eso es lo que un formulario municipal común no puede copiar: los demás le piden al ciudadano que sepa de antemano en qué casillero entra su problema. Acá el sistema lo deduce.

**Decisión de producto confirmada: la IA es invisible para el ciudadano.** Nada de "ViT + RoBERTa", nada de porcentajes de confianza, nada de top-k, nada de jerga de modelos en las superficies públicas. La inteligencia se demuestra en que no hay que elegir categoría, no en contarla. La maquinaria (confianza, predicciones alternativas, feedback de reentrenamiento, versión de modelo) vive solo en el panel municipal.

## Operating Context

**Flujo del vecino:** abre la app en el teléfono → foto (cámara del dispositivo) → el navegador toma la geolocalización y la resuelve a una dirección legible → descripción opcional → confirma → el reporte queda registrado.

**Flujo municipal:** panel con la cola de reportes → filtra por área, estado, prioridad, texto → abre un reporte → cambia estado y prioridad → si la clasificación está mal, la corrige (y esa corrección queda como par imagen+etiqueta exportable para reentrenar el modelo).

**Ciclo de vida (8 estados, `backend/app/models.py:12-20`):** `reportado`, `clasificado`, `pendiente`, `en_proceso`, `resuelto`, `rechazado`, `duplicado`, `requiere_informacion`. El README documenta solo el camino feliz de 5; los otros 3 existen y el panel los usa.

**Prioridades (4, `models.py:22-26`):** `baja`, `media`, `alta`, `critica`. La taxonomía sugiere solo baja/media/alta; `critica` es exclusivamente manual.

**Escena física:** calle, luz de día directa o noche, teléfono en la mano. Contraste y tamaño de objetivo táctil no son detalles estéticos acá, son condiciones de uso.

## Capabilities and Constraints

**Implementado y funcionando:**
- 23 etiquetas hoja en 4 áreas — Infraestructura (5), Higiene Urbana (2), Animales (6), Tránsito y Estacionamiento (10). Fuente de verdad única: `ml/taxonomy.py`.
- Inferencia multimodal sobre foto + texto; devuelve top-3 con score, más jerarquía, prioridad sugerida y `requires_review` cuando la confianza baja de 0.55.
- Auth JWT (HS256, 7 días). Registro, login, `/api/auth/me`.
- CRUD de reportes, PATCH de estado/prioridad, feedback de corrección, export de correcciones para reentrenamiento.
- Geolocalización lat/lng + dirección textual. Reverse geocoding vía Nominatim.
- Almacenamiento de imágenes en filesystem local, servidas por `/uploads`.

**Terminología (usar exactamente esta):** *reporte* (no "ticket", no "denuncia" — el producto describe situaciones, no imputa infracciones), *vecino*, *área*, *categoría*, *estado*, *prioridad*.

**Restricciones técnicas confirmadas:**
- Enums: PostgreSQL guarda los NOMBRES en mayúscula (`REPORTADO`, `MEDIUM`), la API expone los VALORES en minúscula (`reportado`, `media`). El frontend usa siempre minúscula.
- `image_path` es un path relativo (`/uploads/<uuid>.jpg`), no una URL absoluta ni base64. El cliente compone el host.
- El login es `application/x-www-form-urlencoded` con el email en el campo `username` (OAuth2PasswordRequestForm), no JSON.
- `GET /api/reports` devuelve un array plano sin envoltorio de paginación, aunque acepta `skip`/`limit`.
- La respuesta de `POST /api/reports` **no** incluye la jerarquía, `requires_review` ni la prioridad sugerida por la IA: eso solo existe en la respuesta efímera de `POST /api/ai/predict`.

**Deuda conocida, explícitamente no resuelta todavía (no inventar que funciona):**
- El checkpoint distribuido fue entrenado con **14** clases; las 9 de Tránsito y Estacionamiento están en la taxonomía y en la interfaz pero requieren dataset y reentrenamiento antes de inferirse.
- La prioridad que calcula la IA **no se persiste**: todo reporte nace `media`. La transición a `clasificado` nunca se asigna automáticamente.
- No hay verificación de rol en el backend: `PATCH /api/reports/{id}`, el feedback y el export están abiertos a cualquier usuario autenticado. `GET /api/reports` y `/uploads/*` son públicos sin auth.
- No hay logout. No hay `.env`: la URL del backend está escrita a mano en 13 lugares y la `SECRET_KEY` está en el repo.
- No hay tests en el frontend.

## Brand Commitments

**Nombre:** *Reporte Bolívar*. Aparece también como "Bolívar Responde" en algunas partes del código; el nombre canónico a usar es **Reporte Bolívar**.

**Voz:** español rioplatense, voseo ("Sacá una foto", "Reportá"). Directo, cívico, sin infantilizar y sin burocracia. Nunca acusatorio: el sistema describe una situación, no señala a un culpable.

**Compromiso legal, textual y obligatorio** (`ml/taxonomy.py:204-207`):
> "La IA clasifica la situación a partir de la foto y el texto. No determina una infracción legal; eso corresponde a la normativa municipal."

Todo reporte lleva `legal_status: "sin_calificacion_legal"`. Esto no es decorativo: es la línea que separa una herramienta cívica de una app de denuncias entre vecinos.

## Evidence on Hand

- **Reportes reales:** 32 imágenes subidas en `backend/uploads/` (nombres UUID, 23 KB a 1.65 MB).
- **Resultado experimental real:** Baseline A (solo ViT), test Macro F1 = **0.5448**. Baseline B (solo RoBERTa) en entrenamiento. Modelo C (multimodal) pendiente. Estos son los únicos números de rendimiento que existen.
- **Taxonomía completa** con áreas, jerarquía de 3 niveles y prioridad por etiqueta: `ml/taxonomy.py`.
- **Descripciones en español** por categoría en `SEED_CATEGORIES` (`ml/taxonomy.py:178-202`).
- **Contexto geográfico:** Bolívar, Provincia de Buenos Aires. Centro usado por el mapa: aprox. -36.23, -61.11.

**Ausencias que no se deben fabricar:** no hay convenio municipal firmado, no hay usuarios reales en producción, no hay testimonios, no hay métricas de adopción, no hay tiempos de resolución reales, no hay acuerdo de servicio. El proyecto es académico (Universidad Nacional del Centro de la Provincia de Buenos Aires) y no debe presentarse como un servicio municipal oficial vigente.

## Product Principles

1. **El vecino no clasifica.** Cualquier decisión de diseño que le pida al ciudadano elegir entre 23 opciones traiciona el mecanismo del producto. La IA absorbe esa complejidad.
2. **La inteligencia se demuestra, no se narra.** Si hay que explicar la arquitectura para que se entienda el valor, el diseño falló.
3. **Un reporte siempre tiene destino.** Estado visible, seguimiento posible. Nunca un formulario que se envía al vacío.
4. **Describir, no acusar.** El producto reporta situaciones. La calificación legal es del municipio, y eso se dice en voz alta.
5. **La calle es el contexto, no el escritorio.** El flujo de reporte se diseña para un pulgar, a la luz del sol, con una mano ocupada. El escritorio es para el municipio.

## Accessibility & Inclusion

Público municipal abierto: se asume rango de edad amplio, incluidos adultos mayores, y uso en exteriores con reflejo solar. Requisitos derivados: contraste alto real, objetivos táctiles generosos, tipografía que escale sin romper el layout, y operabilidad completa por teclado en el panel municipal. El estado actual no cumple esto (modal sin `role="dialog"` ni foco atrapado, inputs sin `htmlFor`, filas de tabla clicables sin acceso por teclado, `alert()` nativo, emojis como iconografía).
