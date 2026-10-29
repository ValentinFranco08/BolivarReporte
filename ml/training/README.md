# Cómo funciona el entrenamiento

Leer estos tres archivos en este orden:

| Archivo | Qué hace | Dónde empezar |
|---|---|---|
| `train.py` | Prepara datos y modelo, ejecuta las fases y guarda resultados | `run_training()` |
| `trainer.py` | Actualiza pesos por lotes y repite épocas | `Trainer.fit()` y `Trainer.train_epoch()` |
| `incremental.py` | Entrena con correcciones humanas y ejemplos históricos | `IncrementalTrainer.run()`; es un flujo opcional |

## Recorrido normal

```text
Configuración JSON → train.py → Trainer.fit() → Trainer.train_epoch()
                                   ↓
                           Evaluar y guardar checkpoint
```

`run_training()` tiene tres pasos comentados: preparar, entrenar y evaluar.

Una época recorre todos los lotes de entrenamiento. Cada lote pasa por la red, se calcula el error, se calculan gradientes con `loss.backward()` y se actualizan los pesos con `optimizer.step()`.

Después de cada época se mide el F1 en validación. Si mejora, se guarda el checkpoint. Si pasan varias épocas sin mejora, se detiene la fase. El conjunto test se usa al final.

El multimodal tiene tres fases: fusión y clasificador; después se incorporan los últimos bloques de ViT; finalmente los últimos bloques de RoBERTa. Las épocas y cantidades de bloques se configuran en `ml/configs/multimodal.json`. Las capas de la red están en `ml/models/`.

## Ejecutar desde la raíz

```bash
source venv/bin/activate
python -m ml.cli train --model multimodal --dry-run
python -m ml.cli train --model multimodal
```

Para los baselines, cambiar `multimodal` por `vit` o `roberta`. Todos usan el mismo objeto `Trainer`, porque los modelos aceptan entradas por nombre.

`--dry-run` muestra la configuración sin cargar pesos ni entrenar. Entrenar no activa automáticamente los pesos nuevos en el backend.

## Qué se configura y dónde

| Cambio | Archivo | Efecto |
|---|---|---|
| Épocas, lotes y tasas de aprendizaje | `ml/configs/*.json` | Cambia la ejecución del entrenamiento |
| Cantidad de bloques finales que se descongelan | `ml/configs/*.json` | Cambia qué pesos existentes pueden aprender |
| Rutas de dataset y checkpoints | `ml/configs/*.json` | Cambia entradas y salidas del experimento |
| Dimensiones, capas y dropout del clasificador | `ml/models/multimodal.py` o `baselines.py` | Cambia la arquitectura y puede volver incompatibles los pesos anteriores |
| Modelo preentrenado de imagen o texto | `vit_encoder.py` y `roberta_encoder.py` | Cambia el encoder y exige comprobar dimensiones y compatibilidad |
| Etiquetas y orden de sus índices | `ml/taxonomy.py` | Cambia la interpretación de las salidas y requiere revisar dataset y checkpoint |

Los parámetros de ejecución no agregan capas. La longitud del texto y el preprocesamiento deben coincidir al entrenar y predecir; el predictor recupera del checkpoint la configuración disponible. El código del backend no realiza estos cambios cuando recibe un reporte.
