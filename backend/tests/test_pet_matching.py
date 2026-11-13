import io
import json
import pytest
from PIL import Image
from app.models import Report, AnimalReportType, PetType
from app.dependencies import get_predictor
from app.services.similarity import haversine_km, calculate_pet_match_score


@pytest.mark.parametrize("report_type", ["perdido", "encontrado", "en_transito"])
def test_matches_include_similar_reports_of_the_same_type(client, db, report_type):
    embedding = json.dumps([1.0] + [0.0] * 767)

    def report(name, **overrides):
        fields = dict(description="Perro dorado", pet_name=name, image_path="/uploads/test.jpg",
                      report_type=AnimalReportType(report_type), pet_type=PetType.PERRO,
                      embedding=embedding, latitude=-36.23, longitude=-61.11,
                      is_resolved=False)
        fields.update(overrides)
        return Report(**fields)

    milo = report("Milo")
    kinoto = report("Kinoto")
    excluded = [report("Resuelto", is_resolved=True),
                report("Gato", pet_type=PetType.GATO),
                report("Adopción", report_type=AnimalReportType.ADOPCION),
                report("Sin vector", embedding=None),
                report("Diferente", embedding=json.dumps([0.0, 1.0] + [0.0] * 766))]
    db.add_all([milo, kinoto, *excluded])
    db.commit()

    response = client.get(f"/api/reports/{milo.id}/matches")
    assert response.status_code == 200
    matches = response.json()["matches"]
    assert [item["report"]["id"] for item in matches] == [kinoto.id]
    assert matches[0]["visual_similarity"] == 1.0


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
    embedding = get_predictor().extract_pet_embedding(buf.getvalue())
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


def test_identity_matches_without_metadata_and_skips_other_versions(client, db):
    def report(vector, *, version="pet-reid-test", report_type=AnimalReportType.ENCONTRADO, **fields):
        return Report(
            report_type=report_type, pet_type=PetType.PERRO, image_path="/uploads/perro.jpg",
            embedding=json.dumps({"vector": vector, "version": version, "threshold": 0.8}),
            **fields,
        )

    found = report([1.0, 0.0])
    lost = report([0.9, 0.4358899], report_type=AnimalReportType.PERDIDO, pet_name="Milo")
    near = report([0.79, (1 - 0.79 ** 2) ** 0.5])
    review_floor = report([0.50, 0.75 ** 0.5])
    below_floor = report([0.49, (1 - 0.49 ** 2) ** 0.5], color_description="Negro")
    conflicting_near = report([0.79, (1 - 0.79 ** 2) ** 0.5], color_description="Blanco")
    found.color_description = "Negro"
    similar_breed = report([0.6, 0.8], pet_breed="Labrador", color_description="Dorado")
    different_version = report([1.0, 0.0], version="pet-reid-other")
    db.add_all([found, lost, near, review_floor, below_floor, conflicting_near, similar_breed, different_version])
    db.commit()

    response = client.get(f"/api/reports/{found.id}/matches")
    assert response.status_code == 200
    result = response.json()
    assert [item["report"]["id"] for item in result["matches"]] == [lost.id]
    assert [item["report"]["id"] for item in result["review_candidates"]] == [near.id, review_floor.id]
    assert result["total_checked"] == 1


def test_identity_matches_using_an_additional_photo(client, db):
    from app.models import ReportPhoto

    def embedding(vector):
        return json.dumps({"version": "pet-reid-test", "threshold": 0.8, "vector": vector})

    found = Report(
        report_type=AnimalReportType.ENCONTRADO, pet_type=PetType.PERRO,
        image_path="/uploads/found.jpg", embedding=embedding([1.0, 0.0]),
        additional_photos=[ReportPhoto(image_path="/uploads/found-profile.jpg", embedding=embedding([0.0, 1.0]))],
    )
    lost = Report(
        report_type=AnimalReportType.PERDIDO, pet_type=PetType.PERRO,
        image_path="/uploads/lost.jpg", embedding=embedding([0.0, 1.0]),
    )
    db.add_all([found, lost])
    db.commit()

    response = client.get(f"/api/reports/{lost.id}/matches")
    assert response.status_code == 200
    [match] = response.json()["matches"]
    assert match["report"]["id"] == found.id
    assert match["matched_image_path"] == "/uploads/found-profile.jpg"
    assert match["report"]["additional_photos"] == [{"image_path": "/uploads/found-profile.jpg"}]


def test_low_visual_similarity_cannot_be_rescued_by_nearby_reports(client, db):
    import math

    def report(name, cosine):
        return Report(
            pet_name=name, report_type=AnimalReportType.PERDIDO, pet_type=PetType.PERRO,
            image_path=f"/uploads/{name}.jpg",
            embedding=json.dumps([cosine, math.sqrt(1 - cosine ** 2)]),
            latitude=-36.23, longitude=-61.11, pet_breed="Mestizo", color_description="Marrón",
            description="Perro visto en el Parque Las Acollaradas",
        )

    alejo = report("Alejo", 1.0)
    # El coseno 0,382 se proyecta a 22 % en la escala visual anterior.
    kinoto = report("Kinoto", 0.382)
    weaker = report("Otro perro", 0.31)
    db.add_all([alejo, kinoto, weaker])
    db.commit()

    response = client.get(f"/api/reports/{alejo.id}/matches")
    assert response.status_code == 200
    assert response.json()["matches"] == []


@pytest.mark.parametrize("versioned", [False, True])
def test_clear_coat_conflict_excludes_otherwise_similar_reports(client, db, versioned):
    vector = [1.0, 0.0]
    embedding = json.dumps(
        {"vector": vector, "version": "pet-reid-test", "threshold": 0.8}
        if versioned else vector
    )

    def report(color):
        return Report(
            report_type=AnimalReportType.ENCONTRADO, pet_type=PetType.PERRO,
            image_path="/uploads/perro.jpg", embedding=embedding,
            color_description=color, pet_breed="Mestizo",
        )

    found = report("Negro")
    conflicting = [report("Blanco"), report("Dorazo"), report("Marrón")]
    compatible = [report("Negro con manchas blancas"), report(None), report("Quizás dorado")]
    db.add_all([found, *conflicting, *compatible])
    db.commit()

    response = client.get(f"/api/reports/{found.id}/matches")
    assert response.status_code == 200
    assert {item["report"]["id"] for item in response.json()["matches"]} == {row.id for row in compatible}
