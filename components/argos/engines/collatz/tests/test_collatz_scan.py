from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import py_compile
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossible de charger {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cpu = load_module("collatz_a001_cpu", "collatz_a001_memory_vs_residue.py")
zone = load_module("collatz_zone", "collatz_zone_conditioned_k_test.py")


class CollatzArithmeticTests(unittest.TestCase):
    def test_v2_and_oddify(self):
        self.assertEqual(cpu.v2(1), 0)
        self.assertEqual(cpu.v2(8), 3)
        self.assertEqual(cpu.oddify(40), 5)

    def test_known_odd_steps(self):
        self.assertEqual(cpu.odd_step(3), (5, 1))
        self.assertEqual(cpu.odd_step(5), (1, 4))
        self.assertEqual(cpu.odd_step(7), (11, 1))

    def test_invalid_inputs_are_rejected(self):
        for value in (0, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    cpu.v2(value)
                with self.assertRaises(ValueError):
                    cpu.oddify(value)

    def test_deterministic_split(self):
        first = [cpu.is_test(trajectory, step, 0.25) for trajectory in range(20) for step in range(10)]
        second = [cpu.is_test(trajectory, step, 0.25) for trajectory in range(20) for step in range(10)]
        self.assertEqual(first, second)

    def test_zone_boundaries(self):
        self.assertEqual(zone.zone_of(16, 4), "BELOW_HALF")
        self.assertEqual(zone.zone_of(16, 12), "BELOW_START")
        self.assertEqual(zone.zone_of(16, 20), "LOW_ASCENT")
        self.assertEqual(zone.zone_of(16, 40), "HIGH_ASCENT")
        self.assertEqual(zone.zone_of(16, 64), "EXTREME")


class CollatzIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.input_csv = self.base / "starts.csv"
        with self.input_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["n"])
            for n in range(1, 5001):
                writer.writerow([n])

    def tearDown(self):
        self.temp.cleanup()

    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *map(str, args)],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_cpu_experiment_emits_consistent_artifacts(self):
        output = self.base / "a001"
        completed = self.run_script(
            "collatz_a001_memory_vs_residue.py",
            self.input_csv,
            output,
            "--word-length", "4",
            "--step-limit", "300",
            "--max-memory-words", "3",
            "--residue-powers", "1,2,3,4",
        )
        self.assertIn("CAMP-A001-0001 PASS", completed.stdout)
        summary_path = output / "camp_a001_0001_summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(summary["starts"], 5000)
        self.assertGreater(summary["events"], 0)
        self.assertEqual(
            summary["workspace_sha256"],
            hashlib.sha256(self.input_csv.read_bytes()).hexdigest(),
        )
        self.assertTrue((output / "camp_a001_0001_models.csv").stat().st_size > 0)
        self.assertTrue((output / "camp_a001_0001_word_transitions.csv").stat().st_size > 0)

    def test_zone_experiment_emits_bounded_verdict(self):
        output = self.base / "zone"
        completed = self.run_script(
            "collatz_zone_conditioned_k_test.py",
            self.input_csv,
            output,
            "--word-length", "3",
            "--step-limit", "300",
            "--permutations", "20",
        )
        payload = json.loads(
            (output / "collatz_zone_conditioned_k_test_v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn(payload["verdict"], {"SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE"})
        self.assertGreaterEqual(payload["events"], 500)
        self.assertIn(
            f"COLLATZ_ZONE_CONDITIONED_K_TEST_{payload['verdict']}",
            completed.stdout,
        )

    def test_all_sources_compile_without_importing_gpu_dependencies(self):
        for source in SCRIPTS.glob("*.py"):
            py_compile.compile(str(source), doraise=True)


if __name__ == "__main__":
    unittest.main()

