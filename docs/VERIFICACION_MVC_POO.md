# Verificación de la implementación MVC y POO

Fecha: 29 de octubre de 2026.

## Referencia inicial

Se conservaron los cambios locales de la simplificación de entrenamiento. Antes de editar el backend se ejecutó `make test-python`: **39 pruebas aprobadas**.

Se registró el OpenAPI completo de la aplicación: **24 rutas y 25 operaciones**. La comparación posterior incluye parámetros, cuerpos, respuestas, seguridad y esquemas de componentes.

## Resultado final

| Comprobación | Resultado |
|---|---|
| Suite de backend y ML | **42 pruebas aprobadas** |
| Contrato OpenAPI | Idéntico a la referencia inicial |
| Referencias Python a las tres fachadas retiradas | Sin consumidores restantes |
| Compilación de módulos Python modificados y scripts | Correcta |
| Sintaxis de `dev.sh` | Correcta |
| Migraciones y seed | Probados en bases SQLite temporales, desde cero y con esquema histórico |

SHA-256 del OpenAPI normalizado con claves ordenadas y JSON compacto, igual antes y después:

```text
198250d9665102396f77bfffb32cd8fe3145803449be87d5502f272d98e1d964
```

La suite se ejecuta con:

```bash
source venv/bin/activate
make test-python
```

## Comportamientos comprobados

- Crear un reporte con su categoría, predicción y feedback en una sola transacción.
- Revertir todas las escrituras cuando falla el guardado de feedback.
- Revertir centroides y reasignación de reportes cuando falla la fusión de categorías.
- Actualizar repetidamente el feedback de una predicción sin duplicarlo.
- Comprobar permisos REMUM antes de modificar estado o crear alertas.
- Conservar coordenadas cero, confianza cero y el contador inicial de una categoría nueva.
- Resolver matching y autenticación mediante los servicios actuales.
- Usar un único predictor inyectado durante el ciclo de vida y las solicitudes HTTP.
- Importar la API sin cargar PyTorch.
- Mantener los límites entre controladores, repositorios y el módulo ML.

## Entrenamiento y comandos

Las pruebas ejecutan un entrenamiento pequeño, guardan y recuperan checkpoints y verifican las tres fases de `run_training()`. El mismo `Trainer` trabaja con modelos de imagen, texto y multimodal. También se comprueban métricas con clases ausentes y replay limitado al conjunto train.

Se verificaron los comandos `train --dry-run` para los tres modelos y `incremental --dry-run` con datos temporales, además de la ayuda de `manage.py`, `export_dataset.py` y `retrain.py`.

Las utilidades históricas de descarga, semillas con imágenes y transferencia de bases se revisaron y compilaron, pero no se ejecutaron sobre datos del usuario.

## Inferencia real

Se cargó el checkpoint local `best_multimodal_finetuned.pt`, identificado como `multimodal-v1 (best_multimodal_finetuned.pt)`, con los recursos locales y el acceso de Hugging Face en modo offline.

Sobre una base SQLite temporal e imágenes temporales se completó:

```text
Arranque → Predicción real → Login → Crear reporte → Buscar coincidencias → Resolver reporte
```

La predicción devolvió un embedding de 768 dimensiones. El reporte conservó confianza y coordenadas cero. El tamaño y la fecha de modificación del checkpoint permanecieron iguales.

## Límites

Esta ejecución valida organización, contratos y comportamientos; no mide una nueva precisión de la red ni realiza un entrenamiento completo. La comprobación de inferencia usó una imagen sintética para recorrer el sistema.

Las transacciones y migraciones se comprobaron con SQLite. No se validó la ejecución contra un servidor PostgreSQL ni se ejecutaron migraciones sobre la base del usuario. La interfaz web se revisó en sus llamadas a `frontend/lib/api.ts`, formularios y filtros; no hubo cambios visuales ni una prueba de navegador de extremo a extremo.
