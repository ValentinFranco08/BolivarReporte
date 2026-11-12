import os
import shutil
import random
from pathlib import Path
from PIL import Image
from bing_image_downloader import downloader

# Semilla fija para reproducibilidad
random.seed(42)

CATEGORIES_QUERIES = {
    "animals_animal_abandonado": [
        "perro abandonado calle argentina",
        "perro mestizo rescatado calle",
        "gato callejero vereda",
    ],
    "animals_animal_en_riesgo": [
        "perro en la ruta peligro",
        "animal atrapado rescate bomberos",
        "perro autopista banquina",
    ],
    "animals_animal_encontrado": [
        "perro encontrado plaza collar",
        "perrito hallado calle",
        "gato encontrado patio",
    ],
    "animals_animal_perdido": [
        "mascota perdida perro cartel",
        "perro buscando dueño calle",
        "perro desorientado barrio",
    ],
    "animals_animal_suelto": [
        "perro suelto vereda barrio",
        "caballo suelto calle ciudad",
        "perro deambulando asfalto",
    ],
    "animals_posible_animal_herido": [
        "perro rengo callejero",
        "animal herido rescate proteccionista",
        "perro lastimado calle asistencia",
    ],
    "urban_arbol_caido": [
        "arbol caido calle tormenta argentina",
        "rama caida vereda cables",
        "arbol arrancado viento asfalto",
    ],
    "urban_bache": [
        "bache profundo asfalto calle argentina",
        "pozo peligroso calle bacheo",
        "crater asfalto roto calle",
    ],
    "urban_basura": [
        "basura acumulada vereda calle buenos aires",
        "bolsas de basura rota contenedor",
        "residuos tirados esquina calle",
    ],
    "urban_calle_deteriorada": [
        "calle de tierra poceada barro argentina",
        "calle intransitable zanja lodo",
        "camino de tierra roto lomas",
    ],
    "urban_luminaria_danada": [
        "farol roto poste alumbrado publico",
        "luminaria publica rota calle noche",
        "columna alumbrado doblada chocada",
    ],
    "urban_microbasural": [
        "microbasural esquina terreno baldio",
        "basural a cielo abierto barrio escombros",
        "acumulacion de basura escombros esquina",
    ],
    "urban_perdida_agua": [
        "perdida de agua caño roto vereda pavimento",
        "agua brotando asfalto calle rotura",
        "caño roto agua corriente calle inundada",
    ],
    "urban_senalizacion_danada": [
        "cartel pare caido transito chocado",
        "señal de transito rota vandalizada",
        "nomenclador de calle roto doblado",
    ],
}

def is_valid_real_photo(img_path: Path):
    """Filtra imágenes que sean artificiales, logos, cliparts o de mala calidad."""
    try:
        with Image.open(img_path) as im:
            w, h = im.size
            if w < 220 or h < 220:
                return False
            if im.format in ['GIF', 'ICO']:
                return False
            if im.mode == 'RGBA':
                extrema = im.getextrema()
                if len(extrema) == 4 and extrema[3][0] < 250:
                    return False  # Clipart o dibujo transparente
            # Convertir a RGB para asegurar compatibilidad
            im.convert('RGB')
            return True
    except Exception:
        return False

def build_real_balanced_dataset(target_per_category=30):
    base_dest = Path("local_images")
    temp_dir = Path("temp_downloads")
    
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Descargando y curando fotos 100% reales para las {len(CATEGORIES_QUERIES)} categorías...")
    
    curated_images = {}

    for cat_name, queries in CATEGORIES_QUERIES.items():
        print(f"\n📥 Procesando categoría: {cat_name}")
        valid_for_cat = []
        
        for q in queries:
            if len(valid_for_cat) >= target_per_category:
                break
            try:
                downloader.download(
                    q,
                    limit=20,
                    output_dir=str(temp_dir),
                    adult_filter_off=True,
                    force_replace=False,
                    timeout=10,
                    verbose=False
                )
                q_dir = temp_dir / q
                if q_dir.exists():
                    for f in q_dir.iterdir():
                        if f.is_file() and is_valid_real_photo(f):
                            valid_for_cat.append(f)
                            if len(valid_for_cat) >= target_per_category:
                                break
            except Exception as e:
                print(f"  ⚠️ Error en búsqueda '{q}': {e}")

        print(f"  ✅ Fotos reales válidas recolectadas: {len(valid_for_cat)}")
        curated_images[cat_name] = valid_for_cat

    # Limpiar carpetas train, val, test
    for split in ["train", "val", "test"]:
        sp = base_dest / split
        if sp.exists():
            shutil.rmtree(sp)
        sp.mkdir(parents=True, exist_ok=True)

    # Determinar el target parejo
    min_found = min(len(v) for v in curated_images.values())
    target = min(target_per_category, min_found)
    
    n_val = 5
    n_test = 3
    n_train = target - n_val - n_test
    
    print(f"\n==================================================")
    print(f"🎯 EMPAREJAMIENTO EXACTO POR CATEGORÍA: {target} FOTOS")
    print(f"   Train: {n_train} | Val: {n_val} | Test: {n_test} (por cada una de las 14 clases)")
    print(f"==================================================")

    for cat_name, file_list in curated_images.items():
        random.shuffle(file_list)
        selected = file_list[:target]
        
        train_set = selected[:n_train]
        val_set   = selected[n_train:n_train + n_val]
        test_set  = selected[n_train + n_val:target]
        
        for i, f in enumerate(train_set):
            d = base_dest / "train" / cat_name
            d.mkdir(parents=True, exist_ok=True)
            with Image.open(f) as im:
                im.convert('RGB').save(d / f"real_{i:03d}.jpg", "JPEG", quality=90)

        for i, f in enumerate(val_set):
            d = base_dest / "val" / cat_name
            d.mkdir(parents=True, exist_ok=True)
            with Image.open(f) as im:
                im.convert('RGB').save(d / f"real_{i:03d}.jpg", "JPEG", quality=90)

        for i, f in enumerate(test_set):
            d = base_dest / "test" / cat_name
            d.mkdir(parents=True, exist_ok=True)
            with Image.open(f) as im:
                im.convert('RGB').save(d / f"real_{i:03d}.jpg", "JPEG", quality=90)

    # Limpiar temp
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("\n🎉 ¡Descarga, curación de fotos reales y balanceo completado con éxito!")

if __name__ == "__main__":
    build_real_balanced_dataset(target_per_category=30)
