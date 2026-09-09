import json
from app.llm_categorizer import suggest_category
from app import crud, models


def test_suggest_category_municipal_heuristics():
    # 1. Animales
    sug_anim = suggest_category("hay un enjambre de avispas agresivas cerca de los juegos")
    assert sug_anim["area"] == "Animales"
    assert "avispa" in sug_anim["name"]

    # 2. Infraestructura
    sug_infra = suggest_category("bache profundo y cable con chispas colgando")
    assert sug_infra["area"] == "Infraestructura"

    # 3. Tránsito
    sug_trans = suggest_category("camioneta estacionada tapando la rampa de discapacitados")
    assert sug_trans["area"] == "Tránsito y Estacionamiento"

    # 4. Higiene Urbana
    sug_hig = suggest_category("acumulacion de basura y residuos en terreno baldio")
    assert sug_hig["area"] == "Higiene Urbana"


def test_admin_category_management_endpoints(client, db):
    # Registrar y loguear usuario
    user_data = {"email": "admin@bolivar.gob.ar", "password": "password123", "name": "Admin Muni"}
    client.post("/api/auth/register", json=user_data)
    login_res = client.post("/api/auth/login", data={"username": "admin@bolivar.gob.ar", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Crear categoría candidata
    cat_novel = crud.create_or_get_novel_category(
        db,
        name="orugas_plaga",
        area="Espacios Verdes",
        description="Plaga de orugas en la plaza",
        embedding=[0.5, 0.5, 0.0]
    )
    assert not cat_novel.is_verified

    # 2. Listar pendientes
    res_pend = client.get("/api/admin/categories/pending", headers=headers)
    assert res_pend.status_code == 200
    pendientes = res_pend.json()
    assert any(c["name"] == "orugas_plaga" for c in pendientes)

    # 3. Aprobar categoría
    res_app = client.post(
        f"/api/admin/categories/{cat_novel.id}/approve",
        headers=headers,
        json={"name": "plaga_orugas", "area": "Animales"}
    )
    assert res_app.status_code == 200
    assert res_app.json()["is_verified"] is True
    assert res_app.json()["name"] == "plaga_orugas"

    # 4. Probar fusión
    cat_dest = crud.create_or_get_novel_category(db, name="zoonosis_general", area="Animales")
    res_merge = client.post(
        "/api/admin/categories/merge",
        headers=headers,
        json={"source_category_id": cat_novel.id, "target_category_id": cat_dest.id}
    )
    assert res_merge.status_code == 200
    assert res_merge.json()["status"] == "ok"
