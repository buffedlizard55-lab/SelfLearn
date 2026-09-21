"""Retrieval layer: polite HTTP client + a registry of public data sources."""

from __future__ import annotations

from .net import HttpClient, HttpResult, NetworkUnavailable
from .registry import REGISTRY, SourceSpec, get_source, load_source_matrix

__all__ = [
    "HttpClient",
    "HttpResult",
    "NetworkUnavailable",
    "REGISTRY",
    "SourceSpec",
    "get_source",
    "load_source_matrix",
]
