"""Pares de la misma identidad entre escenas y negativos de aspecto similar."""
import csv
import re
from collections import defaultdict


def read_traits(path, column):
    if path is None:
        return {}
    with path.open(newline="") as file:
        rows = csv.DictReader(file, delimiter="\t")
        values = {row["DOG_ID"]: re.sub(r"[^a-z0-9]", "", row[column].casefold()) for row in rows}
    unknown = {"", "unknown", "mixed", "mix", "mixedbreed", "other", "mutt", "na", "notsure"}
    return {dog: label for dog, label in values.items() if label not in unknown}


class ScenePairSampler:
    def __init__(self, rows, splits, breeds, coats=None):
        with splits.open(newline="") as file:
            scenes = {(r["DOG_ID"], r["VIDEO_ID"]): r["GROUP"] for r in csv.DictReader(file, delimiter="\t")}
        self.scenes = [scenes[(dog, path.stem[len(dog) + 1:])] for path, dog in rows]
        self._set_traits(breeds, coats)

    @classmethod
    def from_manifest(cls, rows):
        sampler = cls.__new__(cls)
        sampler.scenes = [row["scene_id"] for row in rows]
        sampler._set_traits(
            {row["dog_id"]: row["breed"] for row in rows if row.get("breed")},
            {row["dog_id"]: row["coat"] for row in rows if row.get("coat")},
        )
        return sampler

    def _set_traits(self, breeds, coats):
        self.breeds = breeds
        self.coats = coats or {}

    def __call__(self, rng, groups):
        by_breed, by_coat = defaultdict(list), defaultdict(list)
        for dog in groups:
            if dog in self.breeds:
                by_breed[self.breeds[dog]].append(dog)
            if dog in self.coats:
                by_coat[self.coats[dog]].append(dog)
        order = list(groups)
        rng.shuffle(order)
        remaining = set(order)
        for anchor in order:
            if anchor not in remaining:
                continue
            batch = [anchor]
            remaining.remove(anchor)
            for trait, index in ((self.breeds, by_breed), (self.coats, by_coat)):
                neighbors = [dog for dog in index[trait.get(anchor)] if dog in remaining]
                if trait is self.coats:
                    neighbors = [dog for dog in neighbors if dog in self.breeds
                                 and anchor in self.breeds and self.breeds[dog] != self.breeds[anchor]]
                rng.shuffle(neighbors)
                for dog in neighbors[:7]:
                    batch.append(dog)
                    remaining.remove(dog)
            for dog in order:
                if len(batch) == 32:
                    break
                if dog in remaining:
                    batch.append(dog)
                    remaining.remove(dog)
            pairs = []
            for dog in batch:
                photos = groups[dog]
                first = rng.choice(photos)
                other_scenes = [i for i in photos if self.scenes[i] != self.scenes[first]]
                second = rng.choice(other_scenes or [i for i in photos if i != first])
                pairs.append((first, second))
            yield pairs
