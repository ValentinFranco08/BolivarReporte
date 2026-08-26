"""
Script para COMPLETAR el dataset existente hasta 100 fotos por categoria.
NO borra las fotos ya existentes, solo agrega las que faltan.
"""
import os
import shutil
import random
from pathlib import Path
from PIL import Image
from bing_image_downloader import downloader

random.seed(42)

TARGET_TOTAL = 100
SPLIT_RATIOS = {"train": 0.75, "val": 0.15, "test": 0.10}

CATEGORIES_QUERIES = {
    "animals_animal_abandonado": [
        "perro abandonado calle argentina",
        "perro mestizo rescatado calle",
        "gato callejero vereda",
        "perro abandonado ciudad raza mestiza",
        "cachorro abandonado vereda calle",
        "perro sin dueno calle argentina fotos",
    ],
    "animals_animal_en_riesgo": [
        "perro en la ruta peligro",
        "animal atrapado rescate bomberos",
        "perro autopista banquina",
        "perro ruta nacional atropellado",
        "animal en peligro calle trafico",
        "perro cruzando calle peligro",
    ],
    "animals_animal_encontrado": [
        "perro encontrado plaza collar",
        "perrito hallado calle",
        "gato encontrado patio",
        "perro hallado con collar sin dueno",
        "mascota encontrada barrio fotos",
        "gato perdido encontrado calle",
    ],
    "animals_animal_perdido": [
        "mascota perdida perro cartel",
        "perro buscando dueno calle",
        "perro desorientado barrio",
        "cartel se busca perro barrio",
        "perro perdido volante fotos",
        "busco mi mascota perdida cartel",
    ],
    "animals_animal_suelto": [
        "perro suelto vereda barrio",
        "caballo suelto calle ciudad",
        "perro deambulando asfalto",
        "perro sin correa calle ciudad",
        "animal suelto calle argentina",
        "perros sueltos barrio vereda fotos",
    ],
    "animals_posible_animal_herido": [
        "perro rengo callejero",
        "animal herido rescate proteccionista",
        "perro lastimado calle asistencia",
        "perro herido pata calle fotos",
        "gato herido calle rescate",
        "animal accidentado calle veterinaria",
    ],
    "urban_arbol_caido": [
        "arbol caido calle tormenta argentina",
        "rama caida vereda cables",
        "arbol arrancado viento asfalto",
        "arbol sobre la calle tormenta",
        "caida de arbol ciudad viento",
        "arbol volcado sobre auto calle",
    ],
    "urban_bache": [
        "bache profundo asfalto calle argentina",
        "pozo peligroso calle bacheo",
        "crater asfalto roto calle",
        "bache grande ruta asfalto danado",
        "deterioro asfalto calle municipal",
        "agujero en la calle pavimento roto",
    ],
    "urban_basura": [
        "basura acumulada vereda calle buenos aires",
        "bolsas de basura rota contenedor",
        "residuos tirados esquina calle",
        "basura en la via publica argentina",
        "bolsas residuos vereda sin recolectar",
        "acumulacion residuos urbanos calle",
    ],
    "urban_calle_deteriorada": [
        "calle de tierra poceada barro argentina",
        "calle intransitable zanja lodo",
        "camino de tierra roto lomas",
        "asfalto deteriorado baches calle barrio",
        "pavimento roto calle municipal argentina",
        "calle en mal estado lodo barrio",
    ],
    "urban_luminaria_danada": [
        "farol roto poste alumbrado publico",
        "luminaria publica rota calle noche",
        "columna alumbrado doblada chocada",
        "farola rota calle oscuridad",
        "poste de luz caido calle",
        "alumbrado publico danado sin luz calle",
    ],
    "urban_microbasural": [
        "microbasural esquina terreno baldio",
        "basural a cielo abierto barrio escombros",
        "acumulacion de basura escombros esquina",
        "basural espontaneo calle argentina",
        "montana escombros basura vereda",
        "micro basural barrio municipal fotos",
    ],
    "urban_perdida_agua": [
        "perdida de agua cano roto vereda pavimento",
        "agua brotando asfalto calle rotura",
        "cano roto agua corriente calle inundada",
        "perdida agua potable vereda calle",
        "fuga de agua municipio calle inundada",
        "rotura caneria agua calle argentina",
    ],
    "urban_senalizacion_danada": [
        "cartel pare caido transito chocado",
        "senal de transito rota vandalizada",
        "nomenclador de calle roto doblado",
        "senal transito caida calle argentina",
        "cartel transito doblado accidente",
        "senalizacion vial deteriorada calle",
    ],
}


