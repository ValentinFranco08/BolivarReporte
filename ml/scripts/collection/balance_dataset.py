import os
import shutil
import random
from pathlib import Path
from PIL import Image

# Fijar semilla
random.seed(42)

def is_artificial_or_low_quality(img_path: Path):
    """Detecta si una imagen es clipart, transparente, corrupta o de tamaño no realista."""
    try:
        with Image.open(img_path) as im:
            w, h = im.size
            # 1. Miniaturas o iconos muy pequeños
            if w < 180 or h < 180:
                return True, f"Tamaño diminuto ({w}x{h})"
            
            # 2. GIFs animados
            if im.format == 'GIF':
                return True, "Formato GIF"
                
            # 3. PNGs con transparencia (cliparts / dibujos vectoriales)
            if im.mode == 'RGBA':
                extrema = im.getextrema()
                if len(extrema) == 4 and extrema[3][0] < 250:
                    return True, f"Clipart transparente RGBA ({w}x{h})"

            # 4. Gráficos o dibujos vectoriales convertidos a RGB con fondos planos/cuadrados sospechosos
            if img_path.name in [
                "web_11.png", "web_12.png", "web_23.png", "web_26.png", 
                "web_31.png", "web_33.png", "web_13.webp"
            ]:
                return True, "Gráfico / Ilustración / Clipart"

            return False, "OK"
    except Exception as e:
        return True, f"Corrupto ({e})"

def clean_and_balance_dataset(target_per_category=30):
    base_path = Path("local_images")
    quarantine_dir = Path("local_images_removed")
    staging_dir = Path("local_images_staging")
    
    quarantine_dir.mkdir(exist_ok=True)
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(exist_ok=True)
    
    # 1. Agrupar todas las imágenes por categoría
    category_images = {}
    
    for split_dir in [base_path / "train", base_path / "val", base_path / "test"]:
        if not split_dir.exists():
            continue
        for cat_dir in split_dir.iterdir():
            if not cat_dir.is_dir():
                continue
            cat_name = cat_dir.name
            if cat_name not in category_images:
                category_images[cat_name] = []
            
            for img_file in cat_dir.iterdir():
                if img_file.is_file() and not img_file.name.startswith('.'):
                    category_images[cat_name].append(img_file)

    print(f"📊 Categorías encontradas: {len(category_images)}")
    
    # 2. Filtrar imágenes artificiales o inválidas y mover válidas a staging
    filtered_categories = {}
    removed_count = 0
    
    for cat_name, file_list in sorted(category_images.items()):
        valid_files = []
        for img_file in file_list:
            if not img_file.exists():
                continue
            is_bad, reason = is_artificial_or_low_quality(img_file)
            if is_bad:
                dest = quarantine_dir / f"{cat_name}_{img_file.name}"
                shutil.move(str(img_file), str(dest))
                removed_count += 1
                print(f"  ❌ Removido ({reason}): {cat_name}/{img_file.name}")
            else:
                cat_staging = staging_dir / cat_name
                cat_staging.mkdir(parents=True, exist_ok=True)
                staged_path = cat_staging / img_file.name
                shutil.move(str(img_file), str(staged_path))
                valid_files.append(staged_path)
        filtered_categories[cat_name] = valid_files

    print(f"\n🧹 Total de imágenes artificiales/baja calidad removidas: {removed_count}")
    
    # 3. Determinar cantidad mínima para emparejar
    min_available = min(len(files) for files in filtered_categories.values())
    target = min(target_per_category, min_available)
    print(f"\n🎯 Emparejando todas las categorías a exactamente: {target} imágenes reales c/u")
    
    # Splits exactos y balanceados (ej. 23 train, 4 val, 3 test = 30)
    n_val = max(1, int(target * 0.15))
    n_test = max(1, int(target * 0.10))
    n_train = target - n_val - n_test
    print(f"   Por categoría: Train = {n_train} | Val = {n_val} | Test = {n_test}")

    # Limpiar y rearmar local_images
    for split in ["train", "val", "test"]:
        split_path = base_path / split
        if split_path.exists():
            shutil.rmtree(split_path)
        split_path.mkdir(parents=True, exist_ok=True)

    for cat_name, file_list in sorted(filtered_categories.items()):
        random.shuffle(file_list)
        selected = file_list[:target]
        
        train_files = selected[:n_train]
        val_files = selected[n_train:n_train + n_val]
        test_files = selected[n_train + n_val:target]
        
        # Mover sobrantes a quarantine_dir para no perderlos
        surplus = file_list[target:]
        for s in surplus:
            dest = quarantine_dir / f"surplus_{cat_name}_{s.name}"
            shutil.move(str(s), str(dest))

        # Crear carpetas de destino y mover desde staging
        for f in train_files:
            dest_dir = base_path / "train" / cat_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(dest_dir / f.name))

        for f in val_files:
            dest_dir = base_path / "val" / cat_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(dest_dir / f.name))

        for f in test_files:
            dest_dir = base_path / "test" / cat_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(dest_dir / f.name))

    if staging_dir.exists():
        shutil.rmtree(staging_dir)

    print(f"\n✅ Dataset balanceado reorganizado exitosamente:")
    print(f"   Total de imágenes: {target * len(filtered_categories)} ({target} x {len(filtered_categories)} clases)")
    print(f"   Train total: {n_train * len(filtered_categories)} ({n_train} x {len(filtered_categories)})")
    print(f"   Val total:   {n_val * len(filtered_categories)} ({n_val} x {len(filtered_categories)})")
    print(f"   Test total:  {n_test * len(filtered_categories)} ({n_test} x {len(filtered_categories)})")

if __name__ == "__main__":
    clean_and_balance_dataset(target_per_category=30)
