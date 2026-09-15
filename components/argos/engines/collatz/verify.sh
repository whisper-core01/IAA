#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 -m unittest discover -s "$ROOT/tests" -v
python3 -m py_compile   "$ROOT/scripts/collatz_a001_memory_vs_residue.py"   "$ROOT/scripts/collatz_a001_memory_vs_residue_gpu.py"   "$ROOT/scripts/collatz_zone_conditioned_k_test.py"

echo "COLLATZ_SCAN_SOFTWARE_CHECK_PASS"
echo "NON_PROOF=Collatz Scan ne prouve pas la conjecture de Collatz."

