"""Bounded-memory Test-Time Template Adjustment (T3A)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.special import softmax


def _normalize_rows(values: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    return values / np.maximum(norms, np.finfo(float).eps)


@dataclass
class T3A:
    """Optimization-free classifier adjustment over frozen embeddings.

    `classifier_weights` has shape `(classes, embedding_dim)`. Each incoming
    embedding receives a pseudo-label from the source classifier, enters that
    class support set, and only the lowest-entropy supports are retained.
    """

    classifier_weights: np.ndarray
    supports_per_class: int = 10
    temperature: float = 1.0
    _supports: list[list[np.ndarray]] = field(init=False, repr=False)
    _entropies: list[list[float]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        weights = np.asarray(self.classifier_weights, dtype=np.float64)
        if weights.ndim != 2:
            raise ValueError("classifier_weights must have shape (classes, embedding_dim)")
        if self.supports_per_class < 1:
            raise ValueError("supports_per_class must be positive")
        if self.temperature <= 0:
            raise ValueError("temperature must be positive")
        self.classifier_weights = _normalize_rows(weights)
        self._supports = [[row.copy()] for row in self.classifier_weights]
        self._entropies = [[0.0] for _ in range(self.classifier_weights.shape[0])]

    @property
    def support_counts(self) -> tuple[int, ...]:
        return tuple(len(items) for items in self._supports)

    def reset(self) -> None:
        self._supports = [[row.copy()] for row in self.classifier_weights]
        self._entropies = [[0.0] for _ in range(self.classifier_weights.shape[0])]

    def _source_probabilities(self, embedding: np.ndarray) -> np.ndarray:
        logits = self.classifier_weights @ embedding / self.temperature
        return softmax(logits)

    def _add_support(self, class_index: int, embedding: np.ndarray, entropy: float) -> None:
        self._supports[class_index].append(embedding.copy())
        self._entropies[class_index].append(float(entropy))
        order = np.argsort(self._entropies[class_index])[: self.supports_per_class]
        self._supports[class_index] = [self._supports[class_index][int(i)] for i in order]
        self._entropies[class_index] = [self._entropies[class_index][int(i)] for i in order]

    def prototypes(self) -> np.ndarray:
        prototypes = np.vstack(
            [np.mean(np.vstack(class_supports), axis=0) for class_supports in self._supports]
        )
        return _normalize_rows(prototypes)

    def predict_one(self, embedding: np.ndarray, *, update: bool = True) -> tuple[int, np.ndarray]:
        vector = np.asarray(embedding, dtype=np.float64).reshape(1, -1)
        if vector.shape[1] != self.classifier_weights.shape[1]:
            raise ValueError("Embedding dimension does not match classifier weights")
        vector = _normalize_rows(vector)[0]
        source_probabilities = self._source_probabilities(vector)
        pseudo_label = int(np.argmax(source_probabilities))
        entropy = float(
            -np.sum(source_probabilities * np.log(np.maximum(source_probabilities, 1e-12)))
        )
        if update:
            self._add_support(pseudo_label, vector, entropy)
        probabilities = softmax(self.prototypes() @ vector / self.temperature)
        return int(np.argmax(probabilities)), probabilities

    def predict(self, embeddings: np.ndarray, *, update: bool = True) -> tuple[np.ndarray, np.ndarray]:
        batch = np.asarray(embeddings, dtype=np.float64)
        if batch.ndim != 2:
            raise ValueError("embeddings must have shape (samples, embedding_dim)")
        labels, probabilities = [], []
        for embedding in batch:
            label, scores = self.predict_one(embedding, update=update)
            labels.append(label)
            probabilities.append(scores)
        return np.asarray(labels, dtype=int), np.vstack(probabilities)
