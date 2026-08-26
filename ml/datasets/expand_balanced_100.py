#!/usr/bin/env python3
"""
Expande local_images a exactamente 100 fotos por cada una de las 14 clases
(70 train / 15 val / 15 test), sin sesgo de cantidad.

Fuentes (se usan las que respondan; el resto se completa con Bing curado):
  - HuggingFace Road Issues  → bache, calle_deteriorada, senalizacion_danada, basura
  - TACO                     → basura
  - Bing (consultas cívicas) → el resto y cualquier cupo incompleto
  - Pool único de callejeros → las 6 clases de animales (fotos distintas, texto las separa)

Uso (desde la raíz del repo, con el venv activo):
  python ml/datasets/expand_balanced_100.py
"""

from __future__ import annotations

import hashlib
import json
import random
import shutil
import sys
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml" / "datasets"))

from build_dataset import build_dataset  # noqa: E402

random.seed(42)

TARGET_PER_CLASS = 100
N_TRAIN, N_VAL, N_TEST = 70, 15, 15
NEW_CAP = 70
MIN_SIZE = 220

CATEGORIES = [
    "animals_animal_abandonado",
    "animals_animal_en_riesgo",
    "animals_animal_encontrado",
    "animals_animal_perdido",
    "animals_animal_suelto",
    "animals_posible_animal_herido",
    "urban_arbol_caido",
    "urban_bache",
    "urban_basura",
    "urban_calle_deteriorada",
    "urban_luminaria_danada",
    "urban_microbasural",
    "urban_perdida_agua",
    "urban_senalizacion_danada",
]

ANIMAL_CATS = [c for c in CATEGORIES if c.startswith("animals_")]

BING_QUERIES = {
    "animals_animal_abandonado": [
        "perro abandonado calle argentina foto",
        "perro atado arbol abandonado",
        "cachorro abandonado caja calle",
    ],
    "animals_animal_en_riesgo": [
        "perro en la ruta banquina peligro foto",
        "animal atrapado rejas rescate",
        "perro autopista argentina",
    ],
    "animals_animal_encontrado": [
        "perro encontrado plaza collar foto",
        "gato encontrado patio collar",
        "perro hallado calle barrio",
    ],
    "animals_animal_perdido": [
        "perro perdido cartel calle argentina",
        "mascota perdida perro barrio",
        "perro desorientado vereda",
    ],
    "animals_animal_suelto": [
        "perro suelto vereda barrio argentina",
        "caballo suelto calle ciudad",
        "perro callejero deambulando asfalto",
    ],
    "animals_posible_animal_herido": [
        "perro herido calle rescate foto",
        "perro rengo callejero lastimado",
        "gato atropellado vereda",
    ],
    "urban_arbol_caido": [
        "arbol caido calle tormenta argentina foto",
        "arbol caido sobre auto vereda",
        "arbol derribado viento asfalto",
    ],
    "urban_bache": [
        "bache profundo asfalto calle argentina foto",
        "pozo en la calzada bacheo",
        "pothole asphalt street close up",
    ],
    "urban_basura": [
        "bolsas de basura vereda esquina argentina",
        "basura acumulada calle contenedor",
        "litter garbage bags sidewalk photo",
    ],
    "urban_calle_deteriorada": [
        "pavimento roto grietas calle argentina",
        "calle deteriorada asfalto levantado",
        "cracked damaged road surface photo",
    ],
    "urban_luminaria_danada": [
        "luminaria publica rota poste calle",
        "farol caido alumbrado publico",
        "broken street light pole damaged",
    ],
    "urban_microbasural": [
        "microbasural baldio escombros argentina",
        "basural informal esquina barrio",
        "illegal dumping pile garbage lot photo",
    ],
    "urban_perdida_agua": [
        "perdida de agua asfalto calle argentina",
        "caño roto agua brotando vereda",
        "burst water main street geyser photo",
    ],
    "urban_senalizacion_danada": [
        "cartel pare caido transito argentina",
        "senal de transito doblada chocada",
        "broken bent traffic sign pole photo",
    ],
}

ANIMAL_POOL_QUERIES = [
    "perro callejero vereda argentina foto",
    "stray dog street sidewalk photo",
    "gato callejero calle barrio",
    "stray cat urban street photo",
    "perro mestizo calle asfalto",
]


