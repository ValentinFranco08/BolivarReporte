# Plan de reentrenamiento de DINOv2 para el cotejo de perros

**Objetivo.** Una persona sube una foto de un perro encontrado y puede recibir una sugerencia de coincidencia aunque desconozca su nombre, raza y color. El modelo debe distinguir individuos cuando cambian el ángulo, la postura, la luz o el fondo. Para activar un nuevo checkpoint por defecto, **al menos el 80 % de las sugerencias mostradas debe corresponder al mismo perro** en pruebas reservadas.

## Punto de partida

DINOv2 Small ya funciona con el predictor de la API. Se entrenó una proyección con 3.090 fotos de 625 perros y se evaluó con identidades separadas. El checkpoint actual tiene estos resultados con el umbral que usa el backend.

| Fotos en el reporte de pérdida | DogReID, escenas distintas | MPDD, distintas posturas |
|---|---:|---:|
| Una | 25,0 % de precisión (108/432) | 61,3 % (38/62) |
| Hasta tres | 19,8 % (166/837) | 48,0 % (47/98) |

En la validación anterior, ningún umbral alcanzó 80 % con al menos 20 sugerencias. El recorte automático mejoró el ranking en una muestra pequeña, por lo que se probará en el conjunto ampliado antes de elegirlo como preprocesamiento. [Auditoría actual](../ml/checkpoints/pet_reid/dinov2-precision.json) · [Guía de cotejo](COTEJO_VISUAL.md)

## 1. Ampliar el dataset y fijar las particiones

