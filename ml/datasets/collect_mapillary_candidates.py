#!/usr/bin/env python3
"""Descarga candidatos urbanos de Mapillary sin persistir el token.

Uso: MAPILLARY_TOKEN='...' python ml/datasets/collect_mapillary_candidates.py
Los archivos se guardan como candidatos pendientes de etiquetado, nunca se
incorporan automáticamente a una clase de entrenamiento.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.datasets.expand_balanced_100 import fingerprint, is_valid_photo

API = "https://graph.mapillary.com/images"
# Buenos Aires, La Plata, Rosario, Córdoba, Mendoza, Mar del Plata.
BBOXES = [
    "-58.395,-34.625,-58.375,-34.605", "-58.430,-34.620,-58.410,-34.600",
    "-57.960,-34.935,-57.940,-34.915", "-60.670,-32.965,-60.650,-32.945",
    "-64.200,-31.430,-64.180,-31.410", "-68.855,-32.900,-68.835,-32.880",
    "-57.570,-38.010,-57.550,-37.990",
]


def get(url: str) -> dict:
    for attempt in range(4):
        try:
            with urlopen(Request(url, headers={"User-Agent": "BolivarRespondeDataset/1.0"}), timeout=60) as r:
                return json.loads(r.read().decode())
        except HTTPError as error:
            if error.code not in {429, 500, 502, 503} or attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("Mapillary no respondió")


def main() -> None:
    token = os.environ.get("MAPILLARY_TOKEN")
    if not token:
        raise SystemExit("Definí MAPILLARY_TOKEN solo para esta ejecución; no lo agregues al repositorio.")
    destination = ROOT / "ml" / "datasets" / "_cache" / "mapillary_candidates"
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    known_ids = {item["id"] for item in manifest}
    used = {fingerprint(p) for p in destination.glob("*.jpg")} - {None}
    for bbox in BBOXES:
        query = urlencode({"access_token": token, "fields": "id,thumb_2048_url,captured_at,computed_geometry", "bbox": bbox, "limit": 200})
        data = get(f"{API}?{query}")
        for item in data.get("data", []):
            image_id, url = item.get("id"), item.get("thumb_2048_url")
            if not image_id or not url or image_id in known_ids:
                continue
            path = destination / f"{image_id}.jpg"
            try:
                with urlopen(Request(url, headers={"User-Agent": "BolivarRespondeDataset/1.0"}), timeout=60) as r:
                    path.write_bytes(r.read())
                fp = fingerprint(path)
                if not is_valid_photo(path) or not fp or fp in used:
                    path.unlink(missing_ok=True)
                    continue
                used.add(fp); known_ids.add(image_id)
                manifest.append({"id": image_id, "file": path.name, "captured_at": item.get("captured_at"), "geometry": item.get("computed_geometry"), "source": f"https://www.mapillary.com/app/?pKey={image_id}"})
            except Exception:
                path.unlink(missing_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"Candidatos descargados: {len(manifest)}. Requieren etiqueta humana antes de entrenar.")


if __name__ == "__main__":
    main()