def cache_dir() -> Path:
    d = ROOT / "ml" / "datasets" / "_cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def fingerprint(path: Path) -> str | None:
    try:
        with Image.open(path) as im:
            thumb = im.convert("RGB").resize((48, 48))
            return hashlib.md5(thumb.tobytes()).hexdigest()
    except Exception:
        return None


def is_valid_photo(path: Path) -> bool:
    try:
        with Image.open(path) as im:
            w, h = im.size
            if w < MIN_SIZE or h < MIN_SIZE:
                return False
            if im.format in {"GIF", "ICO"}:
                return False
            if max(w, h) / max(1, min(w, h)) > 3.2:
                return False
            rgb = im.convert("RGB")
            sample = rgb.resize((32, 32))
            corners = [
                sample.getpixel((0, 0)),
                sample.getpixel((31, 0)),
                sample.getpixel((0, 31)),
                sample.getpixel((31, 31)),
            ]
            if all(sum(c) / 3 > 245 for c in corners):
                return False
            return True
    except Exception:
        return False


def save_jpeg(src: Path, dest: Path) -> bool:
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as im:
            im.convert("RGB").save(dest, "JPEG", quality=90)
        return dest.exists() and dest.stat().st_size > 8_000
    except Exception:
        return False


def iter_images(folder: Path):
    if not folder.exists():
        return
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
            yield p


def collect_existing() -> dict[str, list[Path]]:
    base = ROOT / "local_images"
    out: dict[str, list[Path]] = {c: [] for c in CATEGORIES}
    for split in ("train", "val", "test"):
        for cat in CATEGORIES:
            d = base / split / cat
            if not d.exists():
                continue
            for img in d.iterdir():
                if img.is_file() and not img.name.startswith(".") and is_valid_photo(img):
                    out[cat].append(img)
    return out


def download_url(url: str, dest: Path, timeout: int = 25) -> bool:
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 BolivarRespondeDataset/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        if len(data) < 8_000:
            return False
        with Image.open(BytesIO(data)) as im:
            im.convert("RGB").save(dest, "JPEG", quality=90)
        return dest.exists()
    except Exception:
        return False


def _map_road_issues_path(path_str: str) -> str | None:
    mapping = (
        ("broken road sign", "urban_senalizacion_danada"),
        ("damaged road", "urban_calle_deteriorada"),
        ("pothole", "urban_bache"),
        ("littering", "urban_basura"),
    )
    low = path_str.lower()
    for key, cat in mapping:
        if key in low:
            return cat
    return None


def try_huggingface_road_issues() -> dict[str, list[Path]]:
    """Baja como máximo ~90 fotos por clase urbana, no el dataset entero."""
    dest = cache_dir() / "road_issues"
    dest.mkdir(parents=True, exist_ok=True)
    found: dict[str, list[Path]] = {}
    used: set[str] = set()

    print("  ↳ Reusando caché local de Road Issues…")
    for img in iter_images(dest):
        if ".cache" in img.parts:
            continue
        cat = _map_road_issues_path(str(img))
        if not cat or not is_valid_photo(img):
            continue
        fp = fingerprint(img)
        if not fp or fp in used:
            continue
        if len(found.get(cat, [])) >= NEW_CAP + 20:
            continue
        used.add(fp)
        found.setdefault(cat, []).append(img)

    missing = [
        c
        for c in (
            "urban_bache",
            "urban_calle_deteriorada",
            "urban_senalizacion_danada",
            "urban_basura",
        )
        if len(found.get(c, [])) < NEW_CAP
    ]
    if not missing:
        for cat, files in found.items():
            print(f"     {cat}: {len(files)} (caché)")
        return found

    try:
        from huggingface_hub import HfApi, hf_hub_download
    except Exception as e:
        print(f"  ⚠️  huggingface_hub no disponible ({e}).")
        return found

    print("  ↳ Listando archivos HF y bajando solo el cupo que falta…")
    try:
        files = HfApi().list_repo_files(
            repo_id="Programmer-RD-AI/road-issues-detection-dataset",
            repo_type="dataset",
        )
    except Exception as e:
        print(f"  ⚠️  No se pudo listar el repo HF ({e}).")
        return found

    buckets: dict[str, list[str]] = {c: [] for c in missing}
    for remote in files:
        if not remote.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue
        cat = _map_road_issues_path(remote)
        if cat in buckets:
            buckets[cat].append(remote)

    for cat in missing:
        random.shuffle(buckets[cat])
        need = NEW_CAP + 20 - len(found.get(cat, []))
        downloaded = 0
        for remote in buckets[cat]:
            if downloaded >= need:
                break
            try:
                local = Path(
                    hf_hub_download(
                        repo_id="Programmer-RD-AI/road-issues-detection-dataset",
                        filename=remote,
                        repo_type="dataset",
                        local_dir=str(dest),
                    )
                )
            except Exception:
                continue
            if not is_valid_photo(local):
                continue
            fp = fingerprint(local)
            if not fp or fp in used:
                continue
            used.add(fp)
            found.setdefault(cat, []).append(local)
            downloaded += 1
        print(f"     {cat}: {len(found.get(cat, []))} candidatas")
    return found


