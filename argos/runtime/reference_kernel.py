"""Minimal contract-driven ARGOS reference kernel."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


MANIFEST_VERSION = "IAA.ARGOS.COMPONENT.v1"
SCENARIO_CONTRACT = "IAA.ARGOS.BUSINESS.SCENARIO.v1"
RESULT_CONTRACT = "IAA.ARGOS.BUSINESS.RESULT.v1"
REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWED_COMPONENT_ROOT = (REPO_ROOT / "components" / "argos" / "business").resolve()


class AdmissionError(ValueError):
    pass


class ArgosKernel:
    """Admit and execute replaceable business logic by explicit contract."""

    def __init__(self) -> None:
        self.active = False

    def activate(self) -> None:
        if self.active:
            return
        self.active = True

    def _load_component(
        self,
        component_dir: Path,
        expected_component_id: str,
        expected_contract: str,
    ) -> tuple[dict[str, Any], Any]:
        component_dir = component_dir.resolve()
        if component_dir.parent != ALLOWED_COMPONENT_ROOT:
            raise AdmissionError("component must be a direct child of components/argos/business")

        manifest_path = component_dir / "component.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise AdmissionError("component manifest must be an object")
        required = {"manifest_version", "component_id", "component_kind", "contract", "entrypoint", "factory"}
        missing = sorted(required - manifest.keys())
        if missing:
            raise AdmissionError(f"manifest fields missing: {', '.join(missing)}")
        if manifest["manifest_version"] != MANIFEST_VERSION:
            raise AdmissionError("unsupported manifest version")
        if manifest["component_kind"] != "business":
            raise AdmissionError("component kind is not business")
        if manifest["component_id"] != expected_component_id:
            raise AdmissionError("component_id mismatch")
        if manifest["contract"] != expected_contract:
            raise AdmissionError("component contract mismatch")

        entrypoint = (component_dir / manifest["entrypoint"]).resolve()
        if entrypoint.parent != component_dir or entrypoint.suffix != ".py" or not entrypoint.is_file():
            raise AdmissionError("entrypoint must be one Python file inside the component directory")

        module_name = f"iaa_argos_component_{manifest['component_id'].replace('-', '_')}"
        spec = importlib.util.spec_from_file_location(module_name, entrypoint)
        if spec is None or spec.loader is None:
            raise AdmissionError("cannot load component entrypoint")
        module = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(component_dir.parent))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)
        factory = getattr(module, manifest["factory"], None)
        if not callable(factory):
            raise AdmissionError("manifest factory is not callable")
        return manifest, factory

    def execute(self, component_dir: Path, envelope: dict[str, Any]) -> dict[str, Any]:
        if not self.active:
            raise AdmissionError("ARGOS is not active")
        if envelope.get("contract") != SCENARIO_CONTRACT:
            raise AdmissionError("scenario contract mismatch")
        if not isinstance(envelope.get("component_id"), str):
            raise AdmissionError("component_id must be a string")
        if not isinstance(envelope.get("configuration"), dict):
            raise AdmissionError("configuration must be an object")
        if not isinstance(envelope.get("commands"), list):
            raise AdmissionError("commands must be an array")

        manifest, factory = self._load_component(
            component_dir,
            expected_component_id=envelope["component_id"],
            expected_contract=envelope["contract"],
        )
        session = factory(envelope["configuration"])
        results = []
        for index, command in enumerate(envelope["commands"]):
            if not isinstance(command, dict):
                raise AdmissionError(f"command {index} must be an object")
            results.append(session.handle(command))
        return {
            "contract": RESULT_CONTRACT,
            "component_id": manifest["component_id"],
            "manifest_version": manifest["manifest_version"],
            "results": results,
        }
