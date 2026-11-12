"""
Completa las categorias de TRANSITO_Y_ESTACIONAMIENTO hasta 100 fotos cada una.
No borra las fotos existentes, solo agrega las que faltan.
"""
import shutil
import random
from pathlib import Path
from PIL import Image
from bing_image_downloader import downloader

random.seed(42)
TARGET = 100

BASE_DIR = Path("local_images/TRÁNSITO_Y_ESTACIONAMIENTO")

QUERIES = {
    "ESTACIONAMIENTO_INDEBIDO": [
        "auto mal estacionado vereda argentina",
        "vehiculo en vereda estacionamiento prohibido",
        "coche estacionado en doble fila calle",
        "auto sobre la acera obstaculizando paso",
        "estacionamiento indebido multa argentina",
        "vehiculo estacionado zona prohibida señal",
    ],
    "OBSTRUCCION_DE_CIRCULACION": [
        "contenedor escombros obstruye calle trafico",
        "vehiculo mal estacionado bloquea calle",
        "obstruccion via publica camion descarga",
        "contenedor obra bloquea calzada calle",
        "auto cruzado bloqueando interseccion",
        "via bloqueada accidente calle ciudad",
    ],
    "SEMAFORO": [
        "semaforo roto apagado calle argentina",
        "semaforo danado sin funcionar ciudad",
        "semaforo caido poste accidente",
        "semaforo vandalizdo roto barrio",
        "traffic light broken street",
        "semaforo parpadeando falla electrica calle",
    ],
    "SENALIZACION_DE_TRANSITO": [
        "senal transito calle argentina",
        "cartel vial deteriorado roto",
        "señal de trafico doblada vandalizada",
        "señalizacion vial mal estado calle",
        "cartel pare calle argentina",
        "nomenclador calle senal vial ciudad",
    ],
    "VEHICULO_ABANDONADO": [
        "auto abandonado calle argentina oxidado",
        "vehiculo abandonado sin patente calle",
        "coche viejo abandonado vereda barrio",
        "camioneta abandonada calle oxidada",
        "auto chatarra abandonado vereda",
        "vehiculo destartalado abandonado calle argentina",
    ],
}


def is_valid(img_path, min_size=220):
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


def count_photos(cat_dir):
    if not cat_dir.exists():
        return 0
    return len([f for f in cat_dir.iterdir() if f.is_file()])


def complete():
    temp_dir = Path("temp_transito")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nObjetivo: {TARGET} fotos por categoria en TRANSITO_Y_ESTACIONAMIENTO\n")

    for cat_name, queries in QUERIES.items():
        cat_dir = BASE_DIR / cat_name
        cat_dir.mkdir(parents=True, exist_ok=True)
        existing = count_photos(cat_dir)

        print(f"[{cat_name}]: {existing} fotos actuales", end="", flush=True)

        if existing >= TARGET:
            print(f" -> Ya completa, se omite.")
            continue

        needed = TARGET - existing
        print(f" -> Faltan {needed} fotos, descargando...")

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
                    timeout=12,
                    verbose=False
                )
                q_dir = temp_dir / q
                if q_dir.exists():
                    for f in sorted(q_dir.iterdir()):
                        if f.is_file() and is_valid(f):
                            valid.append(f)
                            if len(valid) >= needed + 10:
                                break
            except Exception as e:
                print(f"  Advertencia '{q}': {e}")

        if not valid:
            print(f"  ERROR: No se encontraron fotos para {cat_name}")
            continue

        random.shuffle(valid)
        start_idx = existing
        saved = 0
        for i, f in enumerate(valid[:needed]):
            try:
                with Image.open(f) as im:
                    out = cat_dir / f"real_{start_idx + i:03d}.jpg"
                    im.convert('RGB').save(out, "JPEG", quality=90)
                    saved += 1
            except Exception:
                pass

        final = count_photos(cat_dir)
        print(f"  OK: ahora tiene {final} fotos.")

    shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n" + "=" * 60)
    print("RESUMEN FINAL - TRANSITO_Y_ESTACIONAMIENTO:")
    for cat_name in QUERIES:
        cat_dir = BASE_DIR / cat_name
        total = count_photos(cat_dir)
        status = "OK" if total >= TARGET else f"INCOMPLETA ({total}/{TARGET})"
        print(f"  [{status}] {cat_name}: {total} fotos")
    print("=" * 60)
    print("\nListo! Ahora integra estas categorias al dataset principal.")


if __name__ == "__main__":
    complete()
