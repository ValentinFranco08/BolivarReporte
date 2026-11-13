# Bolívar Animal · Tablero de Trello

**Descripción del tablero.** Plataforma vecinal de San Carlos de Bolívar para publicar y consultar avisos sobre animales, cotejar fotos, registrar mascotas en REMUM y gestionar casos desde el panel operativo. La IA sugiere categorías y posibles coincidencias que una persona puede revisar.

**Listas sugeridas.** Producto y alcance · Implementado · Experimentos de IA · Pendiente. Cada título BA identifica una tarjeta. Copiá la descripción y los criterios a la tarjeta y usá los elementos de **Aceptación** como checklist. Los pasos principales y alternativos son casos de uso o, para trabajo técnico, casos de prueba. Una tarjeta implementada describe una función disponible en el código, sin implicar que todos sus criterios tengan una prueba automatizada.

**Etiquetas.** Reportes · Cotejo · REMUM · Operación · IA · Arquitectura · QA.

## Lista Producto y alcance

### BA-00 · Objetivo, actores y recorrido de la aplicación

**Descripción.** Centralizar avisos de pérdida, hallazgo, tránsito, adopción y alerta de cebo. Vincular vecinos y tutores mediante avisos, fotos y fichas REMUM.

**Actores.** Vecino que publica o consulta, tutor, operador de Zoonosis y persona que mantiene la aplicación y sus modelos.

**Recorrido de demo.** Publicar un hallazgo con una foto → consultar posibles coincidencias → comparar fotos → registrar o resolver el caso según corresponda → consultar la cartelera. Como recorrido independiente, generar y consultar una credencial REMUM por código.

**Aceptación**

- [ ] La presentación distingue clasificación del reporte, similitud visual entre animales y confirmación humana del reencuentro.
- [ ] La presentación identifica qué está implementado, qué se probó en experimentos y qué falta validar.

## Lista Implementado

### BA-01 · Crear cuenta e iniciar sesión · Operación

**Caso de uso.** Un vecino se registra con nombre, correo y contraseña. Inicia sesión y la aplicación identifica al usuario mediante su token. Si las credenciales son incorrectas, se muestra un error y se conserva el formulario.

**Aceptación**

- [ ] Las credenciales válidas permiten iniciar sesión y consultar la identidad autenticada.
- [ ] Una credencial inválida no crea una sesión y un correo ya registrado no crea otra cuenta con ese correo.
- [ ] La aplicación permite cerrar sesión.

**Evidencia.** `backend/tests/test_main.py`, rutas `/registro` y `/login`.

### BA-02 · Publicar pérdida, hallazgo, tránsito o adopción · Reportes

**Caso de uso.** Un vecino elige el tipo de aviso, adjunta una foto y publica. Puede agregar señas y datos de contacto si los conoce. En un hallazgo puede desconocer el nombre, la raza y el pelaje.

**Aceptación**

- [ ] El formulario exige una foto y muestra su vista previa.
- [ ] Un hallazgo con foto y sin nombre, raza ni color puede publicarse.
- [ ] Tras guardar, se muestra la confirmación. Si falla la publicación, se informa el error.
- [ ] El reporte queda disponible para consultarlo en la cartelera.

**Evidencia.** `frontend/app/reportes/nuevo/page.tsx`, `POST /api/reports`, `frontend/__tests__/nuevo-reporte.test.tsx`.

### BA-03 · Adjuntar varias fotos · Reportes

**Caso de uso.** Un vecino adjunta la foto principal y agrega otras tomas de perfil o cuerpo entero. Puede quitar las adicionales antes de publicar.

**Aceptación**

- [ ] Se admite una foto principal y hasta tres adicionales.
- [ ] La API rechaza una solicitud que supera el límite y devuelve las fotos asociadas al reporte creado.
- [ ] Un aviso anterior de una sola foto sigue disponible.

**Evidencia.** `ReportSubmission`, `ReportPhoto` y migración `f26d90a115aa`.

### BA-04 · Consultar cartelera y mapa · Reportes

**Caso de uso.** Un vecino abre el listado de reportes o el mapa y consulta los avisos de la zona. Puede filtrar el listado y abrir una ficha para ver sus datos.

**Aceptación**

- [ ] La cartelera muestra los reportes guardados y permite filtrar las vistas que ofrece la aplicación.
- [ ] El mapa representa los reportes con coordenadas disponibles.
- [ ] La ficha muestra la foto y los datos publicados del aviso.

