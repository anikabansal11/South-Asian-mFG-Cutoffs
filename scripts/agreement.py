"""Agreement between first and second extraction (the ~20% re-extraction check).

Fill data/reextraction_check.csv with one row per (study, field):
    study_id,field,first_value,second_value
Numbers are compared with a small tolerance, everything else as trimmed,
case-insensitive text. Blank == blank counts as agreement.

Usage:  python scripts/agreement.py [path/to/reextraction_check.csv]
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


def same(a: str, b: str, tol: float = 0.05) -> bool:
    a, b = (a or "").strip(), (b or "").strip()
    try:
        return abs(float(a) - float(b)) <= tol
    except ValueError:
        return a.lower() == b.lower()


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "reextraction_check.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        print("No re-extraction rows yet.")
        return 0
    by_field: dict[str, list[bool]] = defaultdict(list)
    disagreements = []
    for r in rows:
        ok = same(r["first_value"], r["second_value"])
        by_field[r["field"]].append(ok)
        if not ok:
            disagreements.append(r)
    total = sum(len(v) for v in by_field.values())
    agree = sum(sum(v) for v in by_field.values())
    print(f"Overall agreement: {agree}/{total} = {100 * agree / total:.1f}% "
          f"across {len({r['study_id'] for r in rows})} study(ies)")
    for field, v in sorted(by_field.items()):
        print(f"  {field:24s} {sum(v)}/{len(v)}")
    if disagreements:
        print("\nDisagreements to resolve against the paper:")
        for r in disagreements:
            print(f"  {r['study_id']}: {r['field']}: '{r['first_value']}' vs '{r['second_value']}'")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
