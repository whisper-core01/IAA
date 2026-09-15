from __future__ import annotations

import csv
import hashlib
import importlib.util
import py_compile
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossible de charger {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


scan = load_module("collatz_record_scan", "scan_L_records.py")


def normalized_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").rstrip("\r\n").splitlines()


class PublishedRecordTests(unittest.TestCase):
    def run_script(self, script: str, *args: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *map(str, args)],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_records_1e6_reproduce_exact_content(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "records.csv"
            checkpoint = Path(directory) / "checkpoint.json"
            self.run_script(
                "scan_L_records.py",
                "--max-n", 1_000_000,
                "--max-depth", 3000,
                "--output", output,
                "--checkpoint", checkpoint,
                "--progress-every", 0,
                "--checkpoint-every", 0,
            )
            expected = DATA / "records" / "records_1e6.csv"
            self.assertEqual(normalized_lines(output), normalized_lines(expected))
            self.assertEqual(
                hashlib.sha256(output.read_bytes()).hexdigest(),
                "0d6127ac715f0a00a21d125076dd0c4f3b6a4805bb3289329639bdee45c7cae8",
            )

    def test_champion_reproduces_exact_content(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "champion.csv"
            self.run_script(
                "analyze_champion.py",
                "--n0", 2_788_008_987,
                "--max-depth", 1000,
                "--output", output,
            )
            expected = DATA / "champions" / "champion_2788008987.csv"
            self.assertEqual(normalized_lines(output), normalized_lines(expected))

    def test_agreement_profiles_reproduce_exact_content(self):
        configs = (
            (63_728_127, 237, "agreement_63728127.csv"),
            (217_740_015, 249, "agreement_217740015.csv"),
            (2_788_008_987, 282, "agreement_2788008987.csv"),
        )
        with tempfile.TemporaryDirectory() as directory:
            for n0, depth, filename in configs:
                with self.subTest(n0=n0):
                    output = Path(directory) / filename
                    self.run_script(
                        "verify_lift.py",
                        "--n0", n0,
                        "--depth", depth,
                        "--max-q", 20,
                        "--agreement-csv", output,
                    )
                    expected = DATA / "agreements" / filename
                    self.assertEqual(normalized_lines(output), normalized_lines(expected))

    def test_all_published_record_rows_are_internally_recomputable(self):
        for path in sorted((DATA / "records").glob("records_*.csv")):
            with self.subTest(path=path.name):
                with path.open(newline="", encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
                best_r = -1
                best_l = -1
                for row in rows:
                    report = scan.analyze_n(int(row["n0"]), max_depth=3000)
                    expected = {
                        "exit_found": str(report.exit_found),
                        "exit_depth": str(report.exit_depth),
                        "p_stab": str(report.p_stab),
                        "L": str(report.L),
                        "exit_k": str(report.exit_k),
                        "K": str(report.K),
                        "before_exit": str(report.before_exit),
                        "after_exit": str(report.after_exit),
                        "max_orbit": str(report.max_orbit),
                        "strong_drop": str(report.strong_drop),
                    }
                    for key, value in expected.items():
                        self.assertEqual(row[key], value)
                    if row["type"] == "R_RECORD":
                        self.assertGreater(report.exit_depth, best_r)
                        best_r = report.exit_depth
                    elif row["type"] == "L_RECORD":
                        self.assertGreater(report.L, best_l)
                        best_l = report.L
                    else:
                        self.fail(f"Type de record inconnu: {row['type']}")

    def test_agreement_rows_all_report_match(self):
        for path in sorted((DATA / "agreements").glob("agreement_*.csv")):
            with self.subTest(path=path.name):
                with path.open(newline="", encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertTrue(rows)
                self.assertTrue(all(row["match"] == "True" for row in rows))

    def test_historical_progress_logs_have_explicit_completion(self):
        expected = {
            "progress_1e6.log": "Final Best R: n0=626331",
            "progress_1e8.log": "Final Best R: n0=63728127",
            "progress_1e9.log": "Final Best R: n0=217740015",
            "progress_1e10.log": "Final Best R: n0=2788008987",
        }
        for filename, final_record in expected.items():
            with self.subTest(filename=filename):
                text = (EVIDENCE / filename).read_text(encoding="utf-8")
                self.assertIn("\nDONE\n", text)
                self.assertIn(final_record, text)

    def test_incomplete_archive_sources_are_syntax_valid_only(self):
        archive = ROOT / "archive" / "incomplete-vmean"
        for source in archive.glob("*.py"):
            py_compile.compile(str(source), doraise=True)


if __name__ == "__main__":
    unittest.main()
