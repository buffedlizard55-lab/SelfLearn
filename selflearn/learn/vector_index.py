"""A deterministic vector index over the library's claims.

What this is
------------
Every claim is turned into a sparse TF-IDF vector over the content tokens the
claim already contains (``util.content_tokens``: lowercase, stopwords removed).
A query is vectorised the same way and scored by cosine similarity. The index
exists so that cross-domain retrieval ranks claims by the whole vocabulary they
share with a question - weighted by how distinctive each term is across the
corpus - instead of by a single raw containment ratio.

What this is not
----------------
There is no embedding model, no learned projection and no third-party
dependency. A vector here is arithmetic over tokens that are already in stored
documents, so a reviewer can recompute any score by hand from the published
formula:

* ``tf(t, d) = 1 + ln(f(t, d))`` for term frequency ``f`` in document ``d``
* ``idf(t) = ln(1 + N / df(t))`` over ``N`` indexed documents
* weight ``w(t, d) = tf * idf``, each document L2-normalised
* score(query, d) = dot product of the normalised vectors (cosine)

Ordering is fully deterministic: scores are compared as computed, and ties are
broken by claim id, so two runs over the same library return the same list.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable

from ..models import Claim
from ..util import content_tokens


def _terms(text: str) -> list[str]:
    """Index terms: content tokens, kept in a stable list for frequencies."""
    return sorted(content_tokens(text))


@dataclass
class VectorIndex:
    """Sparse TF-IDF vectors for a fixed set of claims."""

    #: claim_id -> {term: l2-normalised weight}
    doc_vectors: dict[str, dict[str, float]] = field(default_factory=dict)
    #: term -> idf weight computed at build time
    idf: dict[str, float] = field(default_factory=dict)

    # -- construction ------------------------------------------------------
    @classmethod
    def build(cls, claims: Iterable[Claim]) -> "VectorIndex":
        """Index the given claims. Order of input does not affect the result."""
        claim_list = sorted(claims, key=lambda c: c.claim_id)
        term_freqs: dict[str, dict[str, int]] = {}
        for claim in claim_list:
            freq: dict[str, int] = {}
            for term in _terms(claim.text):
                freq[term] = freq.get(term, 0) + 1
            term_freqs[claim.claim_id] = freq

        doc_count = len(claim_list)
        document_frequency: dict[str, int] = {}
        for freq in term_freqs.values():
            for term in freq:
                document_frequency[term] = document_frequency.get(term, 0) + 1

        idf = {
            term: math.log(1.0 + doc_count / df)
            for term, df in sorted(document_frequency.items())
        }

        index = cls(idf=idf)
        for claim_id, freq in sorted(term_freqs.items()):
            index.doc_vectors[claim_id] = _normalise(
                {term: (1.0 + math.log(count)) * idf[term] for term, count in freq.items()}
            )
        return index

    # -- queries -----------------------------------------------------------
    def query_vector(self, text: str) -> dict[str, float]:
        """Vectorise a query with the index's idf weights (unknown terms drop)."""
        freq: dict[str, int] = {}
        for term in _terms(text):
            freq[term] = freq.get(term, 0) + 1
        vector = {
            term: (1.0 + math.log(count)) * self.idf[term]
            for term, count in freq.items()
            if term in self.idf
        }
        return _normalise(vector)

    def similarity(self, query: str | dict[str, float], claim_id: str) -> float:
        """Cosine similarity between a query and one indexed claim (0.0 if absent)."""
        query_vector = query if isinstance(query, dict) else self.query_vector(query)
        doc_vector = self.doc_vectors.get(claim_id)
        if not query_vector or not doc_vector:
            return 0.0
        # Iterate the smaller side; both vectors are L2-normalised, so the dot
        # product is the cosine.
        if len(query_vector) > len(doc_vector):
            query_vector, doc_vector = doc_vector, query_vector
        return sum(weight * doc_vector.get(term, 0.0) for term, weight in query_vector.items())

    def search(
        self,
        query: str,
        *,
        k: int = 10,
        exclude_ids: Iterable[str] = (),
    ) -> list[tuple[str, float]]:
        """Top-``k`` claim ids for ``query`` by cosine, ties broken by id."""
        query_vector = self.query_vector(query)
        if not query_vector:
            return []
        excluded = set(exclude_ids)
        scored = [
            (claim_id, self.similarity(query_vector, claim_id))
            for claim_id in self.doc_vectors
            if claim_id not in excluded
        ]
        scored = [(claim_id, score) for claim_id, score in scored if score > 0.0]
        scored.sort(key=lambda item: (-item[1], item[0]))
        return scored[: max(0, k)]

    def to_dict(self) -> dict[str, Any]:
        """A compact, reproducible summary (used by tests and the CLI)."""
        return {
            "documents": len(self.doc_vectors),
            "vocabulary": len(self.idf),
            "idf": {term: round(weight, 6) for term, weight in sorted(self.idf.items())},
        }


def _normalise(weights: dict[str, float]) -> dict[str, float]:
    norm = math.sqrt(sum(w * w for w in weights.values()))
    if norm <= 0.0:
        return {}
    return {term: w / norm for term, w in sorted(weights.items())}
