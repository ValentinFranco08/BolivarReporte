"""Medir una foto de hallazgo contra reportes con una o varias fotos."""
from collections import defaultdict

import torch

from ml.evaluation.reid import calibrate, evaluate


def report_scores(queries, gallery, photos_per_report, top_k=5):
    query_vectors, query_labels = queries
    gallery_vectors, gallery_labels = gallery
    reports = defaultdict(list)
    for index, identity in enumerate(gallery_labels):
        reports[identity].append(index)
    identities = sorted(reports)
    indices = torch.tensor([
        (reports[label] + reports[label][:1] * photos_per_report)[:photos_per_report]
        for label in identities
    ])
    similarities = (query_vectors @ gallery_vectors[indices.flatten()].T).reshape(
        len(query_labels), len(identities), photos_per_report
    ).amax(dim=2).clamp(-1, 1)
    ranked_scores, ranks = similarities.topk(min(top_k, len(identities)), dim=1)
    correct = torch.tensor([
        [label == identities[index] for index in row]
        for label, row in zip(query_labels, ranks.tolist())
    ])
    present = torch.tensor([label in reports for label in query_labels])
    if not present.any() or present.all():
        raise ValueError("La evaluación necesita consultas con pareja y sin pareja.")
    return ranked_scores[:, 0], ranked_scores, correct, present


def compare_photo_counts(validation, test, external):
    result = {}
    for count in (1, 3, 4):
        threshold = calibrate(report_scores(*validation, count))["threshold"]
        result[str(count)] = {
            "dogreid": evaluate(report_scores(*test, count), threshold),
            "mpdd": evaluate(report_scores(*external, count), threshold),
        }
    return result
