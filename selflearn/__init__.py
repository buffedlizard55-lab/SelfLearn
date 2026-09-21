"""SelfLearn - an autonomous, evidence-verifying research engine.

Design contract (see docs/ARCHITECTURE.md):

* The engine never asserts a fact it cannot quote from a retrieved document.
* Anything that is not a verbatim-grounded fact is labelled an *inference* and
  must carry an explicit derivation over verified claims.
* Anything the engine cannot verify is emitted as ``UNKNOWN`` or as an
  irregularity - never silently smoothed over into confident prose.
"""

from __future__ import annotations

__version__ = "0.1.0"

ENGINE_NAME = "SelfLearn"
ENGINE_REPO_URL = "https://github.com/buffedlizard55-lab/SelfLearn"
ENGINE_SITE_URL = "https://buffedlizard55-lab.github.io/SelfLearn/"

__all__ = ["__version__", "ENGINE_NAME", "ENGINE_REPO_URL", "ENGINE_SITE_URL"]