**Evidencia.** `/reportes`, `/mapa` y `GET /api/reports`.

### BA-05 · Cargar ubicación en un reporte · Reportes

**Caso de uso.** El vecino solicita su ubicación desde el formulario. Si el navegador la entrega, el formulario actualiza las coordenadas y busca una dirección legible. El vecino puede editar la dirección.

**Aceptación**

- [ ] El formulario permite solicitar la ubicación y editar la dirección.
- [ ] Si el GPS falla o se deniega, se libera el estado de búsqueda y el formulario sigue utilizable.
- [ ] El reporte conserva la dirección y las coordenadas enviadas.

**Evidencia.** `frontend/controllers/useNuevoReporte.ts`, `frontend/lib/api.ts`.

### BA-06 · Clasificar la situación a partir de foto y texto · IA

**Caso de uso.** Al publicar, el sistema procesa la foto y la descripción en español y propone una categoría de situación. El flujo registra la predicción asociada cuando hay una versión del modelo configurada.

**Aceptación**

- [ ] La API acepta foto y texto y devuelve los resultados del análisis cuando el predictor está disponible.
- [ ] La publicación registra la clase y el puntaje de la predicción cuando corresponde.
- [ ] Una falla de análisis informa el error y no deja una foto guardada por esa solicitud fallida.

**Evidencia.** `POST /api/ai/predict`, `ClassificationService` y pruebas de arquitectura.

### BA-07 · Buscar posibles coincidencias por foto · Cotejo

**Caso de uso.** Después de publicar una pérdida, hallazgo o tránsito, el vecino consulta reportes compatibles. La búsqueda compara vectores visuales y devuelve candidatos para revisión.

**Aceptación**

- [ ] La búsqueda excluye el propio reporte y los reportes resueltos.
- [ ] Puede comparar dos avisos del mismo tipo elegible y puede funcionar si faltan nombre, raza, color o ubicación.
- [ ] Devuelve hasta seis candidatos y una lista vacía cuando ninguno supera el filtro.
- [ ] Los vectores experimentales solo se comparan si corresponden a la misma versión.

**Evidencia.** `GET /api/reports/{id}/matches` y `backend/tests/test_pet_matching.py`.

### BA-08 · Exigir evidencia visual antes de sugerir · Cotejo

**Caso de prueba.** Alejo y Kinoto comparten ubicación pero su similitud visual es de aproximadamente 22 %. Un segundo caso presenta alta similitud visual y poca información textual.

**Aceptación**

- [ ] Alejo y Kinoto quedan fuera con el mínimo provisional de 35 % del cotejo anterior.
- [ ] Cercanía y señas descriptivas solo ayudan a ordenar candidatos admitidos.
- [ ] Un candidato con evidencia visual suficiente puede aparecer aunque falten datos descriptivos.
- [ ] La configuración distingue el umbral del cotejo anterior y el umbral del checkpoint versionado.

**Evidencia.** `MatchingPolicy`, `LEGACY_PET_VISUAL_THRESHOLD` y regresión de baja similitud visual.

### BA-09 · Descartar colores de pelaje incompatibles · Cotejo

**Caso de prueba.** Un hallazgo «negro» recibe candidatos «dorado», «marrón», «blanco», «negro con manchas blancas» y sin color.

**Aceptación**

- [ ] Negro frente a dorado, marrón o blanco se descarta si ambas descripciones son claras y no comparten color.
- [ ] Negro y negro con manchas blancas, color ausente o texto ambiguo siguen al cotejo por foto.
- [ ] La coincidencia en «mestizo» no cambia el descarte.

**Evidencia.** `backend/app/services/coat_color.py` y pruebas de reporte antiguo y vector versionado.

### BA-10 · Revisar sugerencias en el comparador · Cotejo

**Caso de uso.** El vecino revisa las dos fotos, avanza entre candidatos y decide si contactar. Si la búsqueda queda vacía, la publicación sigue confirmada.

**Aceptación**

- [ ] El comparador muestra un porcentaje de similitud visual y presenta las sugerencias como posibles coincidencias.
- [ ] Si la respuesta identifica una foto adicional como el mejor par, se muestra esa foto.
- [ ] La vista muestra «Todavía no encontramos coincidencias visuales» tras una búsqueda exitosa sin candidatos.
- [ ] Se ofrece contacto por WhatsApp cuando el reporte trae un teléfono.

**Evidencia.** `VisualMatchModal.tsx`, prueba de publicación con y sin coincidencias.

### BA-11 · Registrar la resolución de un aviso · Reportes

