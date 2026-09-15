#!/usr/bin/env python3
"""Launch IRIS, which independently activates ARGOS and AORATOS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aoratos.security.reference_boundary import AoratosDataSecurity
from argos.runtime.reference_kernel import AdmissionError, ArgosKernel


class IrisLauncher:
    """Reference startup owner for the current bounded demonstration."""

    def __init__(self) -> None:
        self.active = False
        self.aoratos = AoratosDataSecurity()
        self.argos = ArgosKernel()
        self.activation_order: list[str] = []

    def activate(self) -> None:
        self.active = True
        self.activation_order.append("IRIS")
        self.argos.activate()
        self.activation_order.append("ARGOS")
        self.aoratos.activate()
        self.activation_order.append("AORATOS")

    def execute(self, component_dir: Path, envelope: dict[str, Any]) -> dict[str, Any]:
        if not self.active:
            self.activate()
        result = self.argos.execute(component_dir, envelope)
        return {
            "launcher": "IRIS",
            "activation_order": list(self.activation_order),
            "aoratos": self.aoratos.status(),
            "sol": {
                "status": "NOT_IMPLEMENTED",
                "input_mode": "CANONICAL_FIXTURE_ONLY",
            },
            "argos": result,
        }


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AdmissionError(f"{path} must contain a JSON object")
    return value


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = IrisLauncher().execute(args.component, _load_json(args.input))
    except (AdmissionError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"IRIS activation/execution rejected: {error}", file=sys.stderr)
        return 2
    encoded = canonical_json(result)
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