def is_valid_real_photo(img_path, min_size=220):
    try:
        with Image.open(img_path) as im:
            w, h = im.size
            if w < min_size or h < min_size:
                return False
            if im.format in ['GIF', 'ICO']:
                return False
            if im.mode == 'RGBA':
                extrema = im.getextrema()
                if len(extrema) == 4 and extrema[3][0] < 250:
                    return False
            im.convert('RGB')
            return True
    except Exception:
        return False


def count_existing(base_dest, cat_name):
    total = 0
    for split in ["train", "val", "test"]:
        d = base_dest / split / cat_name
        if d.exists():
            total += len([f for f in d.iterdir() if f.is_file()])
    return total


def complete_dataset(target=TARGET_TOTAL):
    base_dest = Path("local_images")
    temp_dir = Path("temp_downloads_extra")

    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    n_val   = max(1, round(target * SPLIT_RATIOS["val"]))
    n_test  = max(1, round(target * SPLIT_RATIOS["test"]))
    n_train = target - n_val - n_test

    print(f"\n Objetivo: {target} fotos por categoria")
    print(f"   Train: {n_train} | Val: {n_val} | Test: {n_test}\n")

    for cat_name, queries in CATEGORIES_QUERIES.items():
        existing = count_existing(base_dest, cat_name)
        print(f"[{cat_name}]: {existing} fotos actuales", end="", flush=True)

        if existing >= target:
            print(f" -> Ya completa ({existing}), se omite.")
            continue

        needed = target - existing
        print(f" -> Faltan {needed}, descargando...")

        valid = []
        for q in queries:
            if len(valid) >= needed + 10:
                break
            try:
                downloader.download(
                    q,
                    limit=25,
                    output_dir=str(temp_dir),
                    adult_filter_off=True,
                    force_replace=False,
                    timeout=10,
                    verbose=False
                )
                q_dir = temp_dir / q
                if q_dir.exists():
                    for f in sorted(q_dir.iterdir()):
                        if f.is_file() and is_valid_real_photo(f):
                            valid.append(f)
                            if len(valid) >= needed + 10:
                                break
            except Exception as e:
                print(f"  Advertencia en '{q}': {e}")

        if not valid:
            print(f"  ERROR: No se encontraron fotos para {cat_name}")
            continue

        random.shuffle(valid)

        train_dir = base_dest / "train" / cat_name
        val_dir   = base_dest / "val"   / cat_name
        test_dir  = base_dest / "test"  / cat_name

        train_have = len(list(train_dir.iterdir())) if train_dir.exists() else 0
        val_have   = len(list(val_dir.iterdir()))   if val_dir.exists()   else 0
        test_have  = len(list(test_dir.iterdir()))  if test_dir.exists()  else 0

        train_need = max(0, n_train - train_have)
        val_need   = max(0, n_val   - val_have)
        test_need  = max(0, n_test  - test_have)

        def save_photos(photo_list, dest_dir, start_idx):
            dest_dir.mkdir(parents=True, exist_ok=True)
            for i, f in enumerate(photo_list):
                try:
                    with Image.open(f) as im:
                        out = dest_dir / f"real_{start_idx + i:03d}.jpg"
                        im.convert('RGB').save(out, "JPEG", quality=90)
                except Exception:
                    pass

        ptr = 0
        save_photos(valid[ptr:ptr+train_need], train_dir, train_have); ptr += train_need
        save_photos(valid[ptr:ptr+val_need],   val_dir,   val_have);   ptr += val_need
        save_photos(valid[ptr:ptr+test_need],  test_dir,  test_have);

        final = count_existing(base_dest, cat_name)
        print(f"  OK: ahora tiene {final} fotos totales.")

    shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n" + "="*60)
    print("RESUMEN FINAL:")
    for cat_name in CATEGORIES_QUERIES:
        total = count_existing(base_dest, cat_name)
        td = base_dest / "train" / cat_name
        vd = base_dest / "val"   / cat_name
        xd = base_dest / "test"  / cat_name
        tc = len(list(td.iterdir())) if td.exists() else 0
        vc = len(list(vd.iterdir())) if vd.exists() else 0
        xc = len(list(xd.iterdir())) if xd.exists() else 0
        ok = "OK" if total >= target else f"INCOMPLETA ({total}/{target})"
        print(f"  [{ok}] {cat_name}: train={tc} val={vc} test={xc}")
    print("="*60)
    print("\nListo! Correr: python3 ml/datasets/build_dataset.py y reentrenar.")


if __name__ == "__main__":
    complete_dataset(target=TARGET_TOTAL)
