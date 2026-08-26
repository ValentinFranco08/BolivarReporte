#!/usr/bin/env python3
"""Descarga candidatos CC0/dominio público desde Openverse para revisión humana.

No escribe en ``local_images`` ni asigna etiquetas de entrenamiento: una búsqueda
no reemplaza la verificación visual de una situación de tránsito.

Uso: python ml/datasets/collect_public_domain_candidates.py --per-class 120
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.datasets.expand_balanced_100 import fingerprint, is_valid_photo

API = "https://api.openverse.org/v1/images/"
QUERIES = {
    "transit_cordon_amarillo": ["car parked yellow curb", "yellow curb parking"],
    "transit_en_medio_de_calle": ["car blocking street", "vehicle blocking lane"],
    "transit_obstruccion_de_entrada": ["car blocking driveway", "car parked driveway entrance"],
    "transit_sobre_vereda": ["car parked sidewalk", "vehicle on pavement"],
    "transit_lugar_reservado": ["car disabled parking space", "car handicap parking"],
    "transit_lugar_prohibido": ["car no parking sign", "car prohibited parking"],
    "transit_vehiculo_abandonado": ["abandoned car street", "abandoned vehicle urban"],
    "transit_obstruccion_de_circulacion": ["vehicle blocking road", "road blocked car"],
    "transit_semaforo_danado": ["broken traffic light", "damaged traffic signal"],
}


def headers() -> dict[str, str]:
    result = {"User-Agent": "BolivarResponde/1.0 academic dataset"}
    if token := os.environ.get("OPENVERSE_ACCESS_TOKEN"):
        result["Authorization"] = f"Bearer {token}"
    return result


def fetch_json(url: str) -> dict:
    request = Request(url, headers=headers())
    with urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-class", type=int, default=120)
    args = parser.parse_args()
    base = ROOT / "ml" / "datasets" / "_cache" / "public_domain_candidates"
    base.mkdir(parents=True, exist_ok=True)
    manifest_path = base / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    known_urls = {x["url"] for x in manifest}

    for label, queries in QUERIES.items():
        folder = base / label
        folder.mkdir(exist_ok=True)
        current = [p for p in folder.glob("*.jpg") if is_valid_photo(p)]
        fingerprints = {fingerprint(p) for p in current} - {None}
        for query in queries:
            if len(current) >= args.per_class:
                break
            # Openverse limita los resultados autenticados a 50 por página.
            params = urlencode({"q": query, "license": "cc0,pdm", "page_size": 50, "mature": "false"})
            data = fetch_json(f"{API}?{params}")
            for item in data.get("results", []):
                if len(current) >= args.per_class:
                    break
                url = item.get("url")
                if not url or url in known_urls:
                    continue
                path = folder / f"candidate_{len(current):03d}.jpg"
                try:
                    request = Request(url, headers=headers())
                    with urlopen(request, timeout=60) as response:
                        path.write_bytes(response.read())
                    fp = fingerprint(path)
                    if not is_valid_photo(path) or not fp or fp in fingerprints:
                        path.unlink(missing_ok=True)
                        continue
                except Exception:
                    path.unlink(missing_ok=True)
                    continue
                fingerprints.add(fp); current.append(path); known_urls.add(url)
                manifest.append({"suggested_label": label, "file": str(path.relative_to(ROOT)), "url": url,
                                 "landing_url": item.get("foreign_landing_url"), "title": item.get("title"),
                                 "creator": item.get("creator"), "license": item.get("license"),
                                 "provider": item.get("provider")})
            time.sleep(1)
        print(f"{label}: {len(current)} candidatos")
        # Checkpoint por categoría: permite reanudar tras un corte de red.
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"Manifest guardado en {manifest_path}")


if __name__ == "__main__":
    main()
