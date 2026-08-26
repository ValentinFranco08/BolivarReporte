import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import Report

# Centro aproximado de Bolívar
BOLIVAR_LAT = -36.2312
BOLIVAR_LNG = -61.1136

def update_existing_reports():
    db = SessionLocal()
    try:
        reports = db.query(Report).filter(Report.latitude == None).all()
        for r in reports:
            # Añadir un pequeño offset aleatorio para que no estén todos exactamente en el mismo lugar
            lat_offset = random.uniform(-0.01, 0.01)
            lng_offset = random.uniform(-0.01, 0.01)
            
            r.latitude = BOLIVAR_LAT + lat_offset
            r.longitude = BOLIVAR_LNG + lng_offset
            r.address = "Simulado, San Carlos de Bolívar"
        
        db.commit()
        print(f"Se actualizaron {len(reports)} reportes.")
    except Exception as e:
        print(e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_existing_reports()
