"""Entrenar una proyección visual y compararla con el ViT sin ajustar."""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader
from transformers import ViTModel

from ml.data.pet_identity import PetIdentityDataset, identity_splits
from ml.device import get_device
from ml.evaluation.reid import calibrate, evaluate, retrieval_scores
from ml.evaluation.reid_reports import report_scores
from ml.models.pet_reid import PetReIDModel
from ml.preprocessing.images import ImagePreprocessor


@torch.no_grad()
def extract(model, rows, device, batch_size, transform=None):
    batches = DataLoader(PetIdentityDataset(rows, transform or ImagePreprocessor()), batch_size=batch_size)
    features, labels = [], []
    for batch, identities in batches:
        features.append(model.features(batch.to(device)).cpu())
        labels.extend(identities)
        if len(features) % 25 == 0:
            print(f'Fotos procesadas: {len(labels)}/{len(rows)}', flush=True)
    return torch.cat(features), labels


def train_projection(model, train, validation, epochs, seed, photos_per_report=None, sample_batches=None):
    features, labels = train
    groups = defaultdict(list)
    for index, label in enumerate(labels):
        groups[label].append(index)
    identities = list(groups)
    rng = random.Random(seed)
    optimizer = torch.optim.AdamW(model.projection.parameters(), lr=0.001)
    loss_fn = nn.TripletMarginLoss(margin=0.2)
    best = None
    for epoch in range(epochs):
        if sample_batches is None:
            rng.shuffle(identities)
            batches = (identities[start:start + 32] for start in range(0, len(identities), 32))
            pairs_by_batch = ([rng.sample(groups[label], 2) for label in batch] for batch in batches)
        else:
            pairs_by_batch = sample_batches(rng, groups)
        for pairs in pairs_by_batch:
            if len(pairs) < 2:
                continue
            anchors = model.project(features[[a for a, _ in pairs]])
            positives = model.project(features[[p for _, p in pairs]])
            similarities = anchors @ positives.T
            similarities.fill_diagonal_(-torch.inf)
            negatives = positives[similarities.argmax(dim=1)]
            loss = loss_fn(anchors, positives, negatives)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        with torch.no_grad():
            if photos_per_report is None:
                scores = retrieval_scores(model.project(validation[0]), validation[1])
            else:
                query, gallery = validation
                scores = report_scores(
                    (model.project(query[0]), query[1]), (model.project(gallery[0]), gallery[1]), photos_per_report,
                )
            metrics = calibrate(scores)
        print(f'Época {epoch + 1}: {metrics}', flush=True)
        if best is None or metrics['top5_at_threshold'] > best[0]['top5_at_threshold']:
            best = metrics, {k: v.clone() for k, v in model.projection.state_dict().items()}
    return best


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--encoder', default='google/vit-base-patch16-224')
    parser.add_argument('--batch-size', type=int, default=8)
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--limit-identities', type=int)
    args = parser.parse_args(argv)
    if args.epochs < 1 or args.batch_size < 1:
        parser.error('Épocas y tamaño de lote deben ser positivos.')
    torch.manual_seed(args.seed)
    partitions = identity_splits(args.dataset, args.seed)
    if args.limit_identities is not None:
        if args.limit_identities < 2:
            parser.error('--limit-identities debe ser al menos 2 por partición.')
        limited = []
        for rows in partitions:
            selected = set(list(dict.fromkeys(label for _, label in rows))[:args.limit_identities])
            limited.append([row for row in rows if row[1] in selected])
        partitions = limited
    device = get_device()
    encoder = ViTModel.from_pretrained(args.encoder)
    model = PetReIDModel(encoder).to(device).eval()
    print(f'Extrayendo características en {device}: {[len(rows) for rows in partitions]} fotos', flush=True)
    train, validation, test = (extract(model, rows, device, args.batch_size) for rows in partitions)
    model.cpu()
    metrics, weights = train_projection(model, train, validation, args.epochs, args.seed)
    model.projection.load_state_dict(weights)
    with torch.no_grad():
        baseline_threshold = calibrate(retrieval_scores(*validation))['threshold']
        baseline = evaluate(retrieval_scores(*test), baseline_threshold)
        trained = evaluate(retrieval_scores(model.project(test[0]), test[1]), metrics['threshold'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix('.tmp')
    torch.save({'format': 1, 'encoder': args.encoder, 'projection': weights,
                'threshold': metrics['threshold']}, temp)
    temp.replace(args.output)
    result = {'baseline_test': baseline, 'reid_test': trained, 'validation': metrics,
              'splits': [{'photos': len(labels), 'dogs': len(set(labels))} for _, labels in (train, validation, test)]}
    args.output.with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
