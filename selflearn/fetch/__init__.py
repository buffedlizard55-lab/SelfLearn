"""Retrieval layer: polite HTTP client + a registry of public data sources.

The access-policy gate lives here too: :mod:`selflearn.fetch.robots` implements
RFC 9309 and is attached to :class:`HttpClient`, so no caller can request a path
an operator's robots.txt refuses.
"""

from __future__ import annotations

from .net import HttpClient, HttpResult, NetworkUnavailable
from .registry import REGISTRY, SourceSpec, get_source, load_source_matrix
from .robots import (
    CACHE_MAX_AGE_HOURS,
    SPEC_URL,
    RobotsDecision,
    RobotsDisallowed,
    RobotsFile,
    RobotsGate,
    host_decisions,
    load_gate,
)
from .robots import summarise as summarise_robots

__all__ = [
    "CACHE_MAX_AGE_HOURS",
    "HttpClient",
    "HttpResult",
    "NetworkUnavailable",
    "REGISTRY",
    "RobotsDecision",
    "RobotsDisallowed",
    "RobotsFile",
    "RobotsGate",
    "SPEC_URL",
    "SourceSpec",
    "get_source",
    "host_decisions",
    "load_gate",
    "load_source_matrix",
    "summarise_robots",
]
