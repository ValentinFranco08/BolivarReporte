#!/usr/bin/env python3
"""
Completa local_images hasta 100 fotos por clase (70/15/15).

Fuentes (sin Bing):
  - Caché local (Road Issues, TACO, Bing previo no usado)
  - Wikimedia Commons (categorías + búsqueda File:)
  - Roboflow opcional si existe ROBOFLOW_API_KEY

Uso (desde la raíz, venv activo):
  python -u ml/datasets/fill_missing_to_100.py
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml" / "datasets"))

from build_dataset import build_dataset  # noqa: E402
from expand_balanced_100 import (  # noqa: E402
    CATEGORIES,
    N_TEST,
    N_TRAIN,
    N_VAL,
    TARGET_PER_CLASS,
    cache_dir,
    fingerprint,
    is_valid_photo,
    iter_images,
    save_jpeg,
)

random.seed(42)

UA = "BolivarResponde/1.0 (academic dataset fill; Python urllib)"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

ANIMAL_STREET = [
    "animals_animal_perdido",
    "animals_animal_suelto",
    "animals_animal_encontrado",
]

INJURED = "animals_posible_animal_herido"
LIGHT = "urban_luminaria_danada"

WIKI_STREET_CATS = [
    "Category:Feral dogs",
    "Category:Feral cats",
    "Category:Dogs in streets",
    "Category:Cats in streets",
    "Category:Street dogs",
]
WIKI_INJURED_CATS = [
    "Category:Wounded dogs",
    "Category:Injured animals",
]
WIKI_LIGHT_CATS = [
    "Category:Damaged lighting devices",
    "Category:Damaged utility poles",
]
WIKI_STREET_SEARCH = ["stray dog street", "stray cat street", "feral dog sidewalk", "homeless dog street"]
WIKI_INJURED_SEARCH = ["injured stray dog", "wounded dog street", "injured cat street"]
WIKI_LIGHT_SEARCH = ["broken street light pole", "damaged street lamp"]

INJURED_HINTS = ("injur", "wound", "hurt", "herid", "lastim", "rengo", "atropell")


def api_get(params: dict) -> dict:
    q = urlencode({**params, "format": "json"})
    req = Request(f"{COMMONS_API}?{q}", headers={"User-Agent": UA})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def commons_download(url: str, dest: Path) -> bool:
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = Request(url, headers={"User-Agent": UA})
        with urlopen(req, timeout=40) as resp:
            data = resp.read()
        if len(data) < 8_000:
            return False
        dest.write_bytes(data)
        if not is_valid_photo(dest):
            dest.unlink(missing_ok=True)
            return False
        return True
    except Exception:
        dest.unlink(missing_ok=True)
        return False


def commons_category_urls(title: str, limit: int) -> list[tuple[str, str]]:
    """Devuelve (filename, url) de archivos en una categoría."""
    out: list[tuple[str, str]] = []
    cont = {}
    while len(out) < limit:
        params = {
            "action": "query",
            "generator": "categorymembers",
            "gcmtitle": title,
            "gcmtype": "file",
            "gcmlimit": "50",
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
            "iiurlwidth": "1600",
        }
        params.update(cont)
        try:
            data = api_get(params)
        except Exception as e:
            print(f"     ⚠️  API {title}: {e}")
            break
        pages = (data.get("query") or {}).get("pages") or {}
        for page in pages.values():
            infos = page.get("imageinfo") or []
            if not infos:
                continue
            info = infos[0]
            mime = (info.get("mime") or "").lower()
            if not mime.startswith("image/"):
                continue
            url = info.get("thumburl") or info.get("url")
            name = page.get("title") or url
            if url:
                out.append((name, url))
        cont_raw = data.get("continue")
        if not cont_raw:
            break
        cont = cont_raw
        time.sleep(0.15)
    return out[:limit]


def commons_search_urls(query: str, limit: int) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    offset = 0
    while len(out) < limit:
        try:
            data = api_get(
                {
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srnamespace": "6",
                    "srlimit": str(min(50, limit - len(out))),
                    "sroffset": str(offset),
                }
            )
        except Exception as e:
            print(f"     ⚠️  search '{query}': {e}")
            break
        hits = ((data.get("query") or {}).get("search")) or []
        if not hits:
            break
        titles = [h["title"] for h in hits]
        offset += len(hits)
        try:
            info = api_get(
                {
                    "action": "query",
                    "titles": "|".join(titles[:50]),
                    "prop": "imageinfo",
                    "iiprop": "url|mime|size",
                    "iiurlwidth": "1600",
                }
            )
        except Exception:
            break
        pages = (info.get("query") or {}).get("pages") or {}
        for page in pages.values():
            infos = page.get("imageinfo") or []
            if not infos:
                continue
            inf = infos[0]
            if not (inf.get("mime") or "").lower().startswith("image/"):
                continue
            url = inf.get("thumburl") or inf.get("url")
            name = page.get("title") or url
            if url:
                out.append((name, url))
        if "continue" not in data and len(hits) < 50:
            break
        time.sleep(0.15)
    return out[:limit]


def collect_existing() -> dict[str, list[Path]]:
    base = ROOT / "local_images"
    out = {c: [] for c in CATEGORIES}
    for split in ("train", "val", "test"):
        for cat in CATEGORIES:
            d = base / split / cat
            if not d.is_dir():
                continue
            for img in d.iterdir():
                if img.is_file() and not img.name.startswith(".") and is_valid_photo(img):
                    out[cat].append(img)
    return out


def unused_from_dirs(dirs: list[Path], used: set[str], n: int) -> list[Path]:
    picked: list[Path] = []
    for folder in dirs:
        if not folder.exists():
            continue
        files = list(iter_images(folder))
        random.shuffle(files)
        for img in files:
            if ".cache" in img.parts:
                continue
            if len(picked) >= n:
                return picked
            if not is_valid_photo(img):
                continue
            fp = fingerprint(img)
            if not fp or fp in used:
                continue
            used.add(fp)
            picked.append(img)
    return picked


def fetch_commons(pairs: list[tuple[str, str]], dest_dir: Path, used: set[str], n: int) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    got: list[Path] = []
    for i, (name, url) in enumerate(pairs):
        if len(got) >= n:
            break
        dest = dest_dir / f"wiki_{i:04d}.jpg"
        if dest.exists() and is_valid_photo(dest):
            fp = fingerprint(dest)
            if fp and fp not in used:
                used.add(fp)
                got.append(dest)
            continue
        if not commons_download(url, dest):
            continue
        fp = fingerprint(dest)
        if not fp or fp in used:
            dest.unlink(missing_ok=True)
            continue
        used.add(fp)
        got.append(dest)
        if len(got) % 10 == 0:
            print(f"       … {len(got)}/{n}")
    return got


def rewrite_class(cat: str, files: list[Path]) -> None:
    selected = files[:TARGET_PER_CLASS]
    random.shuffle(selected)
    n = len(selected)
    if n >= TARGET_PER_CLASS:
        train, val, test = selected[:N_TRAIN], selected[N_TRAIN:N_TRAIN + N_VAL], selected[N_TRAIN + N_VAL : TARGET_PER_CLASS]
    else:
        n_val = max(0, int(round(n * 0.15)))
        n_test = max(0, int(round(n * 0.15)))
        n_train = n - n_val - n_test
        train = selected[:n_train]
        val = selected[n_train : n_train + n_val]
        test = selected[n_train + n_val :]

    base = ROOT / "local_images"
    for split in ("train", "val", "test"):
        d = base / split / cat
        if d.exists():
            for p in d.iterdir():
                if p.is_file():
                    p.unlink()
        d.mkdir(parents=True, exist_ok=True)

    for split, group in (("train", train), ("val", val), ("test", test)):
        d = base / split / cat
        for i, src in enumerate(group):
            save_jpeg(src, d / f"img_{i:03d}.jpg")
    print(f"  ▶ {cat}: {len(train)}/{len(val)}/{len(test)}  total={len(train)+len(val)+len(test)}")


def is_injured_name(name: str) -> bool:
    low = name.lower()
    return any(h in low for h in INJURED_HINTS)


def main() -> None:
    print("=== Completar a 100 por clase (Wikimedia + caché, sin Bing) ===")
    existing = collect_existing()
    used: set[str] = set()
    for cat, files in existing.items():
        for p in files:
            fp = fingerprint(p)
            if fp:
                used.add(fp)
        print(f"  {cat}: {len(files)}")

    missing = {c: TARGET_PER_CLASS - len(existing[c]) for c in CATEGORIES if len(existing[c]) < TARGET_PER_CLASS}
    if not missing:
        print("Ya hay 100 en todas las clases.")
        return
    print("Faltan:", missing)

    cache = cache_dir()
    extras: dict[str, list[Path]] = {c: [] for c in missing}

    # 1) Caché urbana
    if missing.get("urban_basura", 0) > 0:
        extras["urban_basura"] = unused_from_dirs(
            [cache / "road_issues" / "data" / "Public Cleanliness + Environmental Issues" / "Littering Garbage on Public Places Issues",
             cache / "taco" / "images"],
            used,
            missing["urban_basura"],
        )
        print(f"  caché basura: +{len(extras['urban_basura'])}")
    if missing.get("urban_senalizacion_danada", 0) > 0:
        extras["urban_senalizacion_danada"] = unused_from_dirs(
            [cache / "road_issues" / "data" / "Road Issues" / "Broken Road Sign Issues"],
            used,
            missing["urban_senalizacion_danada"],
        )
        print(f"  caché señal: +{len(extras['urban_senalizacion_danada'])}")
    if missing.get(LIGHT, 0) > 0:
        extras[LIGHT] = unused_from_dirs([cache / "bing" / "urban_luminaria_danada"], used, missing[LIGHT])
        print(f"  caché luminaria: +{len(extras[LIGHT])}")

    leftover_animals = unused_from_dirs([cache / "bing" / "animals_pool"], used, 200)
    print(f"  caché animals_pool sin usar: {len(leftover_animals)}")

    # 2) Wikimedia: heridos
    need_inj = missing.get(INJURED, 0)
    wiki_inj_pairs: list[tuple[str, str]] = []
    if need_inj > 0:
        print("  ↳ Wikimedia heridos…")
        for cat in WIKI_INJURED_CATS:
            wiki_inj_pairs.extend(commons_category_urls(cat, 80))
        for q in WIKI_INJURED_SEARCH:
            wiki_inj_pairs.extend(commons_search_urls(q, 80))
        seen_u = set()
        uniq = []
        for name, url in wiki_inj_pairs:
            if url in seen_u:
                continue
            seen_u.add(url)
            uniq.append((name, url))
        extras[INJURED] = fetch_commons(uniq, cache / "wiki" / "injured", used, need_inj)
        print(f"     heridos nuevos: {len(extras[INJURED])}")

    # 3) Wikimedia: callejeros
    need_street = sum(missing.get(c, 0) for c in ANIMAL_STREET) - len(leftover_animals)
    need_street = max(0, need_street)
    street_new: list[Path] = []
    if need_street > 0:
        print(f"  ↳ Wikimedia callejeros (objetivo {need_street})…")
        pairs: list[tuple[str, str]] = []
        for cat in WIKI_STREET_CATS:
            pairs.extend(commons_category_urls(cat, 120))
        for q in WIKI_STREET_SEARCH:
            pairs.extend(commons_search_urls(q, 120))
        seen_u = set()
        uniq = []
        for name, url in pairs:
            if url in seen_u:
                continue
            if is_injured_name(name):
                continue
            seen_u.add(url)
            uniq.append((name, url))
        street_new = fetch_commons(uniq, cache / "wiki" / "street_animals", used, need_street + 20)
        print(f"     callejeros nuevos: {len(street_new)}")

    street_pool = leftover_animals + street_new
    random.shuffle(street_pool)
    idx = 0
    for cat in ANIMAL_STREET:
        n = missing.get(cat, 0)
        extras[cat] = extras.get(cat, []) + street_pool[idx : idx + n]
        idx += n
        print(f"     asignados {cat}: {len(extras[cat])}")

    # 4) Wikimedia luminaria si aún falta
    still_light = missing.get(LIGHT, 0) - len(extras.get(LIGHT, []))
    if still_light > 0:
        print(f"  ↳ Wikimedia luminaria ({still_light})…")
        pairs = []
        for cat in WIKI_LIGHT_CATS:
            pairs.extend(commons_category_urls(cat, 60))
        for q in WIKI_LIGHT_SEARCH:
            pairs.extend(commons_search_urls(q, 40))
        extras[LIGHT] = extras.get(LIGHT, []) + fetch_commons(pairs, cache / "wiki" / "lights", used, still_light)
        print(f"     luminaria total extra: {len(extras[LIGHT])}")

    # 5) Reescribir solo clases incompletas
    print("\nReescribiendo clases incompletas…")
    for cat, n_miss in missing.items():
        merged = existing[cat] + extras.get(cat, [])
        # quitar duplicados por fingerprint
        seen = set()
        unique = []
        for p in merged:
            fp = fingerprint(p)
            if not fp or fp in seen:
                continue
            seen.add(fp)
            unique.append(p)
        if len(unique) < TARGET_PER_CLASS:
            print(f"  ⚠️  {cat}: {len(unique)}/{TARGET_PER_CLASS} (no se llegó al cupo)")
        rewrite_class(cat, unique)

    print("\nRegenerando dataset.json …")
    os.chdir(ROOT)
    build_dataset()
    print("\n✅ Completado.")


if __name__ == "__main__":
    main()
