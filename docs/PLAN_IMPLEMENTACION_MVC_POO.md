# Plan de implementación: MVC y POO con lectura sencilla

Fecha: 29 de octubre de 2026.

## Objetivo

Consolidar una arquitectura que permita seguir una operación desde la pantalla hasta la base de datos o la red neuronal. Cada clase debe tener una responsabilidad concreta y cada archivo debe poder explicarse en una frase.

El proyecto ya tiene controladores, servicios, repositorios y un módulo ML independiente. El trabajo consiste en simplificar y completar esa organización. La carpeta de entrenamiento ya se redujo a `train.py`, `trainer.py` e `incremental.py`.

La última verificación registrada en este chat fue de 39 pruebas aprobadas. Se volverá a establecer la referencia al comenzar la implementación, porque existen cambios locales de la simplificación que deben conservarse.

## Estructura de referencia

```text
frontend/                     Vista Next.js
backend/app/
  main.py                     Configuración y arranque HTTP
  controllers/                Solicitudes y respuestas HTTP
  services/                   Casos de uso y reglas de negocio
  repositories/               Acceso a datos
  models.py                   Entidades ORM
  schemas.py                  Entradas y respuestas validadas
  database.py                 Conexión y sesiones
  dependencies.py             Construcción de los colaboradores
  core/                       Configuración y errores compartidos
  infrastructure/             Archivos, transacciones y carga del predictor
ml/
  models/                     Capas y forward de las redes
  data/                       Dataset y preparación
  preprocessing/              Imágenes y texto
  training/train.py           Preparar y ejecutar el entrenamiento
  training/trainer.py         Aprender por épocas y lotes
  training/incremental.py     Correcciones humanas y replay
  evaluation/                 Métricas
  inference/                  Predicción y checkpoints
  configs/                    Parámetros de entrenamiento
  taxonomy.py                 Clases y correspondencia de índices
```

`core` e `infrastructure` conservan auxiliares con una función real. Por ejemplo, `UnitOfWork` garantiza rollback y `LazyPredictor` coordina carga y acceso al modelo. Reducir cantidad de archivos no justifica perder esas garantías.

## Etapa 1 — Establecer la referencia y el mapa de responsabilidades

- Revisar el estado de Git y conservar los cambios locales existentes.
- Ejecutar `make test-python` y registrar resultados y fallos previos.
- Registrar rutas, entradas y respuestas de OpenAPI.
- Clasificar los archivos actuales como implementación principal, entrada de comando o compatibilidad histórica.
- Documentar tres recorridos: clasificar una imagen, crear un reporte y entrenar el modelo.

**Entrega:** inventario breve y referencia de comportamiento.

**Criterio de cierre:** identificar qué hace cada módulo, quién lo utiliza y qué comportamiento debe conservarse.

## Etapa 2 — Simplificar el caso completo de reportes

Tomar reportes como ejemplo para el resto del backend:

```text
Vista → Controlador → ReportService → ReportRepository → Base de datos
                            ↓
                   ClassificationService → Predictor
```

- Mantener el controlador centrado en recibir datos y llamar al servicio.
- Dar al servicio métodos públicos con nombres de casos de uso: crear, listar, actualizar y resolver.
- Mantener las consultas SQL en repositorios.
- Hacer explícitas las dependencias en los constructores y en `dependencies.py`.
- Simplificar delegaciones redundantes, conservando las que delimitan responsabilidades útiles.
- Mantener una sola transacción para categoría, reporte, predicción y feedback.
- Conservar los esquemas de entrada y salida en `schemas.py`.

**Entrega:** un flujo de reportes que sirva como ejemplo de MVC y POO.

**Criterio de cierre:** se puede seguir desde el controlador hasta el repositorio o predictor, y un fallo de guardado revierte todas las escrituras del caso de uso.

## Etapa 3 — Aplicar el mismo criterio al resto del backend

Revisar autenticación, categorías, matching, feedback y REMUM en ese orden.

- Utilizar nombres consistentes por área, como `services/reports.py` y `repositories/reports.py`.
- Evitar SQL, carga de archivos y ejecución neuronal dentro de controladores.
- Mantener reglas de permisos y estados en servicios o políticas concretas.
- Conservar funciones puras para cálculos matemáticos pequeños.
- Revisar que las vistas presenten información y gestionen interacción; las decisiones de negocio deben validarse en el backend.
- Mantener las operaciones de mantenimiento fuera del arranque HTTP.

**Entrega:** áreas con la misma organización y convenciones.

**Criterio de cierre:** comprender reportes permite localizar el código equivalente de REMUM o categorías, sin aprender otra arquitectura.

## Etapa 4 — Consolidar el recorrido sencillo de ML

Conservar la simplificación ya realizada:

```text
Configuración → train.py → Trainer.fit() → Trainer.train_epoch()
                                ↓
                      Evaluación y checkpoint
```

- Revisar que `train.py` muestre los pasos de preparar, entrenar y evaluar en orden.
- Mantener `Trainer` como clase que encapsula el aprendizaje por lotes y épocas.
- Usar la interfaz común de los modelos para compartir el entrenador.
- Mantener capas en `models/` y parámetros de entrenamiento en `configs/`.
- Aclarar en la documentación qué parámetros se pueden modificar sin cambiar la arquitectura de la red.
- Mantener el entrenamiento incremental como flujo opcional y separado del recorrido principal.
- Conservar el preprocesamiento compartido y la correspondencia de etiquetas de los checkpoints.

