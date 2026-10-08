import io
import json
from PIL import Image
from app.ai_service import ai_service, haversine_km, calculate_pet_match_score, calculate_cosine_similarity
from app import models, crud

def test_haversine_bolivar():
    # Centro Cívico Bolívar: -36.2333, -61.1167
    # Parque Las Acollaradas: -36.2250, -61.1250 (aprox ~1.18 km)
    dist = haversine_km(-36.2333, -61.1167, -36.2250, -61.1250)
    assert 0.8 <= dist <= 1.6
    # Misma coordenada debe dar 0 km
    assert haversine_km(-36.2333, -61.1167, -36.2333, -61.1167) == 0.0

def test_pet_match_score():
    # Caso 1: Alta similitud visual (0.90), rasgos semánticos coincidentes (1.0) y distancia corta (0.5 km)
    score_completo = calculate_pet_match_score(0.90, 0.5, semantic_sim=1.0, max_radius_km=5.0)
    # 0.65 * 0.90 + 0.20 * 1.0 + 0.15 * 0.90 = 0.585 + 0.20 + 0.135 = 0.92
    assert score_completo >= 0.90

    # Caso 2: Alta similitud visual (0.90) sin rasgos semánticos (neutral 0.5) y lejos (10 km)
    score_lejos = calculate_pet_match_score(0.90, 10.0, semantic_sim=0.5, max_radius_km=5.0)
    # 0.65 * 0.90 + 0.20 * 0.5 + 0.15 * 0.0 = 0.585 + 0.10 = 0.685
    assert 0.68 <= score_lejos <= 0.70

def test_pet_embedding_extraction():
    img = Image.new("RGB", (100, 100), color="goldenrod")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    embedding = ai_service.extract_pet_embedding(buf.getvalue())
    assert isinstance(embedding, list)
    assert len(embedding) == 768
    # Comprobar normalización L2 (norma ~ 1.0)
    norm = sum(x * x for x in embedding) ** 0.5
    assert 0.95 <= norm <= 1.05

def test_pet_matching_endpoints(client, db):
    # Registrar usuario y loguear
    user_data = {"email": "rescatista@bolivar.gob.ar", "password": "password123", "name": "Rescatista Bolívar"}
    client.post("/api/auth/register", json=user_data)
    login_res = client.post("/api/auth/login", data={"username": "rescatista@bolivar.gob.ar", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Crear perro encontrado (ej: en Barrio Pompeya)
    emb_perro = [0.05] * 768
    norm = sum(x*x for x in emb_perro)**0.5
    emb_perro = [x/norm for x in emb_perro]

    report_encontrado = {
        "description": "Perro tipo labrador dorado encontrado cerca de la plaza",
        "latitude": -36.2330,
        "longitude": -61.1170,
        "address": "Av. San Martín 450",
        "report_type": "encontrado",
        "pet_type": "perro",
        "pet_name": "Sin nombre",
        "pet_breed": "Labrador / Mestizo",
        "color_description": "Dorado claro",
        "health_status": "sano",
        "contact_name": "Juan",
        "contact_phone": "2314123456",
        "image_path": "/uploads/labrador_encontrado.jpg",
        "embedding": emb_perro
    }
    res1 = client.post("/api/reports", json=report_encontrado, headers=headers)
    assert res1.status_code == 200
    rep1_id = res1.json()["id"]

    # 2. Crear reporte de perro perdido muy similar (dueño buscando a 'Milo')
    report_perdido = {
        "description": "Se perdió Milo, perro labrador doradito con collar rojo",
        "latitude": -36.2340,
        "longitude": -61.1180,
        "address": "Belgrano y Alsina",
        "report_type": "perdido",
        "pet_type": "perro",
        "pet_name": "Milo",
        "pet_breed": "Labrador",
        "color_description": "Dorado",
        "health_status": "sano",
        "contact_name": "María",
        "contact_phone": "2314987654",
        "image_path": "/uploads/milo_perdido.jpg",
        "embedding": emb_perro
    }
    res2 = client.post("/api/reports", json=report_perdido, headers=headers)
    assert res2.status_code == 200
    rep2_id = res2.json()["id"]

    # 3. Consultar matches para 'Milo'
    res_matches = client.get(f"/api/reports/{rep2_id}/matches")
    assert res_matches.status_code == 200
    matches_data = res_matches.json()
    assert len(matches_data["matches"]) >= 1
    top_match = matches_data["matches"][0]
    assert top_match["report"]["id"] == rep1_id
    assert top_match["visual_similarity"] >= 0.95
    assert top_match["combined_score"] >= 0.85

    # 4. Probar resolver reporte
    res_res = client.patch(f"/api/reports/{rep2_id}/resolve", headers=headers)
    assert res_res.status_code == 200
    assert res_res.json()["is_resolved"] is True
