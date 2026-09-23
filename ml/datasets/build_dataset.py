"""
Script para generar el dataset multimodal (imagen + texto + label).
Recorre local_images/{train,val,test}/<categoria>/<imagen>
y crea ml/datasets/dataset.json con textos sintéticos realistas.
"""

import os
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Semilla para reproducibilidad
random.seed(42)

# -----------------------------------------------------------------------
# Plantillas de texto por categoría (5-10 variantes c/u)
# -----------------------------------------------------------------------
TEMPLATES = {
    "animals_animal_abandonado": [
        "Encontré un animal abandonado en la calle, parece que lleva días ahí sin comer.",
        "Hay un perro que fue dejado en la vía pública, se ve desnutrido y asustado.",
        "Vi a un animal solo en el barrio, claramente fue abandonado por su dueño.",
        "Reporto un animal abandonado cerca de mi casa, necesita ayuda urgente.",
        "Un gato fue dejado en la calle sin comida ni agua, está en mal estado.",
        "Animal abandonado en la vereda, nadie lo reclama hace varios días.",
        "Encontré un perro atado a un árbol y abandonado, urge rescate.",
        "Hay un animal que fue claramente dejado atrás por sus dueños, necesita asistencia.",
    ],
    "animals_animal_en_riesgo": [
        "Hay un animal en situación de riesgo sobre la ruta, puede ser atropellado.",
        "Vi un perro en peligro cerca de la carretera, corre riesgo de accidente.",
        "Reporto un animal en una situación peligrosa, necesita ser rescatado.",
        "Un animal está atrapado en un lugar de difícil acceso, urge ayuda.",
        "Hay un gato en el techo de un edificio sin poder bajar.",
        "Vi a un animal en riesgo inminente, está cerca de cables eléctricos caídos.",
        "Perro en riesgo, atascado entre rejas sin poder moverse.",
        "Animal en peligro junto a un desagüe abierto.",
    ],
    "animals_animal_encontrado": [
        "Encontré un perro perdido en la calle, tiene collar pero no tiene placa.",
        "Apareció un gato en mi patio, parece domesticado pero no sé de quién es.",
        "Hallé un animal en la vía pública que parece tener dueño.",
        "Encontré un perro deambulando por el barrio, está en buen estado.",
        "Me apareció un animal en la puerta de casa, parece domesticado.",
        "Encontré un perrito solo en la plaza, está limpio y parece tener dueño.",
        "Hay un animal encontrado en mi calle, busco a sus dueños.",
        "Apareció un gato con collar azul en mi jardín.",
    ],
    "animals_animal_perdido": [
        "Se me perdió mi perro, era un labrador dorado, desapareció ayer.",
        "Busco a mi gato que se escapó hace dos días del barrio centro.",
        "Mi mascota se perdió cerca de la plaza, es un caniche blanco pequeño.",
        "Perdí a mi perro pastor alemán, si lo ven avisen por favor.",
        "Se escapó mi gata de la casa, es gris con ojos verdes.",
        "Mi perro se perdió ayer a la tarde, es de raza poodle y anda asustado.",
        "Estoy buscando a mi mascota perdida, era un perro mestizo marrón.",
        "Mi gato macho naranja se escapó esta mañana.",
    ],
    "animals_animal_suelto": [
        "Hay un perro suelto en la calle sin collar ni dueño a la vista.",
        "Vi un animal deambulando por el barrio sin nadie que lo cuide.",
        "Hay varios perros sueltos en la avenida, pueden causar accidentes.",
        "Un animal anda suelto en la zona y asusta a los vecinos.",
        "Hay un perro grande suelto en el parque sin su dueño.",
        "Vi un animal corriendo sin rumbo por la calle principal.",
        "Perro suelto en el centro, sin collar, pareciera sin dueño.",
        "Animal suelto en zona escolar, puede representar peligro para los chicos.",
    ],
    "animals_posible_animal_herido": [
        "Vi un animal que parece estar herido en la vereda, cojea bastante.",
        "Hay un perro que está sangrando en la calle, necesita atención veterinaria.",
        "Encontré un gato que parece haber sido atropellado, urge ayuda.",
        "Un animal en la vía pública parece tener una lesión en la pata.",
        "Vi un perro que no puede caminar bien, posiblemente esté herido.",
        "Hay un animal herido tirado en la calle, no se levanta.",
        "Encontré un gato lastimado, tiene una herida visible en el cuerpo.",
        "Animal con signos de estar golpeado o atropellado, necesita veterinario urgente.",
    ],
}

def get_label_from_folder(folder_name: str) -> str:
    from ml.taxonomy import FOLDER_TO_LABEL
    return FOLDER_TO_LABEL.get(folder_name, folder_name)

def build_dataset():
    base_path = Path("local_images")
    splits = ["train", "val", "test"]
    
    all_records = []
    stats = {}

    for split in splits:
        split_path = base_path / split
        if not split_path.exists():
            print(f"  ⚠️  No existe {split_path}, se omite.")
            continue

        for category_dir in sorted(split_path.iterdir()):
            if not category_dir.is_dir():
                continue

            category_name = category_dir.name
            
            # Si no está en TEMPLATES, significa que fue purgado de la taxonomía (ej. urban_ o transit_)
            if category_name not in TEMPLATES:
                continue
                
            label = get_label_from_folder(category_name)
            templates = TEMPLATES[category_name]

            images = sorted([f for f in category_dir.iterdir() if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]])
            if not images:
                continue

            count = 0
            for img_path in images:
                text = random.choice(templates)
                record = {
                    "image": str(img_path),
                    "text": text,
                    "label": label,
                    "split": split,
                }
                all_records.append(record)
                count += 1

            key = f"{split}/{category_name}"
            stats[key] = count

    # Si no hay imágenes en test, tomamos el 15% del train
    has_test = any(r["split"] == "test" for r in all_records)
    if not has_test:
        print("  ℹ️  Split 'test' vacío. Re-asignando 15% del train como test...")
        train_records = [r for r in all_records if r["split"] == "train"]
        random.shuffle(train_records)
        n_test = max(1, int(len(train_records) * 0.15))
        test_records = train_records[:n_test]
        test_ids = {id(r) for r in test_records}
        for r in all_records:
            if id(r) in test_ids:
                r["split"] = "test"

    # Guardar dataset.json
    output_path = Path("ml/datasets/dataset.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    train_c = sum(1 for r in all_records if r["split"] == "train")
    val_c   = sum(1 for r in all_records if r["split"] == "val")
    test_c  = sum(1 for r in all_records if r["split"] == "test")

    print(f"\n✅ Dataset generado con {len(all_records)} ejemplos totales.")
    print(f"   train: {train_c} | val: {val_c} | test: {test_c}")
    print(f"   Guardado en: {output_path}")

    labels = {}
    for r in all_records:
        labels[r["label"]] = labels.get(r["label"], 0) + 1
    print("\n📊 Distribución por categoría:")
    for k, v in sorted(labels.items()):
        print(f"  {k}: {v}")

if __name__ == "__main__":
    build_dataset()