**Entrega:** entrenamiento comprensible a partir de tres archivos principales y una guía corta.

**Criterio de cierre:** el mismo entrenador funciona con imagen, texto y multimodal, guarda y recupera checkpoints y conserva las fases configuradas.

## Etapa 5 — Unificar la integración y retirar compatibilidad innecesaria

En la referencia inicial había consumidores de los módulos históricos:

- `crud.py`: pruebas de categorías, centroides y matching.
- `ai_service.py`: pruebas de embeddings y scripts de semillas.
- `llm_categorizer.py`: pruebas de sugerencias.

Actualizar esos consumidores hacia los servicios, repositorios o módulos ML correspondientes antes de retirar cualquier fachada.

- Mantener un punto claro de construcción del predictor en las dependencias del backend.
- Separar carga del modelo, predicción y persistencia.
- Verificar que ML no importe FastAPI, SQLAlchemy ni módulos del backend.
- Documentar los comandos activos en una sola guía.
- Retirar fachadas sin consumidores; conservar compatibilidad cuando exista un consumidor conocido que todavía la necesite.
- Clasificar las utilidades históricas de datos y semillas. Su eliminación requiere comprobar que su función esté cubierta o haya dejado de utilizarse.

**Entrega:** una ruta principal por operación, con menos importaciones históricas y documentación coherente.

**Criterio de cierre:** no hay referencias rotas y los comandos documentados siguen funcionando.

## Etapa 6 — Verificar y preparar la explicación académica

- Ejecutar las pruebas de backend y ML pertinentes a los cambios.
- Comparar el contrato HTTP con la referencia de la etapa 1.
- Comprobar creación y rollback de reportes, permisos REMUM, categorías y matching.
- Comprobar entrenamiento breve con modelos pequeños, validación, guardado y recuperación.
- Probar inferencia con el checkpoint disponible sobre datos y almacenamiento temporales.
- Actualizar `docs/ARQUITECTURA.md`, el README principal y la guía corta de entrenamiento.
- Incorporar un diagrama de componentes y un UML pequeño con las clases centrales.
- Explicar con código real encapsulamiento, composición, herencia de `nn.Module` y polimorfismo de los modelos.

**Entrega:** implementación verificada y material para explicar el proyecto frente al profesor.

**Criterio de cierre:** poder responder dónde están las capas, dónde se actualizan los pesos, cómo se predice, cómo se guardan reportes y qué principio de POO cumple cada clase principal.

## Alcance y orden de ejecución

Orden: referencia → reportes → otras áreas del backend → consolidación de ML → compatibilidad → verificación y documentación.

Esta implementación trata la organización del código. Se conservarán la arquitectura neuronal, la taxonomía, los pesos existentes y las reglas funcionales, salvo correcciones concretas identificadas y verificadas. El reentrenamiento completo no es necesario para validar una refactorización.

Los controladores pueden ser funciones con `APIRouter`. La POO se aplica a objetos con responsabilidad y comportamiento; no exige convertir cada función en una clase ni eliminar los bucles propios del entrenamiento.

## Lista de finalización

- [x] Referencia de pruebas y contratos registrada.
- [x] Reportes consolidado como ejemplo principal.
- [x] Resto del backend con convenciones consistentes.
- [x] ML con recorrido corto y configuración clara.
- [x] Consumidores históricos migrados y fachadas revisadas.
- [x] Pruebas pertinentes aprobadas y límites de validación registrados.
- [x] Diagramas y guía de defensa actualizados.


## Ejecución completada — 29 de octubre de 2026

- Referencia inicial: 39 pruebas aprobadas; contrato completo de 24 rutas y 25 operaciones registrado antes de editar.
- Reportes: creación organizada en tres pasos y una sola transacción; el feedback se persiste directamente mediante `FeedbackRepository`, sin un servicio intermedio de persistencia.
- Categorías: un único método público para aprobar y otro para fusionar; la resolución de la categoría de un reporte está encapsulada en `resolve_for_report()`.
- Autenticación: dependencias HTTP en `auth.py`, registro/login en `AuthService`, funciones de contraseñas y JWT en `infrastructure/security.py`.
- Predictor: construcción compartida mediante `get_predictor()`; el arranque y las rutas usan el mismo proveedor, también al inyectar uno de prueba.
- Compatibilidad: consumidores migrados y fachadas `crud.py`, `ai_service.py` y `llm_categorizer.py` retiradas. También se retiró la importación histórica `ml/datasets/multimodal_dataset.py`, sin consumidores. Las utilidades manuales específicas permanecen inventariadas en la guía.
- ML: conservados `train.py`, `trainer.py` e `incremental.py`; documentada la diferencia entre parámetros de ejecución, arquitectura y taxonomía.
- Verificación: 42 pruebas aprobadas, OpenAPI idéntico a la referencia y prueba del flujo completo con el checkpoint real usando base e imágenes temporales.

El detalle y los límites de la validación están en [VERIFICACION_MVC_POO.md](VERIFICACION_MVC_POO.md). La guía de lectura, diagramas e inventario final están en [ARQUITECTURA.md](ARQUITECTURA.md).
