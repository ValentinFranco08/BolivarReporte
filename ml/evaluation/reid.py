"""Búsqueda por foto con identidades reservadas y consultas sin pareja."""
import torch


def retrieval_scores(vectors, identities):
    first = {}
    gallery = []
    for index, identity in enumerate(identities):
        if identity not in first:
            first[identity] = index
        else:
            gallery.append(index)
    queries = list(first.values())
    present = torch.arange(len(queries)) % 2 == 0
    present_labels = {identities[index] for index, keep in zip(queries, present.tolist()) if keep}
    gallery = [index for index in gallery if identities[index] in present_labels]
    scores = vectors[queries] @ vectors[gallery].T
    ranks = scores.argsort(dim=1, descending=True)[:, :5]
    correct = torch.tensor([
        [identities[query] == identities[gallery[position]] for position in row]
        for query, row in zip(queries, ranks.tolist())
    ])
    return scores.max(dim=1).values, scores.gather(1, ranks), correct, present


def evaluate(scores, threshold):
    best, ranked_scores, correct, present = scores
    return {
        'recall_at_5': float(correct[present].any(dim=1).float().mean()),
        'top5_at_threshold': float((correct[present] & (ranked_scores[present] >= threshold)).any(dim=1).float().mean()),
        'false_alert_rate': float((best[~present] >= threshold).float().mean()),
        'threshold': threshold,
    }


def calibrate(scores, max_false_alert_rate=0.05):
    # Los únicos puntos donde cambia el conjunto aceptado son los scores observados.
    best = scores[0]
    thresholds = [1.000001, *sorted(set(best.tolist()), reverse=True)]
    candidates = [evaluate(scores, threshold) for threshold in thresholds]
    valid = [row for row in candidates if row['false_alert_rate'] <= max_false_alert_rate]
    return max(valid, key=lambda row: row['top5_at_threshold'])
