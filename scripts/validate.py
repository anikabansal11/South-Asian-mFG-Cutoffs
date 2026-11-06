"""Validate every CSV in data/ against scripts/schema.py.

Usage:  python scripts/validate.py [data_dir]
Exit status 1 if anything is malformed. Used by the GitHub Actions workflow.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from pydantic import BaseModel, ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema import Claim, Comparator, ScreeningRow, Study  # noqa: E402

FILES: dict[str, tuple[type[BaseModel], str]] = {
    "studies.csv": (Study, "study_id"),
    "comparators.csv": (Comparator, "comparator_id"),
    "claims.csv": (Claim, "claim_id"),
    "screening_log.csv": (ScreeningRow, "record_id"),
}


def read_rows(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        rows = []
        for row in reader:
            # Blank cells mean "not reported"; strip whitespace around values.
            rows.append({k: (v.strip() if v and v.strip() else None)
                         for k, v in row.items() if k is not None})
            if None in row:
                rows[-1]["__extra_cells__"] = "row has more cells than header"
        return header, rows


def validate_file(path: Path, model: type[BaseModel], id_field: str) -> tuple[list[str], list[BaseModel]]:
    errors: list[str] = []
    header, rows = read_rows(path)
    expected = list(model.model_fields)
    if header != expected:
        missing = [c for c in expected if c not in header]
        extra = [c for c in header if c not in expected]
        errors.append(f"{path.name}: header mismatch (missing={missing}, extra={extra}, "
                      f"order_ok={[c for c in header if c in expected] == [c for c in expected if c in header]})")
        return errors, []

    parsed: list[BaseModel] = []
    seen: set[str] = set()
    for i, row in enumerate(rows, start=2):  # line 1 is the header
        label = f"{path.name} line {i} ({row.get(id_field) or 'no id'})"
        if "__extra_cells__" in row:
            errors.append(f"{label}: {row['__extra_cells__']}")
            continue
        try:
            # Blank cells are dropped so field defaults (e.g. quality_flag=unrated)
            # apply; required fields left blank still fail as "Field required".
            obj = model(**{k: v for k, v in row.items() if v is not None})
        except ValidationError as exc:
            for e in exc.errors():
                loc = ".".join(str(x) for x in e["loc"]) or "row"
                errors.append(f"{label}: {loc}: {e['msg']}")
            continue
        ident = getattr(obj, id_field)
        if ident in seen:
            errors.append(f"{label}: duplicate {id_field} '{ident}'")
        seen.add(ident)
        parsed.append(obj)
    return errors, parsed


def cross_check(studies: list[Study], screening: list[ScreeningRow]) -> list[str]:
    errors: list[str] = []
    study_ids = {s.study_id for s in studies}
    for row in screening:
        if row.study_id and row.study_id not in study_ids:
            errors.append(f"screening_log {row.record_id}: study_id '{row.study_id}' "
                          "not found in studies.csv")
    logged = {r.study_id for r in screening if r.study_id}
    for s in studies:
        if s.study_id not in logged:
            errors.append(f"studies.csv {s.study_id}: no matching row in screening_log.csv")
        if s.inclusion_status == "included":
            decisions = {r.decision for r in screening if r.study_id == s.study_id}
            if "include" not in decisions:
                errors.append(f"studies.csv {s.study_id}: marked included but the "
                              "screening log has no 'include' decision for it")
    return errors


def main(argv: list[str]) -> int:
    data_dir = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[1] / "data"
    all_errors: list[str] = []
    parsed: dict[str, list[BaseModel]] = {}
    for name, (model, id_field) in FILES.items():
        path = data_dir / name
        if not path.exists():
            all_errors.append(f"missing file: {path}")
            continue
        errs, objs = validate_file(path, model, id_field)
        all_errors += errs
        parsed[name] = objs
        print(f"{name}: {len(objs)} valid row(s)")

    if "studies.csv" in parsed and "screening_log.csv" in parsed:
        all_errors += cross_check(parsed["studies.csv"], parsed["screening_log.csv"])  # type: ignore[arg-type]

    if all_errors:
        print(f"\n{len(all_errors)} problem(s):", file=sys.stderr)
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
