import math
import json
import pytest
from app import crud, models


def test_vector_normalization_and_update(db):
    # 1. Crear categoría inicial
    cat = models.Category(
        name="problema_test",
        area="Infraestructura",
        description="Test de centroides",
        active=True,
        is_verified=False
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)

    # 2. Vector inicial: [1.0, 0.0, 0.0]
    vec1 = [1.0, 0.0, 0.0]
    cat_updated = crud.update_category_centroid(db, cat.id, vec1)
    assert cat_updated.sample_count == 1
    centroid1 = json.loads(cat_updated.embedding_centroid)
    assert pytest.approx(centroid1[0], 0.001) == 1.0
    assert pytest.approx(centroid1[1], 0.001) == 0.0

    # 3. Vector 2: [0.0, 1.0, 0.0]
    # El promedio de [1, 0, 0] y [0, 1, 0] normalizado debe ser [1/sqrt(2), 1/sqrt(2), 0]
    vec2 = [0.0, 1.0, 0.0]
    cat_updated2 = crud.update_category_centroid(db, cat.id, vec2)
    assert cat_updated2.sample_count == 2
    centroid2 = json.loads(cat_updated2.embedding_centroid)
    
    expected_val = 1.0 / math.sqrt(2.0)
    assert pytest.approx(centroid2[0], 0.001) == expected_val
    assert pytest.approx(centroid2[1], 0.001) == expected_val
    assert pytest.approx(centroid2[2], 0.001) == 0.0

    # La norma L2 del centroide debe ser exactamente 1.0
    norm = math.sqrt(sum(x * x for x in centroid2))
    assert pytest.approx(norm, 0.001) == 1.0


def test_merge_categories_centroids(db):
    # Categoría A (ej: 'crater_calle', 2 reportes)
    cat_a = models.Category(
        name="crater_calle",
        area="Infraestructura",
        description="Pozos gigantes",
        active=True,
        is_verified=False,
        sample_count=2,
        embedding_centroid=json.dumps([1.0, 0.0, 0.0])
    )
    # Categoría B (ej: 'bache_oficial', 2 reportes)
    cat_b = models.Category(
        name="bache_oficial",
        area="Infraestructura",
        description="Baches de calle",
        active=True,
        is_verified=True,
        sample_count=2,
        embedding_centroid=json.dumps([0.0, 1.0, 0.0])
    )
    db.add(cat_a)
    db.add(cat_b)
    db.commit()

    # Fusionar A en B
    merged = crud.merge_categories(db, source_category_id=cat_a.id, target_category_id=cat_b.id)
    assert merged.id == cat_b.id
    assert merged.sample_count == 4
    assert not cat_a.active

    # Verificar que el centroide combinado esté ponderado equitativamente
    centroid_merged = json.loads(merged.embedding_centroid)
    expected_val = 1.0 / math.sqrt(2.0)
    assert pytest.approx(centroid_merged[0], 0.001) == expected_val
    assert pytest.approx(centroid_merged[1], 0.001) == expected_val
