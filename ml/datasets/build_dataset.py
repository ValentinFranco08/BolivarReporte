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
    "urban_arbol_caido": [
        "Un árbol cayó sobre la calle después de la tormenta y bloquea el paso.",
        "Hay un árbol caído en la vereda que impide la circulación peatonal.",
        "El temporal derribó un árbol que cortó la calle por completo.",
        "Reporto un árbol caído sobre la calzada, urgente despeje.",
        "Cayó un árbol grande en la avenida y bloqueó el tránsito.",
        "Un árbol viejo se vino abajo y está cortando la circulación.",
        "Después del viento fuerte hay un árbol caído que obstruye el paso.",
        "Árbol derrumbado sobre la vereda, peligro para los peatones.",
    ],
    "urban_bache": [
        "Hay un bache enorme en la calle que daña los vehículos.",
        "Reporto un pozo en la calzada que representa peligro para los autos.",
        "La calle tiene un bache profundo que puede causar accidentes.",
        "Hay un pozo grande en la vía que ya rompió varias cubiertas.",
        "Bache peligroso en la intersección, urge reparación.",
        "La calle tiene múltiples baches que hacen muy difícil el tránsito.",
        "Hay un agujero en el asfalto que representa riesgo para motos y ciclistas.",
        "Bache sin señalizar en zona de alta circulación.",
    ],
    "urban_basura": [
        "Hay acumulación de basura en la esquina hace varios días sin recolección.",
        "Reporto bolsas de residuos tiradas en la vía pública sin retirar.",
        "La basura se acumula en la calle porque no pasó el camión recolector.",
        "Hay residuos abandonados en la vereda que generan mal olor.",
        "Basura sin recolectar hace más de una semana en mi cuadra.",
        "Hay bolsas de basura tiradas en el medio de la calle.",
        "Se acumularon residuos domiciliarios en la vereda hace días.",
        "Gran cantidad de basura en la esquina atrae animales y genera problemas.",
    ],
    "urban_calle_deteriorada": [
        "La calle está muy deteriorada con el pavimento totalmente roto.",
        "El asfalto de esta arteria está en pésimas condiciones, lleno de grietas.",
        "Hay un tramo de calle completamente deteriorado que dificulta el tránsito.",
        "El pavimento de este sector está muy dañado y necesita urgente reparación.",
        "La calzada tiene grietas profundas y está levantada en varios puntos.",
        "Calle en muy mal estado, el asfalto se está desintegrando.",
        "El pavimento está roto y levantado, muy peligroso para motos.",
        "Calle deteriorada, hay pozos y el asfalto se levanta con el tráfico.",
    ],
    "urban_luminaria_danada": [
        "Hay una luminaria dañada en la calle que deja el sector sin iluminación.",
        "Reporto un farol roto que deja oscura toda la manzana de noche.",
        "La luz pública de esta cuadra no funciona hace semanas.",
        "Hay una luminaria caída en la vereda que representa un riesgo eléctrico.",
        "Se fundió el alumbrado público de toda la cuadra.",
        "Luminaria apagada en zona de mucho tránsito peatonal nocturno.",
        "Hay un poste con la luz rota que deja a oscuras el barrio.",
        "Tres luminarias seguidas sin funcionar, la zona queda muy oscura.",
    ],
    "urban_microbasural": [
        "Se formó un microbasural en el terreno baldío del barrio.",
        "Hay un basural clandestino a cielo abierto en la zona.",
        "Vecinos dejaron de depositar residuos en un punto que se convirtió en basural.",
        "Reporto un microbasural que atrae plagas y genera mal olor.",
        "Se formó un basural improvisado en el fondo de la manzana.",
        "Hay escombros y residuos acumulados formando un microbasural.",
        "En el terreno abandonado de la esquina se acumula basura de todo tipo.",
        "Microbasural en expansión, vecinos siguen arrojando residuos.",
    ],
    "urban_perdida_agua": [
        "Hay una pérdida de agua en la calle, el agua brota del pavimento.",
        "Reporto una cañería rota que está inundando la vereda.",
        "Hay agua brotando de la calle, parece una rotura de caño.",
        "Una pérdida de agua en la vereda lleva días sin ser reparada.",
        "Hay un caño roto que manda agua a la calle continuamente.",
        "Pérdida importante de agua en la vía pública.",
        "El asfalto está siempre mojado por una rotura de cañería.",
        "Agua saliendo del suelo en la calle, probablemente rotura de red.",
    ],
    "urban_senalizacion_danada": [
        "La señal de tránsito está caída y nadie la levantó.",
        "Hay una señalización dañada en la intersección que genera confusión.",
        "Reporto un cartel de tráfico que está roto o mal ubicado.",
        "La señal de pare está doblada y casi no se ve.",
        "Faltan señales de tránsito en esta esquina, es peligrosa.",
        "El semáforo no funciona hace días, nadie lo repara.",
        "Señalización horizontal borrada en zona escolar.",
        "La demarcación de la calzada está muy deteriorada y no se ve.",
    ],
    "transit_cordon_amarillo": [
        "Hay un auto estacionado sobre el cordón amarillo en esta esquina.",
        "Vehículo parado en zona de cordón amarillo, impide el giro.",
        "Reporto un auto sobre la línea amarilla del cordón.",
        "Estacionaron en cordón amarillo frente al comercio.",
        "Camioneta sobre cordón pintado de amarillo, no debería estar ahí.",
        "Auto detenido en cordón amarillo a media cuadra de mi casa.",
        "Hay un vehículo apoyado sobre el cordón amarillo de la ochava.",
        "Moto y auto sobre cordón amarillo en la avenida.",
    ],
    "transit_en_medio_de_calle": [
        "Hay un auto parado en el medio de la calle bloqueando el paso.",
        "Vehículo detenido en el centro de la calzada sin motivo.",
        "Un auto quedó parado en medio de la avenida y genera embotellamiento.",
        "Reporto un vehículo detenido en el carril central.",
        "Hay una camioneta parada en medio de la calle, no se puede circular.",
        "Auto frenado en el medio de la intersección.",
        "Vehículo ocupando el centro de la calzada hace rato.",
        "Están estacionados literalmente en el medio de la calle.",
    ],
    "transit_obstruccion_de_entrada": [
        "Un auto está tapando la entrada del garaje y no puedo salir.",
        "Vehículo estacionado frente a la cochera, obstruye la entrada.",
        "Tapan la entrada de mi casa con un auto mal estacionado.",
        "Hay un auto bloqueando el acceso vehicular del edificio.",
        "Reporto un vehículo que impide entrar al garage.",
        "Estacionaron delante de la rampa de entrada.",
        "La entrada peatonal y vehicular está obstruida por un auto.",
        "Camioneta cruzada tapando el portón de entrada.",
    ],
    "transit_sobre_vereda": [
        "Hay un auto estacionado arriba de la vereda y no se puede caminar.",
        "Vehículo subido a la acera, obliga a bajar a la calle.",
        "Estacionaron sobre la vereda frente a la escuela.",
        "Una camioneta está completamente sobre la vereda.",
        "Reporto autos estacionados en la acera, bloquean peatones.",
        "Moto y auto sobre la vereda en la esquina.",
        "No puedo pasar con el cochecito porque hay un auto en la vereda.",
        "Vehículo ocupando toda la vereda de mi cuadra.",
    ],
    "transit_lugar_reservado": [
        "Un auto sin permiso está en el lugar reservado para discapacidad.",
        "Estacionaron en el espacio de personas con movilidad reducida.",
        "Vehículo en lugar reservado de carga y descarga.",
        "Ocupan el cajón reservado sin credencial visible.",
        "Reporto un auto en el lugar exclusivo para discapacidad.",
        "Hay un vehículo en el estacionamiento reservado del hospital.",
        "Están usando el lugar reservado que no les corresponde.",
        "Auto en plaza azul de discapacidad, no tiene distintivo.",
    ],
    "transit_lugar_prohibido": [
        "Hay un auto estacionado donde está prohibido estacionar.",
        "Vehículo en zona de no estacionar, hay cartel visible.",
        "Estacionaron en prohibido frente a la esquina.",
        "Reporto un auto en área de estacionamiento prohibido.",
        "Camioneta parada en zona prohibida sobre la avenida.",
        "Están estacionados debajo del cartel de no estacionar.",
        "Auto en lugar prohibido, tapa la senda peatonal.",
        "Vehículo en zona restringida de estacionamiento.",
    ],
    "transit_vehiculo_abandonado": [
        "Hay un auto abandonado hace semanas en la calle, está sucio y sin patentes.",
        "Vehículo aparentemente abandonado, con pastos alrededor de las ruedas.",
        "Reporto un auto que no se mueve hace meses en esta cuadra.",
        "Hay un coche abandonado, vidrios polvorientos y sin ruedas.",
        "Vehículo abandonado en la vía pública, parece chocado y dejado.",
        "Un auto viejo está abandonado frente a mi casa.",
        "Camioneta abandonada, nadie la reclama.",
        "Hay un vehículo sin uso, abandonado en la banquina.",
    ],
    "transit_obstruccion_de_circulacion": [
        "La calle está bloqueada por un vehículo y no se puede circular.",
        "Hay una obstrucción en la calzada que corta el tránsito.",
        "Un camión trabado está impidiendo el paso en ambos sentidos.",
        "Reporto la calle cortada por un auto mal ubicado.",
        "Obstrucción de circulación en la avenida, se formó una cola enorme.",
        "No se puede pasar, hay un vehículo bloqueando todo el carril.",
        "La esquina está intransitable por un auto atravesado.",
        "Circulación obstruida por un vehículo detenido en doble fila.",
    ],
    "transit_semaforo_danado": [
        "El semáforo de esta esquina no funciona, está apagado.",
        "Semáforo caído después del viento, peligroso para el cruce.",
        "El semáforo intermitente o muerto genera confusión en la intersección.",
        "Reporto un semáforo dañado, solo prende una luz.",
        "Semáforo fuera de servicio en una esquina con mucho tránsito.",
        "El semáforo peatonal no anda y los autos no paran.",
        "Hay un semáforo colgando, parece que se va a caer.",
        "Cruce sin semáforo operativo, urge reparación.",
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
            label = get_label_from_folder(category_name)
            templates = TEMPLATES.get(category_name, [f"Reporto un problema de tipo {label}."])

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
