"""Completa candidatos públicos de Tránsito con Openverse y trazabilidad.

Uso: OPENVERSE_ACCESS_TOKEN='…' python ml/datasets/complete_transito_smart.py --apply
Sin --apply solo informa faltantes. Las consultas son específicas por carpeta.
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from ml.datasets.expand_balanced_100 import fingerprint, is_valid_photo

TARGET, API = 100, "https://api.openverse.org/v1/images/"
BASE = ROOT / "local_images" / "TRÁNSITO_Y_ESTACIONAMIENTO"
CACHE = ROOT / "ml" / "datasets" / "_cache" / "transit_smart"
CATEGORIES = {
 "ESTACIONAMIENTO_INDEBIDO/CORDON_AMARILLO":["car parked yellow curb","yellow kerb parking"],
 "ESTACIONAMIENTO_INDEBIDO/EN_MEDIO_DE_CALLE":["car blocking traffic lane","vehicle stopped middle street"],
 "ESTACIONAMIENTO_INDEBIDO/OBSTRUCCION_DE_ENTRADA":["car blocking driveway","vehicle blocking garage entrance"],
 "ESTACIONAMIENTO_INDEBIDO/SOBRE_VEREDA":["car parked sidewalk","vehicle parked pavement"],
 "ESTACIONAMIENTO_INDEBIDO/LUGAR_RESERVADO":["car disabled parking space","vehicle handicap parking"],
 "ESTACIONAMIENTO_INDEBIDO/LUGAR_PROHIBIDO":["car no parking sign","vehicle no parking zone"],
 "VEHICULO_ABANDONADO":["abandoned car urban street","derelict vehicle street"],
 "OBSTRUCCION_DE_CIRCULACION":["vehicle blocking road","car blocking street traffic"],
 "SENALIZACION_DE_TRANSITO":["damaged traffic sign street","broken road sign urban"],
 "SEMAFORO":["broken traffic light street","damaged traffic signal"],
}
def headers():
 t=os.environ.get("OPENVERSE_ACCESS_TOKEN")
 if not t: raise RuntimeError("Definí OPENVERSE_ACCESS_TOKEN fuera del repositorio.")
 return {"Authorization":f"Bearer {t}","User-Agent":"BolivarResponde/1.0 academic dataset"}
def get(url):
 with urlopen(Request(url,headers=headers()),timeout=45) as r:return json.loads(r.read().decode())
def fetch(url,path):
 try:
  with urlopen(Request(url,headers=headers()),timeout=60) as r:path.write_bytes(r.read())
  return is_valid_photo(path)
 except Exception: path.unlink(missing_ok=True);return False
def main():
 p=argparse.ArgumentParser();p.add_argument("--apply",action="store_true");p.add_argument("--category",choices=sorted(CATEGORIES));a=p.parse_args()
 chosen={a.category:CATEGORIES[a.category]} if a.category else CATEGORIES
 if not a.apply:
  for rel in chosen:
   n=sum(x.is_file() for x in (BASE/rel).glob("*"));print(f"{rel}: {n}/{TARGET}, faltan {max(0,TARGET-n)}")
  return
 CACHE.mkdir(parents=True,exist_ok=True);mp=CACHE/"manifest.json"; manifest=json.loads(mp.read_text()) if mp.exists() else [];urls={x["url"] for x in manifest}
 for rel,queries in chosen.items():
  folder=BASE/rel;folder.mkdir(parents=True,exist_ok=True);files=[x for x in folder.glob("*") if x.is_file() and is_valid_photo(x)];seen={fingerprint(x) for x in files}-{None};need=TARGET-len(files);added=0
  for query in queries:
   for page in range(1,4):
    if added>=need:break
    params=urlencode({"q":query,"license":"cc0,pdm","page_size":50,"page":page,"mature":"false"})
    for item in get(f"{API}?{params}").get("results",[]):
     if added>=need:break
     url=item.get("url"); tmp=CACHE/f"tmp_{len(manifest):05d}.jpg"
     if not url or url in urls or not fetch(url,tmp):continue
     fp=fingerprint(tmp)
     if not fp or fp in seen:tmp.unlink(missing_ok=True);continue
     final=folder/f"externa_{len(files)+added:03d}.jpg";tmp.replace(final);seen.add(fp);urls.add(url);added+=1
     manifest.append({"category":rel,"file":str(final.relative_to(ROOT)),"url":url,"landing_url":item.get("foreign_landing_url"),"title":item.get("title"),"creator":item.get("creator"),"license":item.get("license"),"provider":item.get("provider")})
    time.sleep(1)
  mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(f"{rel}: +{added}; total {len(files)+added}/{TARGET}")
if __name__=="__main__":main()