**Caso de uso.** La API recibe una solicitud autenticada para resolver un aviso. El panel permite actualizar el estado del reporte. El comparador incluye un botón de confirmación, cuyo flujo de sesión debe verificarse en BA-25.

**Aceptación**

- [ ] Una resolución exitosa devuelve el estado resuelto.
- [ ] El aviso resuelto deja de ser candidato de nuevas búsquedas.
- [ ] Si el servicio rechaza la actualización, el comparador informa el error.

**Evidencia.** `PATCH /api/reports/{id}/resolve` y prueba del flujo de coincidencias.

### BA-12 · Registrar una mascota y generar su QR · REMUM

**Caso de uso.** El tutor completa la ficha de su mascota. El registro guarda el nombre, especie y datos opcionales, y genera un código único. El tutor puede consultar sus mascotas.

**Aceptación**

- [ ] La ficha creada queda vinculada al usuario correspondiente y trae un código QR único.
- [ ] El listado personal muestra las fichas del usuario autenticado.
- [ ] Se conservan las coordenadas si el registro las incluye.

**Evidencia.** `/remum/nuevo`, `RemumService` y prueba de creación con coordenadas.

### BA-13 · Consultar y escanear una credencial · REMUM

**Caso de uso.** El vecino abre el escáner o la URL de la credencial y consulta la ficha de la mascota por código.

**Aceptación**

- [ ] Un código registrado abre su ficha pública.
- [ ] Un código inexistente devuelve un resultado de ficha no encontrada.
- [ ] Se puede comprobar el flujo en el navegador con una credencial de prueba.

**Evidencia.** `/remum/escanear`, `/qr/[id]` y `GET /api/remum/{qr_code_id}`. La vinculación del contacto real queda en BA-25.

### BA-14 · Gestionar mascotas comunitarias, padrinos y salud · REMUM

**Caso de uso.** Un vecino consulta fichas comunitarias. Una persona autenticada registra un evento de salud o agrega un padrino a una mascota comunitaria.

**Aceptación**

- [ ] El listado comunitario devuelve las fichas marcadas como comunitarias.
- [ ] La API registra eventos de salud asociados a una ficha válida.
- [ ] Agregar padrinos requiere sesión y se rechaza en fichas no comunitarias.

**Evidencia.** `RemumService` y rutas REMUM `/comunitarios`, `/salud` y `/padrinos`.

### BA-15 · Emitir una alerta de extravío desde REMUM · REMUM

**Caso de uso.** El tutor o administrador activa la alerta desde una ficha. El sistema marca al animal como extraviado y crea un reporte de pérdida. Si la solicitud incluye coordenadas, las usa en el reporte.

**Aceptación**

- [ ] La ficha y el reporte quedan actualizados en una misma transacción.
- [ ] Una persona ajena al registro, sin rol administrador, no puede emitir la alerta.
- [ ] Si se deniega la solicitud, no se crea un reporte ni se cambia el estado de la ficha.

**Evidencia.** `POST /api/remum/{qr_code_id}/alerta` y `test_remum_denied_alert_does_not_modify_data`.

### BA-16 · Publicar y consultar alertas de cebo · Reportes

**Caso de uso.** El vecino publica un aviso de alerta de cebo con evidencia y ubicación. Otros vecinos consultan avisos ubicados en el mapa. Desde SOS se puede abrir el formulario de alerta e imprimir el recurso de denuncia.

**Aceptación**

- [ ] El formulario permite publicar el tipo «alerta de cebo».
- [ ] La API de alertas activas devuelve únicamente alertas de cebo no resueltas.
- [ ] La pantalla SOS enlaza al formulario de alerta y ofrece un recurso de denuncia imprimible.

**Evidencia.** `/sos`, `/mapa` y `GET /api/alerts/active`.

### BA-17 · Revisar reportes en el panel operativo · Operación

**Caso de uso.** El operador abre el panel, filtra avisos, revisa una ficha y modifica su estado o prioridad. También puede revisar la predicción asociada.

**Aceptación**

- [ ] El panel muestra avisos con estado y prioridad.
- [ ] Los cambios guardados se ven al volver a consultar el aviso.
- [ ] Una actualización rechazada se informa en pantalla.

**Evidencia.** `/dashboard` y `PATCH /api/reports/{id}`. La verificación de permisos por rol queda en BA-25.

### BA-18 · Validar o fusionar categorías sugeridas · Operación