def try_taco() -> list[Path]:
    """TACO: baja annotations y como máximo 120 fotos de basura en contexto."""
    taco_dir = cache_dir() / "taco"
    taco_dir.mkdir(exist_ok=True)
    ann_path = taco_dir / "annotations.json"
    print("  ↳ TACO (basura en la calle)…")
    if not ann_path.exists():
        ok = download_url(
            "https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations.json",
            ann_path,
            timeout=60,
        )
        if not ok:
            # annotations.json no es jpeg; guardar crudo
            try:
                req = Request(
                    "https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations.json",
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                with urlopen(req, timeout=60) as resp:
                    ann_path.write_bytes(resp.read())
            except Exception as e:
                print(f"  ⚠️  No se pudo bajar annotations TACO ({e}).")
                return []
    try:
        data = json.loads(ann_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ⚠️  annotations TACO inválido ({e}).")
        return []

    urls = []
    for img in data.get("images", []):
        url = img.get("flickr_url") or img.get("coco_url") or img.get("file_name")
        if isinstance(url, str) and url.startswith("http"):
            urls.append(url)
    random.shuffle(urls)

    out: list[Path] = []
    img_dir = taco_dir / "images"
    for i, url in enumerate(urls):
        if len(out) >= NEW_CAP + 10:
            break
        dest = img_dir / f"taco_{i:04d}.jpg"
        if dest.exists() and is_valid_photo(dest):
            out.append(dest)
            continue
        if download_url(url, dest):
            if is_valid_photo(dest):
                out.append(dest)
            else:
                dest.unlink(missing_ok=True)
    print(f"     TACO fotos válidas: {len(out)}")
    return out


def bing_download(query: str, limit: int, out_dir: Path) -> list[Path]:
    try:
        from bing_image_downloader import downloader
    except ImportError:
        print("  ⚠️  Falta bing_image_downloader. pip install bing-image-downloader")
        return []
    try:
        downloader.download(
            query,
            limit=limit,
            output_dir=str(out_dir),
            adult_filter_off=True,
            force_replace=False,
            timeout=12,
            verbose=False,
        )
    except Exception as e:
        print(f"     query '{query}': {e}")
        return []
    q_dir = out_dir / query
    return [p for p in iter_images(q_dir) if is_valid_photo(p)]


def fill_with_bing(needed: dict[str, int]) -> dict[str, list[Path]]:
    got: dict[str, list[Path]] = {c: [] for c in needed}
    tmp = cache_dir() / "bing"
    tmp.mkdir(exist_ok=True)

    animal_need = sum(needed.get(c, 0) for c in ANIMAL_CATS)
    animal_pool: list[Path] = []
    if animal_need:
        print(f"  ↳ Bing pool animales (hace falta ~{animal_need})…")
        for q in ANIMAL_POOL_QUERIES:
            if len(animal_pool) >= animal_need + 40:
                break
            animal_pool.extend(bing_download(q, 30, tmp / "animals_pool"))
        seen = set()
        unique = []
        for p in animal_pool:
            fp = fingerprint(p)
            if not fp or fp in seen:
                continue
            seen.add(fp)
            unique.append(p)
        random.shuffle(unique)
        idx = 0
        for cat in ANIMAL_CATS:
            n = needed.get(cat, 0)
            got[cat] = unique[idx : idx + n]
            idx += n
            print(f"     {cat}: {len(got[cat])} del pool callejero")

    for cat, n in needed.items():
        if cat in ANIMAL_CATS:
            continue
        if n <= 0:
            continue
        print(f"  ↳ Bing {cat} (objetivo {n})…")
        files: list[Path] = []
        seen: set[str] = set()
        for q in BING_QUERIES.get(cat, [cat]):
            if len(files) >= n:
                break
            for p in bing_download(q, 28, tmp / cat):
                fp = fingerprint(p)
                if not fp or fp in seen:
                    continue
                seen.add(fp)
                files.append(p)
                if len(files) >= n:
                    break
        got[cat] = files[:n]
        print(f"     {cat}: {len(got[cat])}")
    return got


def take_unique(candidates: list[Path], n: int, used_fps: set[str]) -> list[Path]:
    picked = []
    for p in candidates:
        if len(picked) >= n:
            break
        if not is_valid_photo(p):
            continue
        fp = fingerprint(p)
        if not fp or fp in used_fps:
            continue
        used_fps.add(fp)
        picked.append(p)
    return picked


def write_balanced(final: dict[str, list[Path]]) -> None:
    base = ROOT / "local_images"
    backup = ROOT / "local_images_before_100"
    if base.exists() and not backup.exists():
        shutil.copytree(base, backup)
        print(f"  💾 Backup de las 30 originales → {backup.name}")

    staging = ROOT / "local_images_staging_100"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()

    counts = {}
    for cat, files in final.items():
        random.shuffle(files)
        selected = files[:TARGET_PER_CLASS]
        if len(selected) < TARGET_PER_CLASS:
            print(f"  ⚠️  {cat}: solo {len(selected)}/{TARGET_PER_CLASS}")
        train = selected[:N_TRAIN]
        val = selected[N_TRAIN : N_TRAIN + N_VAL]
        test = selected[N_TRAIN + N_VAL : N_TRAIN + N_VAL + N_TEST]
        for split, group in (("train", train), ("val", val), ("test", test)):
            d = staging / split / cat
            d.mkdir(parents=True, exist_ok=True)
            for i, src in enumerate(group):
                save_jpeg(src, d / f"img_{i:03d}.jpg")
        counts[cat] = (len(train), len(val), len(test))

    for split in ("train", "val", "test"):
        dest = base / split
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(staging / split, dest)
    shutil.rmtree(staging, ignore_errors=True)

    print("\n📊 Split final por clase (train/val/test):")
    for cat in CATEGORIES:
        t, v, te = counts.get(cat, (0, 0, 0))
        print(f"  {cat}: {t}/{v}/{te}  total={t + v + te}")


def main() -> None:
    print("=== Expandir dataset a 100 por clase (sin sesgo de cantidad) ===")
    existing = collect_existing()
    used_fps: set[str] = set()
    keep_existing: dict[str, list[Path]] = {}
    for cat in CATEGORIES:
        keep_existing[cat] = take_unique(existing[cat], 30, used_fps)
        print(f"  existentes {cat}: {len(keep_existing[cat])}")

    sourced: dict[str, list[Path]] = {c: [] for c in CATEGORIES}

    hf = try_huggingface_road_issues()
    for cat, files in hf.items():
        sourced[cat].extend(files)

    taco = try_taco()
    sourced["urban_basura"].extend(taco)

    still_needed: dict[str, int] = {}
    preview_fps = set(used_fps)
    for cat in CATEGORIES:
        already = take_unique(sourced[cat], NEW_CAP, preview_fps)
        sourced[cat] = already
        still_needed[cat] = max(0, NEW_CAP - len(already))

    if any(v > 0 for v in still_needed.values()):
        print("\nCompletando cupos con Bing curado…")
        bing = fill_with_bing(still_needed)
        for cat, files in bing.items():
            sourced[cat].extend(files)

    final: dict[str, list[Path]] = {}
    used_fps = set()
    for cat in CATEGORIES:
        kept = take_unique(keep_existing[cat], 30, used_fps)
        extra = take_unique(sourced[cat], NEW_CAP, used_fps)
        merged = kept + extra
        if len(merged) < TARGET_PER_CLASS:
            extra2 = take_unique(existing[cat] + sourced[cat], TARGET_PER_CLASS - len(merged), used_fps)
            merged.extend(extra2)
        final[cat] = merged
        print(f"  ▶ {cat}: {len(kept)} viejas + {len(extra)} nuevas = {len(merged)}")

    write_balanced(final)
    print("\nRegenerando ml/datasets/dataset.json …")
    import os

    os.chdir(ROOT)
    build_dataset()
    print("\n✅ Listo. 14 clases × 100 fotos. Backup en local_images_before_100/")


if __name__ == "__main__":
    main()
