# Plan de implementación del filtro visual de coincidencias

**Objetivo.** Mostrar un reporte como posible coincidencia solo cuando la foto aporte evidencia suficiente. Los datos descriptivos y la cercanía sirven para ordenar los candidatos que pasan el filtro. Una foto de hallazgo alcanza para iniciar la búsqueda.

## Caso de regresión

Alejo y Kinoto aparecieron como posible coincidencia con 22 % de similitud visual, 60 % en datos descriptivos y 0 km de distancia. El 41 % combinado resulta aproximadamente de `0,65 × 0,22 + 0,20 × 0,60 + 0,15 × 1`. En la rama de vectores antiguos, basta con superar el mínimo visual de 20 % o con que alguna de las condiciones del puntaje combinado se cumpla. El nuevo filtro debe excluir este par aunque los reportes compartan ubicación.

## 1. Separar admisión y orden en el backend

- Centralizar la decisión en `MatchingPolicy`. Primero verificar que los vectores sean válidos y comparables. Después aplicar el umbral visual correspondiente al modelo que los generó. Solo entonces calcular el orden de las sugerencias.
- En el cotejo anterior, eliminar las condiciones que permiten admitir candidatos por puntaje combinado o por texto. Calibrar el mínimo visual con pares verificados y mantenerlo configurable. El caso Alejo–Kinoto queda como prueba de regresión. La captura por sí sola no alcanza para elegir el umbral definitivo.
- En DINOv2, mantener la comparación por versión de checkpoint. Validar por separado los escenarios de una foto y de varias fotos. Al usar el par más parecido, considerar que aumenta la posibilidad de un parecido casual conforme se comparan más fotos. Cuando corresponda, calibrar umbrales por cantidad de fotos y tamaño de galería.
- Para candidatos admitidos, mantener la similitud visual como criterio principal. Usar cercanía y señas descriptivas disponibles como apoyo de orden, sin asignar un puntaje ficticio a campos ausentes. Conservar el par de fotos que originó la sugerencia.
- El DAO sigue trayendo reportes elegibles. El servicio aplica el filtro y el controlador conserva el contrato de respuesta. Si no hay candidatos admitidos, devolver una lista vacía.

## 2. Aclarar el resultado en la vista

- Mostrar **«Posible coincidencia»** junto a la similitud visual y las dos fotos. Retirar de la vista el porcentaje combinado que compite con el porcentaje visual. Conservar la distancia y los datos descriptivos como contexto cuando estén disponibles.
- Mantener el puntaje combinado en la API mientras existan consumidores que lo usen. En la pantalla, explicar que las fotos deben compararse antes de contactar o confirmar.
- Cuando la lista esté vacía, mostrar **«Todavía no encontramos coincidencias visuales»** y conservar la confirmación de que el reporte se publicó.

## 3. Verificar y calibrar

| Caso | Resultado esperado |
|---|---|
| Alejo y Kinoto con 22 % visual, 60 % descriptivo y 0 km | Quedan fuera de las sugerencias. |
| Mismo perro con fotos de ángulos distintos, hallazgo sin nombre, raza ni color | Aparece si la evidencia visual supera el umbral. |
| Perros distintos de la misma raza o de distinto pelaje con ubicación cercana | La ubicación por sí sola no los admite. |
| La coincidencia pasa por una foto adicional | La interfaz muestra ese par de fotos y devuelve una sugerencia por reporte. |
| Búsqueda sin pareja, vectores incompatibles o candidatos bajo el umbral | Se devuelve una lista vacía cuando ninguno es elegible. |

Agregar pruebas de regresión en `backend/tests/test_pet_matching.py` y verificar el flujo de publicación y cotejo en el frontend. Comparar la regla anterior con la nueva en los mismos casos, incluyendo perros parecidos y búsquedas sin pareja. Fijar el umbral en validación y medir en perros reservados. Reportar precisión de sugerencias, cuántos perros se recuperan, cuántas búsquedas muestran resultados y falsos avisos por consulta sin pareja.

## 4. Activar con evidencia

Para habilitar por defecto una configuración de cotejo, exigir **al menos 80 % de sugerencias correctas en la prueba local reservada** para los escenarios de fotos que se habiliten. Fijar el tamaño mínimo de muestra y el piso de cobertura antes de abrir la prueba. El 80 % se calcula sobre las sugerencias mostradas y no equivale a un umbral de similitud visual del 80 %.

Validar la API y el formulario en una base temporal, con reportes antiguos y nuevos. Si se cambia de checkpoint, probar la reindexación de fotos principales y adicionales y documentar cómo volver a la versión anterior. Si el modelo no alcanza la precisión y la cobertura acordadas, conservarlo como experimental. [Plan de reentrenamiento](PLAN_REENTRENAMIENTO_DINOV2.md)

**Primera entrega.** Implementar la separación entre filtro visual y orden de candidatos, agregar la regresión Alejo–Kinoto y simplificar la pantalla. Después ejecutar la comparación con casos verificados para elegir el umbral y decidir qué configuración se puede activar.

## Estado de la primera entrega

El backend aplica un mínimo visual provisional de 35 % en la escala del cotejo anterior, configurable con `LEGACY_PET_VISUAL_THRESHOLD`. Los vectores versionados de DINOv2 conservan el umbral del checkpoint. En ambos casos, las señas y la distancia ordenan candidatos admitidos después de la similitud visual. La vista muestra el puntaje visual y conserva la confirmación de publicación si la búsqueda queda vacía.

El caso de Alejo se verificó en modo lectura en la base local. Kinoto quedó fuera de las sugerencias. La calibración con identidades locales verificadas y la evaluación del requisito de 80 % quedan pendientes. El mínimo provisional no representa una precisión medida.