**Caso de uso.** El operador revisa las categorías pendientes y decide aprobar una o fusionarla con una existente.

**Aceptación**

- [ ] La aprobación actualiza la categoría y su estado de verificación.
- [ ] La fusión reasigna los reportes y combina los centroides compatibles.
- [ ] Si falla la fusión, los cambios se revierten como una sola operación.

**Evidencia.** `/api/admin/categories` y pruebas de categorías y transacciones.

### BA-19 · Registrar feedback y preparar reentrenamiento · IA

**Caso de uso.** El operador confirma una predicción o indica la clase correcta. Mantenimiento puede exportar el feedback y ejecutar el entrenamiento incremental con ejemplos históricos.

**Aceptación**

- [ ] El feedback queda asociado a la predicción y una corrección posterior actualiza el registro.
- [ ] Se pueden exportar los datos para el entrenamiento incremental.
- [ ] El comando admite una prueba sin entrenamiento y marca el feedback procesado después de guardar un checkpoint.

**Evidencia.** `FeedbackService`, `ml/training/incremental.py` y `backend/scripts/retrain.py`.

### BA-20 · Organizar backend, frontend y modelos · Arquitectura

**Caso de prueba.** Se sigue una publicación desde la vista al controlador, al servicio y al DAO. Se reemplaza el predictor por un doble de prueba.

**Aceptación**

- [ ] El backend separa entidades, controladores, servicios, DAO e integraciones.
- [ ] Nuevo reporte separa vista, controlador de formulario y servicio de publicación.
- [ ] El módulo ML mantiene entrenamiento e inferencia independientes del backend.
- [ ] Se pueden probar servicios con dependencias inyectadas y revertir escrituras ante errores.

**Evidencia.** [Guía de arquitectura](ARQUITECTURA.md) y `backend/tests/test_architecture.py`.

### BA-21 · Migrar, iniciar y comprobar el sistema · Arquitectura · QA

**Caso de prueba.** Mantenimiento prepara una base de desarrollo, aplica migraciones, levanta el servicio y ejecuta los tests. También verifica una base previa con datos.

**Aceptación**

- [ ] Alembic puede inicializar una base vacía y preservar reportes al adoptar una base anterior.
- [ ] El endpoint de salud informa disponibilidad de la API y del modelo.
- [ ] Las pruebas cubren login, publicación, coincidencias, filtros, REMUM y transacciones según el alcance del repositorio.

**Evidencia.** `make migrate`, `make test-python`, `npm run test:ci` en `frontend`, `backend/tests/test_migrations.py`. En la revisión del tablero pasaron 54 pruebas de Python y 4 de frontend.

## Lista Experimentos de IA

### BA-22 · Entrenar y evaluar el clasificador multimodal · IA

**Caso de prueba.** Comparar modelos de imagen, texto y multimodal con sus conjuntos reservados. Separar métricas de categoría de métricas de identificación.

**Aceptación**

- [ ] Quedan guardados configuración, checkpoints y métricas de evaluación.
- [ ] Se informa el tamaño de la prueba junto con accuracy y F1 macro.
- [ ] El resultado de clasificación se comunica como desempeño del experimento sobre ese conjunto.

**Resultado registrado.** 58/60 aciertos (96,7 %) y F1 macro 94,2 % en el conjunto del experimento. Se identificó reutilización de descripciones entre entrenamiento y prueba. Hace falta una prueba más representativa con reportes locales.

### BA-23 · Comparar ViT y DINOv2 para identificación · IA · Cotejo

**Caso de prueba.** Buscar un perro con una foto de hallazgo contra avisos de pérdida de una o varias fotos. Incluir perros ausentes y comparar fotos completas con recortes.

**Aceptación**

- [ ] El entrenamiento y la prueba separan identidades.
- [ ] Se informan aciertos entre los cinco primeros, precisión de sugerencias y falsos avisos por separado.
- [ ] El checkpoint experimental puede cargarse y probarse con datos temporales.

**Resultado registrado.** En DogReID, con hasta tres fotos de referencia, DINOv2 pasó del 20,2 % del ViT anterior al 42,9 % de aciertos entre los cinco primeros antes del umbral. Se conservan los experimentos con DogFaceNet, DogReID y MPDD. [Resultados y comandos](COTEJO_VISUAL.md)

### BA-24 · Versionar el dataset y reentrenar con recorte · IA

**Caso de prueba.** Crear un manifiesto por perro y escena, revisar un lote piloto de pelaje y comparar foto completa frente a recorte automático.

**Aceptación**

