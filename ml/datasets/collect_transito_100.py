#!/usr/bin/env python3
"""Recolecta candidatos de Wikimedia Commons para Tránsito y Estacionamiento.

Descarga fotografías con licencia trazable, filtra tamaño/formato/fondos blancos y
duplicados perceptuales, y crea una partición 70/15/15. No usa Bing. Cada archivo
queda registrado en ``ml/datasets/_cache/transit/manifest.json`` para revisión.

Uso: python ml/datasets/collect_transito_100.py
     python ml/datasets/collect_transito_100.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.datasets.expand_balanced_100 import (
    N_TEST, N_TRAIN, N_VAL, TARGET_PER_CLASS, fingerprint,
    is_valid_photo, save_jpeg,
)

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "BolivarResponde/1.0 (academic, contact: dataset-maintainer)"
RANDOM = random.Random(42)

# Consultas deliberadamente específicas: el nombre/preview no sustituye revisión humana.
QUERIES = {
    "transit_cordon_amarillo": ["car parked yellow curb", "vehicle yellow kerb parking", "yellow curb no parking car"],
    "transit_en_medio_de_calle": ["car parked middle of street", "vehicle blocking lane street", "car stopped in traffic lane"],
    "transit_obstruccion_de_entrada": ["car blocking driveway", "vehicle blocking garage entrance", "car parked in front of driveway"],
    "transit_sobre_vereda": ["car parked on sidewalk", "vehicle parked pavement sidewalk", "car blocking pedestrian sidewalk"],
    "transit_lugar_reservado": ["car parked disabled parking space", "vehicle handicap parking space", "car in accessible parking space"],
    "transit_lugar_prohibido": ["car parked no parking sign", "vehicle in no parking zone", "car parked prohibited parking"],
    "transit_vehiculo_abandonado": ["abandoned car street", "abandoned vehicle roadside", "derelict car urban street"],
    "transit_obstruccion_de_circulacion": ["vehicle blocking road", "car blocking street traffic", "road blocked by vehicle"],
    "transit_semaforo_danado": ["broken traffic light", "damaged traffic signal", "fallen traffic light"],
}

# Categorías de Commons: aportan más variedad que la búsqueda de títulos de archivo.
COMMONS_CATEGORIES = {
    "transit_cordon_amarillo": ["Category:Illegal parking", "Category:Illegal parking in Berlin"],
    "transit_en_medio_de_calle": ["Category:Illegal parking", "Category:Streets"],
    "transit_obstruccion_de_entrada": ["Category:Illegal parking", "Category:Driveways"],
    "transit_sobre_vereda": ["Category:Vehicles parked on sidewalks in Taiwan", "Category:Sidewalk parking in Taiwan"],
    "transit_lugar_reservado": ["Category:Illegal parking", "Category:Parking spaces for disabled people"],
    "transit_lugar_prohibido": ["Category:Illegal parking", "Category:Illegal parking in Munich"],
    "transit_vehiculo_abandonado": ["Category:Abandoned cars"],
    "transit_obstruccion_de_circulacion": ["Category:Illegal parking", "Category:Streets"],
    "transit_semaforo_danado": ["Category:Traffic lights", "Category:Traffic lights in disrepair"],
}


def api(params: dict) -> dict:
    request = Request(f"{COMMONS_API}?{urlencode({**params, 'format': 'json'})}", headers={"User-Agent": USER_AGENT})
    for attempt in range(5):
        try:
            with urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code != 429 or attempt == 4:
                raise
            delay = 5 * (2 ** attempt)
            print(f"  Wikimedia limitó la tasa; reintento en {delay}s…")
            time.sleep(delay)
    raise RuntimeError("No se pudo consultar Wikimedia")


def search(query: str, limit: int = 50) -> list[dict]:
    data = api({"action": "query", "generator": "search", "gsrsearch": query,
                "gsrnamespace": 6, "gsrlimit": limit, "prop": "imageinfo",
                "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1600})
    return list((data.get("query") or {}).get("pages", {}).values())


def category_members(category: str, limit: int = 100) -> list[dict]:
    data = api({"action": "query", "generator": "categorymembers", "gcmtitle": category,
                "gcmtype": "file", "gcmlimit": limit, "prop": "imageinfo",
                "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1600})
    return list((data.get("query") or {}).get("pages", {}).values())


def download(url: str, destination: Path) -> bool:
    try:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            payload = response.read()
        if len(payload) < 8_000:
            return False
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        if not is_valid_photo(destination):
            destination.unlink(missing_ok=True)
            return False
        return True
    except Exception:
        destination.unlink(missing_ok=True)
        return False


def existing(category: str) -> list[Path]:
    dataset_files = [p for split in ("train", "val", "test") for p in (ROOT / "local_images" / split / category).glob("*")]
    cache_files = list((ROOT / "ml" / "datasets" / "_cache" / "transit" / category).glob("*"))
    return [p for p in dataset_files + cache_files if p.is_file() and is_valid_photo(p)]


def rewrite(category: str, files: list[Path]) -> None:
    RANDOM.shuffle(files)
    for split, group in (("train", files[:N_TRAIN]), ("val", files[N_TRAIN:N_TRAIN + N_VAL]), ("test", files[N_TRAIN + N_VAL:TARGET_PER_CLASS])):
        folder = ROOT / "local_images" / split / category
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob("*"):
            if old.is_file(): old.unlink()
        for index, source in enumerate(group):
            save_jpeg(source, folder / f"img_{index:03d}.jpg")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--per-class", type=int, default=TARGET_PER_CLASS)
    parser.add_argument("--category", choices=sorted(QUERIES), help="Reanuda una única clase para respetar límites de la fuente.")
    args = parser.parse_args()
    if args.per_class != TARGET_PER_CLASS:
        raise SystemExit("Este script preserva el split contractual 70/15/15; use 100 imágenes por clase.")

    cache = ROOT / "ml" / "datasets" / "_cache" / "transit"
    manifest_path = cache / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    all_fingerprints = {fingerprint(p) for category in QUERIES for p in existing(category)} - {None}

    selected = {args.category: QUERIES[args.category]} if args.category else QUERIES
    for category, queries in selected.items():
        pool = existing(category)
        seen = {fingerprint(p) for p in pool} - {None}
        print(f"{category}: {len(pool)}/{TARGET_PER_CLASS}")
        candidate_groups = [(f"category:{name}", lambda name=name: category_members(name)) for name in COMMONS_CATEGORIES[category]]
        candidate_groups += [(query, lambda query=query: search(query)) for query in queries]
        for query, fetch in candidate_groups:
            if len(pool) >= TARGET_PER_CLASS: break
            try:
                candidates = fetch()
            except Exception as error:
                print(f"  API falló para {query!r}: {error}")
                continue
            for page in candidates:
                if len(pool) >= TARGET_PER_CLASS: break
                info = (page.get("imageinfo") or [{}])[0]
                if not (info.get("mime") or "").startswith("image/") or min(info.get("width", 0), info.get("height", 0)) < 400:
                    continue
                url = info.get("thumburl") or info.get("url")
                if not url: continue
                destination = cache / category / f"commons_{len(pool):03d}.jpg"
                if args.dry_run:
                    print(f"  candidato: {page.get('title')}")
                    continue
                if not download(url, destination): continue
                fp = fingerprint(destination)
                if not fp or fp in seen or fp in all_fingerprints:
                    destination.unlink(missing_ok=True)
                    continue
                seen.add(fp); all_fingerprints.add(fp); pool.append(destination)
                manifest.append({"category": category, "file": str(destination.relative_to(ROOT)), "title": page.get("title"), "source_url": info.get("descriptionurl"), "image_url": info.get("url"), "license": ((info.get("extmetadata") or {}).get("LicenseShortName") or {}).get("value", "unknown")})
            # Commons recomienda solicitudes seriales y moderadas para procesos batch.
            time.sleep(2)
        if not args.dry_run and len(pool) >= TARGET_PER_CLASS:
            rewrite(category, pool[:TARGET_PER_CLASS])
        print(f"  resultado: {len(pool)}/{TARGET_PER_CLASS}")

    if not args.dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
        print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
