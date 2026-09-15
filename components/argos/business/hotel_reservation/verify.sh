#!/usr/bin/env bash
set -euo pipefail

component_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -m unittest discover -s "$component_dir/tests" -p 'test_*.py' -v
python3 "$component_dir/generate_demo.py"
"$component_dir/../../../../iris/launch.sh" \
  --component "$component_dir" \
  --input "$component_dir/demo/argos-scenario.json" \
  --output "$component_dir/demo/argos-output.json"

git_diff="$(git -C "$component_dir" diff -- demo 2>/dev/null || true)"
if [[ -n "$git_diff" ]]; then
  printf '%s\n' "Generated demo artifacts differ from the committed versions." >&2
  printf '%s\n' "$git_diff" >&2
  exit 1
fi
