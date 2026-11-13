# Etiquetado de fotos para cotejo de perros

Asigná un `dog_id` anónimo por perro. Confirmá con el tutor o el refugio que las fotos corresponden al mismo animal y que se pueden usar para el proyecto. Usá el mismo `scene_id` para fotos de la misma sesión, ráfaga o video. Reuní fotos desde otros ángulos y en otros lugares o momentos. Evitá nombres de personas, direcciones y otros datos de contacto en el manifiesto.

Anotá los rasgos visibles y revisalos en más de una foto. Usá `negro`, `blanco`, `marron`, `crema` o `gris` para el color dominante. Anotá el secundario si se distingue y el patrón como `solido`, `bicolor`, `manchas`, `moteado` o `atigrado`. Dejá en blanco un dato dudoso. La raza es declarada, con opción de dejarla vacía. Registrá el ángulo y el encuadre por separado porque una foto de perfil puede mostrar el cuerpo entero.

El [lote piloto](../ml/datasets/reid_coats_pilot.tsv) contiene 24 perros de DogReID-1553, ocho por partición, revisados en dos imágenes por perro. Las etiquetas de prueba sirven solo para desglosar los resultados. El muestreador usa el color dominante de los perros de entrenamiento. Los campos secundario y patrón quedan registrados para revisar y ampliar el lote.

Para sumar fotos locales, prepará un JSON con rutas relativas al archivo. Cada perro de entrenamiento necesita al menos dos fotos. Para un perro de validación o prueba con pareja, asigná escenas distintas a consulta y galería. Para simular que no existe un reporte de pérdida, incluí perros que aparezcan solo en consulta. Los identificadores deben permanecer estables en todas las versiones.

```json
[
  {
    "image": "fotos/dog-001-frente.jpg",
    "dog_id": "dog-001",
    "scene_id": "sesion-a",
    "role": "train",
    "identity_verified": true,
    "authorized": true,
    "breed": "",
    "coat": "marron",
    "secondary": "blanco",
    "pattern": "manchas",
    "angle": "frente",
    "framing": "cuerpo_entero"
  }
]
```

Los roles son `train`, `val_query`, `val_gallery`, `test_query` y `test_gallery`. El constructor verifica que un perro no aparezca en dos particiones, que consulta y galería no compartan escena y que fotos duplicadas exactas no crucen identidades ni roles. La revisión de fotos casi idénticas e identidades repetidas entre fuentes se hace al incorporar datos.

## BA-26 · Inventario local

La base SQLite de desarrollo tiene 19 referencias a fotos de perros entre avisos y fichas REMUM. Tras deduplicar por SHA-256 quedan 12 fotos legibles. Cinco de ellas tienen más de una referencia. No hay fotos adicionales de reportes en esa base.

El inventario local `ml/datasets/_cache/reid-v2/ba26-candidatas-locales.json` registra las referencias para que el tutor o el refugio pueda confirmar cada identidad, sesión y autorización. Una foto repetida en un aviso y una ficha cuenta una sola vez. Pasar únicamente las fotos verificadas a un JSON de entrada como el del ejemplo y reservar los perros de prueba antes de preparar entrenamiento o validación. Las rutas de ese JSON se interpretan desde su propio directorio.