- Usar la partición oficial de entrenamiento de DogReID-1553 como base. Reunir fotos locales autorizadas con refugios, rescatistas y tutores. Priorizar mestizos, perros parecidos entre sí y fotos de celular de cuerpo entero, cara y perfil, tomadas en sesiones distintas. [DogReID-1553](https://doi.org/10.7910/DVN/LVTRLG)
- Proponer un primer lote local de **100 perros con 4–6 fotos por perro en al menos dos sesiones**. Es una meta inicial de recolección. Ampliar las identidades y los escenarios donde queden pocos casos para medir o se concentren los errores.
- Reservar perros completos para validación y prueba. Mantener la prueba oficial de DogReID y MPDD como referencias. Crear también una prueba local nueva, cerrada antes de entrenar. Dentro de cada prueba, las fotos de consulta y galería del mismo perro deben proceder de sesiones distintas. [MPDD](https://data.mendeley.com/datasets/v5j6m8dzhv/1)
- Detectar duplicados exactos, fotos casi idénticas y posibles identidades repetidas entre fuentes antes de separar los conjuntos. Agrupar fotos de ráfagas y fotogramas del mismo video en una sesión. Registrar la procedencia y las condiciones de uso.

**Entregable.** Un manifiesto versionado y un informe con cantidades de perros, fotos y sesiones por fuente y partición. Guardar las imágenes fuera de Git.

## 2. Etiquetar y revisar los ejemplos

| Dato | Nivel | Uso |
|---|---|---|
| `dog_id` y estado de verificación | Perro | La identidad confirmada define qué fotos pertenecen al mismo animal. Revisar los casos dudosos antes de usarlos como positivos. |
| `scene_id` y fuente | Foto | Formar pares de sesiones distintas y detectar repeticiones. |
| Ángulo, encuadre y calidad | Foto | Identificar frente, perfil, cuerpo entero, desenfoque u oclusión para auditar errores. |
| Color principal, secundario y patrón | Perro, con evidencia visible en fotos | Elegir perros distintos con pelaje parecido. Usar un vocabulario común con valores como negro, blanco, marrón, manchas, atigrado y «no determinable». |
| Raza declarada o «desconocida» | Perro | Seleccionar perros distintos de la misma raza. Registrar mestizo cuando se conozca y conservar la procedencia de la etiqueta. |
| Región del perro, cuando esté disponible | Foto | Comparar recortes anotados con los automáticos y revisar detecciones dudosas. |

Preparar una muestra revisada de pelaje en entrenamiento, validación y prueba, con identidades separadas. Exportar `DOG_ID` y `COAT` desde el manifiesto para el muestreador existente. Las etiquetas de raza y pelaje son auxiliares durante el entrenamiento. En la app alcanza una foto para iniciar el cotejo.

**Entregable.** Guía corta de etiquetado, manifiesto validado y un lote revisado de pares difíciles de misma raza y de distinta raza con pelaje similar.

## 3. Reentrenar DINOv2 y comparar variantes

1. Reproducir la referencia actual en el protocolo de evaluación fijado. Registrar la semilla, el manifiesto, los pesos base y la configuración.
2. Comparar foto completa, recorte anotado y recorte automático en validación. Usar el recorte anotado para estimar cuánto podría aportar un buen detector. Definir cómo se procesa una foto sin detección válida o con varios perros y aplicar la misma regla en validación, prueba e inferencia.
3. Entrenar primero la proyección con DINOv2 congelado. Priorizar positivos del mismo perro entre escenas y negativos de perros distintos con la misma raza o pelaje parecido. Comparar contra el mismo modelo entrenado sin esa selección de ejemplos para medir el aporte de las etiquetas.
4. Si la proyección se estanca en validación, probar el ajuste de los últimos bloques de DINOv2 con una tasa de aprendizaje baja. Elegir la variante por su capacidad para encontrar más coincidencias correctas al nivel de precisión requerido. Seleccionar el modelo, el recorte y el umbral antes de abrir la prueba local.

**Entregable.** Checkpoints versionados con el extractor, la proyección, el preprocesamiento y su configuración. Guardar por separado las métricas de cada variante.

## 4. Calibrar y verificar el 80 % de precisión

Medir la **precisión de sugerencias** como sugerencias correctas divididas por el total de sugerencias que vería el usuario. Una consulta sin pareja aporta falsos positivos si muestra algún perro. Si no se muestra ninguna sugerencia, la precisión queda indefinida.

- Reproducir el flujo de la API con una foto de hallazgo, hasta seis sugerencias y reportes de pérdida de hasta una, tres o cuatro fotos. Incluir perros ausentes, perros parecidos, distintas posturas y galerías de distintos tamaños. Definir el tamaño de galería y la proporción de consultas sin pareja representativos del uso local antes de abrir la prueba.
- Calibrar en validación cómo combinar varias fotos y qué umbral aplicar. Comparar la regla del par más parecido con una que tenga en cuenta la cantidad de fotos comparadas. Congelar la regla y usarla en la evaluación y el backend.
- Informar precisión, número de sugerencias, cobertura, porcentaje de búsquedas con pareja que encuentran al perro correcto y falsos avisos por consulta sin pareja. Desglosar misma raza, distinto pelaje y distinta raza con pelaje similar. Reportar el tamaño de cada grupo y la incertidumbre agrupando por perro para tener en cuenta las fotos repetidas de un mismo individuo.
- **Criterio de activación.** Alcanzar al menos 80 % de precisión en la prueba local reservada para cada modalidad de fotos que se quiera habilitar. Mantener los resultados públicos de DogReID y MPDD como comprobaciones externas y explicar cualquier caída. El mínimo de 20 sugerencias por escenario del evaluador actual sirve como filtro preliminar. Fijar un tamaño de muestra y un piso de cobertura de aceptación antes de evaluar la versión final. Entre los modelos que cumplan, elegir el que recupere más perros.

**Entregable.** Informe con conteos, métricas, umbrales y una decisión explícita de si el checkpoint cumple. Si queda por debajo del objetivo, usar los errores para planificar otra ronda y reservar una prueba nueva para la siguiente decisión.

## 5. Integrar el checkpoint que cumpla

- Reutilizar la separación MVC + Service + DAO. `ml/` genera los vectores, `MatchingService` aplica la regla validada y el DAO consulta los reportes candidatos. Exportar la versión del extractor, el preprocesamiento y la configuración de umbrales que se evaluó.
- Probar la reindexación de fotos principales y adicionales en una base temporal. Verificar que se comparen vectores de la misma versión y que un reporte antiguo siga disponible después de reindexar.
- Verificar el flujo completo con un hallazgo sin nombre, raza ni color y una pérdida con fotos desde otros ángulos. Comprobar también una búsqueda sin pareja, un perro distinto de la misma raza, el par de fotos que muestra la interfaz y el tiempo de respuesta.
- Habilitar el checkpoint cuando se cumpla el criterio de precisión y cobertura. Conservar el checkpoint anterior y documentar cómo reindexar al volver a esa versión.

**Primera entrega de implementación.** Preparar el manifiesto de DogReID y de la muestra local, fijar las particiones, revisar el primer lote de etiquetas de pelaje y ejecutar la comparación reproducible de DINOv2 con fotos completas y recortadas. Los resultados de esa entrega indicarán qué ejemplos conviene sumar antes del entrenamiento definitivo.

## Estado de la primera entrega

El constructor de manifiestos y el entrenamiento reproducible ya están implementados. El manifiesto público se generó con 7.805 fotos de DogReID-1553 y MPDD, organizadas por identidad, escena cuando está disponible y rol. Se revisaron 48 fotos para registrar el pelaje de 24 perros de DogReID, con ocho perros en cada partición. Ver la [guía de etiquetado](ETIQUETADO_COTEJO.md) y los [comandos del experimento](COTEJO_VISUAL.md#reentrenamiento-desde-un-manifiesto-versionado).

La incorporación de fotos locales, su revisión de identidad y la evaluación de aceptación dependen de contar con fotos autorizadas y etiquetadas. La auditoría local se informa separada de DogReID y MPDD.
