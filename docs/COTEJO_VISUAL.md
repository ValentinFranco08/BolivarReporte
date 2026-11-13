# Cotejo de perros por foto

El clasificador multimodal sigue asignando categorías al reporte. El cotejo por identidad usa un ViT preentrenado y una proyección entrenada con Triplet Loss. La salida es un vector normalizado de 128 componentes. El backend compara fotos de perros aunque el reporte no incluya nombre, raza, color ni ubicación.

El formulario admite una foto principal y hasta tres adicionales. Los reportes anteriores conservan su foto principal. La búsqueda calcula la mayor similitud entre pares de fotos de dos reportes y devuelve una posible coincidencia por reporte. El umbral experimental se calibra con consultas de una sola foto. Antes de activar el modelo para uso general, conviene medir los falsos avisos con varias fotos por reporte y con perros locales fotografiados de cuerpo entero.

## Repetir el experimento

Descargar `DogFaceNet_224resized.zip` desde [Zenodo](https://zenodo.org/records/12578449). El MD5 publicado es `010c207e202bb499039452aa7363b015`. El archivo extraído contiene el directorio `after_4_bis`, con una carpeta por perro. La preparación separa los perros completos por conjunto, descarta duplicados idénticos dentro de una identidad y rechaza fotos idénticas con etiquetas contradictorias.

```bash
unzip DogFaceNet_224resized.zip -d ml/datasets/_cache/dogfacenet
venv/bin/python -m ml.training.reid \
  --dataset ml/datasets/_cache/dogfacenet/after_4_bis \
  --output ml/checkpoints/pet_reid/dogfacenet.pt --epochs 12 --batch-size 16
```

El comando guarda el checkpoint y un JSON con resultados. La referencia en ese JSON es el mismo ViT congelado sin proyección, sobre el mismo conjunto de prueba. El umbral se selecciona en validación con un objetivo de hasta 5 % de consultas sin pareja que generan sugerencias. Los resultados describen el conjunto DogFaceNet, que contiene caras recortadas.

## Probar la integración

Aplicar la migración con `make migrate`. Para activar el checkpoint, usar su ruta absoluta. El comando de reindexación regenera los vectores a partir de las fotos almacenadas. El backend compara vectores de una misma versión y mantiene el cotejo previo para los reportes que todavía tienen vectores del formato anterior.

```bash
export PET_REID_CHECKPOINT="$PWD/ml/checkpoints/pet_reid/dogfacenet.pt"
venv/bin/python backend/scripts/manage.py reindex
make backend
```

El nombre de versión incluye una huella del checkpoint. Si cambia el archivo, volver a ejecutar la reindexación. Para volver al cotejo anterior, desactivar `PET_REID_CHECKPOINT` y ejecutar `venv/bin/python backend/scripts/manage.py reindex --legacy`.

## Primer experimento

DogFaceNet aportó 8.363 fotos de 1.393 perros. Se usaron 1.115 perros para entrenamiento, 139 para validación y 139 para prueba. Los resultados de prueba están en [dogfacenet.json](../ml/checkpoints/pet_reid/dogfacenet.json).

| Métrica de prueba | ViT de referencia | Proyección entrenada |
|---|---:|---:|
| Perro correcto entre las primeras cinco sugerencias, sin umbral | 91,4 % | 95,7 % |
| Perro correcto entre las primeras cinco sugerencias y por encima del umbral | 44,3 % | 64,3 % |
| Avisos en consultas sin pareja | 1,4 % | 5,8 % |

La integración HTTP se verificó con dos fotos diferentes de un perro reservado para prueba, con el reporte de hallazgo sin nombre, raza ni color. El experimento usa caras alineadas. Queda pendiente validar el recorte automático y el desempeño con fotos locales de cuerpo entero antes de habilitar el checkpoint por defecto.

## Fotos de cuerpo entero y reportes con varias fotos

El experimento usa los recortes de [DogReID-1553](https://doi.org/10.7910/DVN/LVTRLG) (CC0 1.0). Conserva la prueba abierta oficial, en la que las fotos de consulta y de galería para un mismo perro proceden de escenas distintas. Se reservan 120 perros del conjunto oficial de entrenamiento para elegir la época y los umbrales. En [Multi-pose Dog Dataset](https://data.mendeley.com/datasets/v5j6m8dzhv/1) (Zhimin He, 2023, CC BY 4.0) se usan las carpetas oficiales de consulta y galería. Se omite de la galería la mitad de las identidades para medir los avisos cuando el perro buscado está ausente.

Cada consulta simula un hallazgo con una foto. La galería simula un reporte por perro con hasta 1, 3 o 4 fotos, según la prueba. Cada perro cuenta una vez en el ranking y recibe la mayor similitud entre sus fotos y la consulta. Los umbrales se ajustan por cantidad de fotos en validación de DogReID y se aplican a las dos pruebas. El checkpoint exportado usa el umbral de una foto. Las métricas de varias fotos son experimentales.

Descomprimir `Images.zip` y `MPDD.zip` en `ml/datasets/_cache/reid_sources/` y guardar allí `splits.tab`, publicado en Dataverse como `splits.csv`. Ejecutar desde la raíz con el entorno virtual activo.

```bash
python -m ml.training.reid_body \
  --images ml/datasets/_cache/reid_sources/Images \
  --splits ml/datasets/_cache/reid_sources/splits.tab \
  --mpdd ml/datasets/_cache/reid_sources/MPDD/pytorch \
  --reference ml/checkpoints/pet_reid/dogfacenet.pt \
  --output ml/checkpoints/pet_reid/dogreid.pt
```

Con la proyección entrenada en DogReID-1553, al pasar de una foto a hasta tres por reporte, los aciertos entre las primeras cinco sugerencias por encima del umbral pasaron de 3,1 % a 6,0 % en la prueba abierta de DogReID y de 54,7 % a 83,0 % en MPDD. Los avisos en consultas sin pareja pasaron de 17,4 % a 28,0 % en DogReID y se mantuvieron en 33,3 % en MPDD. El objetivo de hasta 5 % aplicado en validación no se sostuvo fuera de ese conjunto. Cada escenario usa su propio umbral de validación.

Los [resultados completos](../ml/checkpoints/pet_reid/dogreid.json) incluyen las comparaciones con ViT congelado y DogFaceNet. El checkpoint `dogreid.pt` queda disponible para experimentar. Las tasas de falsos avisos y los pocos aciertos en la prueba abierta de DogReID impiden recomendar su activación por defecto.

## Comparación con DINOv2

`reid_compare` usa los mismos conjuntos de DogReID y MPDD. Mantiene congelado DINOv2 Small y entrena la proyección con Triplet Loss. El muestreo prioriza fotos del mismo perro en escenas distintas y agrupa perros distintos de la misma raza. La opción `--coats` admite un TSV con columnas `DOG_ID` y `COAT` para incorporar perros de raza distinta y pelaje parecido. El experimento publicado no contó con etiquetas de pelaje.

```bash
python -m ml.training.reid_compare \
  --source ml/datasets/_cache/reid_sources \
  --encoder ml/datasets/_cache/dinov2-small \
  --output ml/checkpoints/pet_reid/dinov2-dogreid.pt

python -m ml.evaluation.reid_crops \
  --source ml/datasets/_cache/reid_sources \
  --checkpoint ml/checkpoints/pet_reid/dinov2-dogreid.pt \
  --detector ml/datasets/_cache/detectors/ssdlite.pth \
  --output ml/checkpoints/pet_reid/dinov2-crops.json
```

Los pesos base corresponden a [DINOv2 Small](https://huggingface.co/facebook/dinov2-small). El detector experimental usa SSDLite de TorchVision con pesos COCO. Los resultados de recorte usan una muestra de 64 identidades en la galería por partición y 48 consultas sin pareja. El recorte automático se aplica si se detecta exactamente un perro con puntaje de al menos 0,45. En los demás casos se compara la foto completa. Las métricas de esta muestra se comparan entre sí, ya que su galería es más pequeña que la de la prueba abierta completa.

En la prueba completa DogReID con hasta tres fotos, DINOv2 entrenado obtuvo 42,9 % de aciertos en el top 5 antes del umbral, frente al 20,2 % del ViT entrenado anterior. Con el umbral calibrado en validación, obtuvo 11,5 % de aciertos y 11,8 % de falsos avisos, frente a 6,0 % y 28,0 % respectivamente. En MPDD, los aciertos pasaron de 83,0 % a 86,8 % y los falsos avisos de 33,3 % a 13,7 %. El objetivo de falsos avisos de 5 % todavía no se sostiene en la prueba completa.

El checkpoint experimental carga desde la API y se verificó la reindexación en SQLite temporal. Para una prueba local se puede configurar `PET_REID_CHECKPOINT` con la ruta de `dinov2-dogreid.pt`. El checkpoint exportado utiliza el umbral de una foto. La comparación por cantidad de fotos calibra umbrales separados en validación. Queda pendiente validar el efecto de distintos tamaños de galería y fotos locales antes de habilitar el modelo por defecto.

[Resultados de DINOv2](../ml/checkpoints/pet_reid/dinov2-dogreid.json) · [Recortes ViT](../ml/checkpoints/pet_reid/dogreid-crops.json) · [Recortes DINOv2](../ml/checkpoints/pet_reid/dinov2-crops.json)

En la muestra de recortes con hasta tres fotos por reporte, DINOv2 pasó de 73,4 % en el top 5 con la foto completa a 81,2 % con recorte automático y 92,2 % con recorte anotado, antes del umbral. Con el umbral, el recorte automático obtuvo 12,5 % de aciertos y 4,2 % de falsos avisos. La foto completa obtuvo 10,9 % y 6,2 %. El detector produjo un recorte para 146 de las 254 fotos de prueba.

## Criterio de precisión para el cotejo

La precisión mínima es 80 %. Se calcula dividiendo las sugerencias correctas por todas las sugerencias mostradas, hasta seis por consulta como en la API. Las consultas sin pareja también cuentan. Si no hay sugerencias, la precisión queda indefinida. Para esta primera evaluación se usan al menos 20 sugerencias por escenario para evitar aprobar con unos pocos casos.

El evaluador mide el checkpoint con su umbral actual y busca un umbral alternativo usando solo validación. Entre los umbrales que alcanzan el objetivo, elige el que recupera más coincidencias correctas. Luego mide por separado la precisión, la cobertura, la recuperación entre los primeros cinco y los falsos avisos en la prueba reservada y en MPDD. La prueba de una foto de hallazgo contra hasta una, tres o cuatro fotos de referencia se informa por separado.

```bash
python -m ml.evaluation.reid_precision \
  --source ml/datasets/_cache/reid_sources \
  --checkpoint ml/checkpoints/pet_reid/dinov2-dogreid.pt \
  --output ml/checkpoints/pet_reid/dinov2-precision.json \
  --minimum 0.8
```

El checkpoint DINOv2 actual no cumple el requisito. Con una foto de referencia obtuvo 108 aciertos entre 432 sugerencias en DogReID (25,0 %) y 38 entre 62 en MPDD (61,3 %). Con hasta tres fotos obtuvo 166 entre 837 (19,8 %) y 47 entre 98 (48,0 %), respectivamente. En validación, ningún umbral alcanzó 80 % con al menos 20 sugerencias para los escenarios medidos. Ver [resultados de precisión](../ml/checkpoints/pet_reid/dinov2-precision.json).

## Reentrenamiento desde un manifiesto versionado

El [plan de reentrenamiento](PLAN_REENTRENAMIENTO_DINOV2.md) fija el 80 % de precisión. La [guía de etiquetado](ETIQUETADO_COTEJO.md) describe cómo preparar el archivo local y el lote piloto. Los comandos generan un manifiesto con hashes de las imágenes y comparan dos proyecciones de DINOv2, entrenadas con fotos completas o con recorte automático. Si el detector encuentra exactamente un perro con puntaje de al menos 0,45, se usa su recorte con margen. En los demás casos se usa la foto completa. El predictor aplica la misma regla cuando el checkpoint declara un detector.

```bash
python -m ml.data.reid_manifest \
  --source ml/datasets/_cache/reid_sources \
  --coats ml/datasets/reid_coats_pilot.tsv \
  --output ml/datasets/_cache/reid-v2/manifest-labeled.json

python -m ml.training.reid_v2 \
  --manifest ml/datasets/_cache/reid-v2/manifest-labeled.json \
  --encoder ml/datasets/_cache/dinov2-small \
  --detector ml/datasets/_cache/detectors/ssdlite.pth \
  --output-dir ml/checkpoints/pet_reid
```

El constructor admite `--local` para el JSON de fotos locales verificadas. La corrida pública queda como experimento. La aprobación para uso general requiere la prueba local reservada y el criterio de cobertura del plan.

La primera corrida procesó 7.805 fotos y ajustó dos proyecciones con 3.090 fotos de entrenamiento, incluyendo el lote piloto de pelaje. Con recorte automático y hasta tres fotos de referencia, el umbral calibrado dio 81,8 % en validación (18/22), 84,8 % en MPDD (39/46) y 35,0 % en DogReID de escenas distintas (106/303). La variante de foto completa y el escenario de una foto con recorte no alcanzaron 80 % con al menos 20 sugerencias en validación. Los dos checkpoints son experimentales y conservan el umbral elegido por falsos avisos durante entrenamiento. Los umbrales calibrados por precisión se informan por separado y no se aplicaron a la API.

El resultado de MPDD no se sostuvo en DogReID. La prueba local permanece pendiente. El subconjunto de distinta raza y mismo color incluyó solo 29 pares en la prueba pública, insuficientes para sacar una conclusión por pelaje. [Informe de la corrida](../ml/checkpoints/pet_reid/dinov2-v2.json)

## BA-27 · Decisión de activación

**Estado.** Pendiente de la muestra local verificada de BA-26. DINOv2 v2 con recorte automático sigue en evaluación. El informe registra 0 fotos locales. Los porcentajes de la tabla provienen de pruebas públicas con hasta tres fotos de referencia y el umbral calibrado en validación.

| Conjunto | Precisión (aciertos / sugerencias) | Cobertura | Recuperación con umbral (top 5) | Falsos avisos en consultas sin pareja |
| --- | ---: | ---: | ---: | ---: |
| MPDD | 84,8 % (39/46) | 40,4 % | 73,6 % | 5,9 % |
| DogReID | 35,0 % (106/303) | 9,6 % | 8,2 % | 6,4 % |

**Propuesta para acordar antes de abrir la prueba local.** Reservar 120 perros verificados, con una consulta por perro. Incluir al menos 60 consultas con pareja y 60 sin pareja, con perros de pelaje similar y de la misma raza o mestizos. Para medir una y hasta tres fotos de referencia sobre las mismas consultas, preparar tres fotos de galería por perro con pareja, de sesiones distintas de la consulta. Presentar cada hallazgo con una foto, sin raza, nombre ni color declarado.

Por modalidad, exigir al menos 80 % de precisión, 30 sugerencias y 25 % de cobertura (consultas con alguna sugerencia sobre el total). Fijar la versión del checkpoint, los filtros del backend y el umbral con datos de validación antes de abrir el conjunto reservado. Registrar también cuántas consultas con pareja recuperan al perro correcto y cuántas consultas sin pareja reciben algún aviso.

Si una modalidad cumple, verificar en una base temporal la reindexación y el regreso al cotejo anterior antes de habilitarla por defecto. La activación requiere que la API aplique la misma configuración evaluada.

### Piloto en el entorno de desarrollo

En este entorno se habilitó `dinov2-v2-automatic.pt` mediante `PET_REID_CHECKPOINT` en `backend/.env`. La ruta del archivo de configuración es relativa a la raíz del proyecto. Una variable de entorno explícita tiene precedencia. El piloto usa el umbral incorporado al checkpoint (0,7213) y permite revisar el flujo con avisos reales del entorno de desarrollo.

Se reindexaron 15 avisos en la base SQLite de desarrollo y se comprobó que la API de cotejo respondió a los 15. En una copia temporal, la reversión recuperó los vectores anteriores de 768 componentes. BA-27 mantiene pendiente la evaluación de precisión con las fotos verificadas de BA-26.

Para volver al cotejo anterior en desarrollo, dejar `PET_REID_CHECKPOINT=` en `backend/.env`, ejecutar el siguiente comando desde la raíz y reiniciar el backend.

```bash
DATABASE_URL="sqlite:///$PWD/backend/bolivar_dev.db" \
  venv/bin/python backend/scripts/manage.py reindex --legacy
```

### Demostración del cotejo para el profesor

1. Abrí la cartelera local, buscá el aviso perdido de **Renato** y pulsá **Coincidencias**.
2. Entre los avisos para revisar aparecen los hallazgos #27 (71,4 % de similitud visual) y #25 (54,7 %). El umbral de posible coincidencia del piloto es 72,1 %.
3. Compará las fotos lado a lado. El aviso de revisión permite inspeccionar las señas. Las acciones de contacto y confirmación están disponibles en los candidatos que superan el umbral, según los datos y la sesión del usuario.

Para explicar el recorrido, el controlador de reportes solicita el cotejo a `MatchingService`. El DAO obtiene los avisos elegibles y `MatchingPolicy` compara los vectores de DINOv2 de la misma versión. El comparador muestra hasta tres avisos para revisión manual desde 50 % de similitud visual y por debajo del umbral del modelo, después de aplicar los filtros habituales. La precisión del 80 % se mide sobre sugerencias correctas en una muestra reservada y sigue pendiente en BA-27.
