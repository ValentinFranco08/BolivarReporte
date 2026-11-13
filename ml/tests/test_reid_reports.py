import torch

from ml.evaluation.reid import evaluate
from ml.evaluation.reid_precision import calibrate_precision, precision_metrics
from ml.evaluation.reid_reports import report_scores


def test_additional_photos_improve_a_match_and_can_raise_false_alerts():
    # A profile photo matches the lost dog. Another dog looks similar from one angle.
    gallery = (
        torch.tensor([[0.0, 1.0], [1.0, 0.0], [-1.0, 0.0], [0.0, 1.0]]),
        ["lost", "lost", "other", "other"],
    )
    queries = (torch.tensor([[1.0, 0.0], [0.0, 1.0]]), ["lost", "absent"])

    one = evaluate(report_scores(queries, gallery, 1), threshold=0.9)
    multiple = evaluate(report_scores(queries, gallery, 3), threshold=0.9)

    assert one["top5_at_threshold"] == 0.0
    assert multiple["top5_at_threshold"] == 1.0
    assert multiple["false_alert_rate"] == 1.0


def test_sampling_prefers_separate_scenes_and_similar_dogs(tmp_path):
    import random
    from pathlib import Path

    from ml.data.reid_sampling import ScenePairSampler

    dogs = ["a", "b", "c"]
    rows = [(Path(f"{dog}-{video}.jpg"), dog) for dog in dogs for video in ("0", "1", "2")]
    splits = tmp_path / "splits.tab"
    splits.write_text("DOG_ID\tVIDEO_ID\tGROUP\n" + "".join(
        f"{dog}\t{video}\t{int(video == "2")}\n" for dog in dogs for video in ("0", "1", "2")
    ))
    sampler = ScenePairSampler(rows, splits, {"a": "labrador", "b": "labrador", "c": "poodle"})
    groups = {dog: list(range(i * 3, i * 3 + 3)) for i, dog in enumerate(dogs)}

    [pairs] = list(sampler(random.Random(42), groups))

    assert {rows[a][1] for a, _ in pairs} == set(dogs)
    assert all(rows[a][1] == rows[b][1] and sampler.scenes[a] != sampler.scenes[b] for a, b in pairs)


def test_precision_calibration_counts_all_suggestions_at_a_tied_score():
    ranked = torch.tensor([[0.95, 0.70], [0.90, 0.80], [0.80, 0.40]])
    correct = torch.tensor([[True, False], [True, False], [False, False]])
    scores = ranked[:, 0], ranked, correct, torch.tensor([True, True, False])

    threshold = calibrate_precision(scores, minimum=0.8, min_suggestions=2)
    assert threshold == float(ranked[1, 0])
    assert precision_metrics(scores, threshold)["precision"] == 1.0
    assert calibrate_precision(scores, minimum=0.8, min_suggestions=3) is None
    assert precision_metrics(scores, threshold=1.0)["precision"] is None


def test_manifest_keeps_local_test_separate_and_rejects_unverified_photos(tmp_path, monkeypatch):
    import json
    import pytest
    from ml.data import reid_manifest

    monkeypatch.setattr(reid_manifest, "dogreid_splits", lambda *_: {})
    monkeypatch.setattr(reid_manifest, "mpdd_splits", lambda *_: ([], []))
    (tmp_path / "splits.tab").write_text("DOG_ID\tVIDEO_ID\tGROUP\n")
    (tmp_path / "breeds.tab").write_text("DOG_ID\tBREED\n")
    (tmp_path / "photo.jpg").write_bytes(b"test-photo")
    local = tmp_path / "local.json"
    photo = {"image": "photo.jpg", "dog_id": "1", "scene_id": "street",
             "role": "test_query", "identity_verified": True, "authorized": False}
    local.write_text(json.dumps([photo]))
    with pytest.raises(ValueError, match="autorización"):
        reid_manifest.build_manifest(tmp_path, local)
    photo["authorized"] = True
    local.write_text(json.dumps([photo]))
    [row] = reid_manifest.build_manifest(tmp_path, local)
    assert row["role"] == "local_test_query"
    assert row["dog_id"] == "local:1"
