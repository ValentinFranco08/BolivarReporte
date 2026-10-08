"""
sync_db.py — Sincroniza automáticamente la base de datos de desarrollo (SQLite bolivar_dev.db)
hacia PostgreSQL (Docker) para garantizar que tanto la ejecución manual como ./dev.sh
tengan exactamente los mismos reportes, fotos y mascotas.
"""

import os
import sqlite3

try:
    import psycopg2
except ImportError:
    psycopg2 = None

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_PATH = os.path.join(BACKEND_DIR, "bolivar_dev.db")
PG_URL = os.getenv("DATABASE_URL", "postgresql://bolivar_user:bolivar_password@localhost:5433/bolivar_responde")


def sync():
    if not psycopg2 or not os.path.exists(SQLITE_PATH):
        return

    # 1. Intentar conectar a PostgreSQL
    try:
        pg_conn = psycopg2.connect(PG_URL, connect_timeout=1)
        pg_cur = pg_conn.cursor()
    except Exception:
        # Si Postgres no está activo, no hay nada que sincronizar
        return

    try:
        # 2. Asegurar que las columnas existan en PostgreSQL
        pg_cur.execute("ALTER TABLE categories ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT TRUE;")
        pg_cur.execute("ALTER TABLE categories ADD COLUMN IF NOT EXISTS embedding_centroid TEXT;")
        pg_cur.execute("ALTER TABLE categories ADD COLUMN IF NOT EXISTS sample_count INTEGER DEFAULT 1;")

        pg_cur.execute("ALTER TABLE reports ADD COLUMN IF NOT EXISTS is_novel_category BOOLEAN DEFAULT FALSE;")
        pg_cur.execute("ALTER TABLE reports ADD COLUMN IF NOT EXISTS embedding TEXT;")
        pg_cur.execute("ALTER TABLE reports ADD COLUMN IF NOT EXISTS report_type animalreporttype DEFAULT 'PERDIDO';")
        pg_cur.execute("ALTER TABLE reports ADD COLUMN IF NOT EXISTS pet_type pettype DEFAULT 'PERRO';")
        pg_cur.execute("ALTER TABLE reports ADD COLUMN IF NOT EXISTS pet_name VARCHAR;")
        pg_cur.execute("ALTER TABLE reports ADD COLUMN IF NOT EXISTS pet_breed VARCHAR;")
        pg_cur.execute("ALTER TABLE reports ADD COLUMN IF NOT EXISTS color_description VARCHAR;")
        pg_cur.execute("ALTER TABLE reports ADD COLUMN IF NOT EXISTS health_status pethealthstatus DEFAULT 'SANO';")
        pg_cur.execute("ALTER TABLE reports ADD COLUMN IF NOT EXISTS contact_name VARCHAR;")
        pg_cur.execute("ALTER TABLE reports ADD COLUMN IF NOT EXISTS contact_phone VARCHAR;")
        pg_cur.execute("ALTER TABLE reports ADD COLUMN IF NOT EXISTS is_resolved BOOLEAN DEFAULT FALSE;")
        pg_cur.execute("ALTER TABLE feedback ADD COLUMN IF NOT EXISTS used_for_retraining BOOLEAN DEFAULT FALSE;")

        # 3. Verificar si Postgres ya tiene datos
        pg_cur.execute("SELECT count(*) FROM reports;")
        pg_count = pg_cur.fetchone()[0]

        sq_conn = sqlite3.connect(SQLITE_PATH)
        sq_conn.row_factory = sqlite3.Row
        sq_cur = sq_conn.cursor()
        sq_cur.execute("SELECT count(*) FROM reports;")
        sq_count = sq_cur.fetchone()[0]

        # Si están iguales, no hace falta re-sincronizar
        if pg_count == sq_count and pg_count > 0:
            pg_conn.commit()
            pg_conn.close()
            sq_conn.close()
            return

        # 4. Truncar y sincronizar desde SQLite
        pg_cur.execute("TRUNCATE users, categories, reports, ai_predictions, feedback, remum_records, remum_health_events, remum_godparents CASCADE;")

        # Migrar users
        sq_users = sq_cur.execute("SELECT * FROM users;").fetchall()
        if sq_users:
            u_cols = [k for k in sq_users[0].keys()]
            u_cols_str = ', '.join(u_cols)
            u_placeholders = ', '.join(['%s'] * len(u_cols))
            for u in sq_users:
                pg_cur.execute(f"INSERT INTO users ({u_cols_str}) VALUES ({u_placeholders});", [u[c] for c in u_cols])
            pg_cur.execute("SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 1) FROM users));")

        # Migrar categories
        sq_cats = sq_cur.execute("SELECT * FROM categories;").fetchall()
        if sq_cats:
            cat_cols = [k for k in sq_cats[0].keys()]
            cat_cols_str = ', '.join(cat_cols)
            cat_placeholders = ', '.join(['%s'] * len(cat_cols))
            for cat in sq_cats:
                c_vals = [bool(cat[c]) if c in ('active', 'is_verified') else cat[c] for c in cat_cols]
                pg_cur.execute(f"INSERT INTO categories ({cat_cols_str}) VALUES ({cat_placeholders});", c_vals)
            pg_cur.execute("SELECT setval('categories_id_seq', (SELECT COALESCE(MAX(id), 1) FROM categories));")

        # Migrar reports
        sq_reports = sq_cur.execute("SELECT * FROM reports;").fetchall()
        if sq_reports:
            cols = [k for k in sq_reports[0].keys()]
            cols_str = ', '.join(cols)
            placeholders = ', '.join(['%s'] * len(cols))
            for r in sq_reports:
                vals = [bool(r[c]) if c in ('is_resolved', 'is_novel_category') else r[c] for c in cols]
                pg_cur.execute(f"INSERT INTO reports ({cols_str}) VALUES ({placeholders});", vals)
            pg_cur.execute("SELECT setval('reports_id_seq', (SELECT COALESCE(MAX(id), 1) FROM reports));")

        # Migrar remum_records
        sq_remum = sq_cur.execute("SELECT * FROM remum_records;").fetchall()
        if sq_remum:
            r_cols = [k for k in sq_remum[0].keys()]
            r_cols_str = ', '.join(r_cols)
            r_placeholders = ', '.join(['%s'] * len(r_cols))
            for r in sq_remum:
                vals = [bool(r[c]) if c == 'is_community_pet' else r[c] for c in r_cols]
                pg_cur.execute(f"INSERT INTO remum_records ({r_cols_str}) VALUES ({r_placeholders});", vals)
            pg_cur.execute("SELECT setval('remum_records_id_seq', (SELECT COALESCE(MAX(id), 1) FROM remum_records));")

        pg_conn.commit()
        print("✅ Base de datos PostgreSQL sincronizada exitosamente con bolivar_dev.db")
    except Exception as e:
        print(f"⚠️ Error sincronizando DB: {e}")
    finally:
        pg_conn.close()
        sq_conn.close()


if __name__ == "__main__":
    sync()
