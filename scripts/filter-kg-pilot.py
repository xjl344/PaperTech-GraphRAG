"""Revalidate the archived v4 mechanism pilot without model calls."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from papertech.kg_rebuild_filter import filter_archived, VERSION


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input-run", required=True, help="v4 run directory containing checkpoint.json")
args = parser.parse_args()
run_dir = (ROOT / args.input_run).resolve() if not Path(args.input_run).is_absolute() else Path(args.input_run)
out, payload = filter_archived(ROOT, run_dir)
print({"version": VERSION, "report": str(out / "filter-report.json"), "summary": payload["summary"]})