- [ ] El manifiesto separa entrenamiento, validación y prueba, y rechaza cruces de identidad o duplicados exactos entre roles.
- [ ] El predictor reproduce el preprocesamiento de la variante exportada.
- [ ] El informe distingue qué conjunto usó cada umbral y documenta cuántos datos locales y de pelaje se incorporaron.

**Resultado registrado.** Se procesaron 7.805 fotos públicas, con 3.090 para entrenamiento y 24 perros etiquetados en el piloto de pelaje. Con recorte y hasta tres fotos, el umbral calibrado dio 84,8 % de precisión en MPDD y 35,0 % en DogReID. [Informe](../ml/checkpoints/pet_reid/dinov2-v2.json)

## Lista Pendiente

### BA-25 · Verificar permisos, sesión y contacto real · Operación · REMUM

**Caso de prueba.** Comparar solicitudes de un visitante, un vecino autenticado y un administrador. Escanear una credencial de prueba y revisar a quién dirige el contacto.

**Aceptación**

- [ ] Se define quién puede actualizar reportes y administrar categorías.
- [ ] Las rutas operativas aplican el permiso correspondiente en el backend y se prueba el rechazo de un usuario sin autorización.
- [ ] El contacto de la ficha QR usa el destino autorizado de esa ficha. Si falta un contacto, la pantalla presenta el estado correspondiente.
- [ ] El comparador recibe la sesión de un usuario autenticado desde sus pantallas de entrada y permite completar la confirmación cuando tiene permiso.

**Hallazgo.** Hay rutas operativas que hoy comprueban sesión sin verificar el rol. La vista QR contiene un número fijo y las pantallas que abren el comparador omiten su token de sesión.

### BA-26 · Reunir y verificar una muestra local · IA · QA

**Caso de prueba.** Preparar un lote con fotos de un mismo perro en distintas sesiones, perros mestizos parecidos y búsquedas sin pareja.

**Aceptación**

- [ ] Cada foto local tiene autorización y una identidad revisada.
- [ ] La prueba local queda reservada antes de entrenar y no comparte perros con entrenamiento.
- [ ] El lote documenta los casos de pelaje parecido, misma raza y sesiones distintas.

**Referencia.** [Guía de etiquetado](ETIQUETADO_COTEJO.md) y [plan de reentrenamiento](PLAN_REENTRENAMIENTO_DINOV2.md).

**Avance.** Inventario de 12 fotos únicas de avisos y fichas REMUM. Falta confirmar identidades, sesiones y autorizaciones y reunir la muestra reservada.

### BA-27 · Validar 80 % de precisión y decidir activación · IA · QA

**Caso de prueba.** En una galería representativa se simula un hallazgo con una foto y sin datos descriptivos. Se evalúan pérdidas de una y varias fotos e identidades que no tienen un reporte compatible.

**Aceptación**

- [ ] Se acuerdan el tamaño mínimo de muestra y el piso de cobertura antes de abrir la prueba.
- [ ] Al menos 80 % de las sugerencias mostradas son del perro correcto en la prueba local reservada, para cada modalidad que se habilite.
- [ ] El informe incluye conteos, recuperación, cobertura y falsos avisos. Un sistema que no muestra sugerencias no puede aprobar.
- [ ] Si el checkpoint cumple, se verifica reindexación y reversión con una base temporal antes de activarlo por defecto.

**Decisión registrada.** DINOv2 v2 está activo como piloto en el entorno local de desarrollo. Se probaron la reindexación y la reversión en una copia temporal. Con hasta tres fotos de referencia y el umbral calibrado, obtuvo 84,8 % en MPDD y 35,0 % en DogReID. La corrida registró 0 fotos locales verificadas. La aprobación para uso general depende de la prueba reservada de BA-26. [Resultados y propuesta de validación](COTEJO_VISUAL.md#ba-27--decisión-de-activación).

### BA-28 · Validar el flujo completo con navegador y PostgreSQL · QA

**Caso de prueba.** Ejecutar la demo con una base de prueba y un navegador. Registrar cuenta, publicar un hallazgo, consultar el cotejo, cerrar un aviso, crear una ficha REMUM y escanear su QR.

**Aceptación**

- [ ] La migración y la demo se verifican sobre PostgreSQL con datos de prueba.
- [ ] Se registran resultados esperados y observados por paso, incluyendo un caso sin coincidencias y una operación rechazada.
- [ ] Cada hallazgo de la demo se enlaza a su tarjeta de seguimiento.
