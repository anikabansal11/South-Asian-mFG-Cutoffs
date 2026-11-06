import csv
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402


def run(data_dir: Path) -> int:
    return validate.main(["validate.py", str(data_dir)])


@pytest.fixture()
def data_copy(tmp_path):
    dst = tmp_path / "data"
    shutil.copytree(ROOT / "data", dst)
    return dst


def edit(path: Path, study_id: str, **changes):
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols = reader.fieldnames
        rows = list(reader)
    for r in rows:
        if r[cols[0]] == study_id:
            r.update(changes)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def test_repo_data_is_valid():
    assert run(ROOT / "data") == 0


def test_prevalence_must_match_counts(data_copy, capsys):
    edit(data_copy / "studies.csv", "bibi_2024_peshawar", prev_at_8_pct="40.0")
    assert run(data_copy) == 1
    assert "disagrees with n_hirsute_at_8" in capsys.readouterr().err


def test_guideline_8_must_be_8(data_copy, capsys):
    edit(data_copy / "studies.csv", "bibi_2024_peshawar", cutoff_used="6")
    assert run(data_copy) == 1
    assert "guideline_8 requires cutoff_used=8" in capsys.readouterr().err


def test_included_needs_checked_source(data_copy, capsys):
    edit(data_copy / "studies.csv", "bibi_2024_peshawar", source_checked="secondary")
    assert run(data_copy) == 1
    assert "primary_full_text or abstract_only" in capsys.readouterr().err


def test_percentage_out_of_range(data_copy, capsys):
    edit(data_copy / "studies.csv", "josyula_2024_bengaluru", prev_at_cutoff_pct="150")
    assert run(data_copy) == 1


def test_unknown_enum_value(data_copy, capsys):
    edit(data_copy / "studies.csv", "josyula_2024_bengaluru", setting="hospital")
    assert run(data_copy) == 1
    assert "setting" in capsys.readouterr().err


def test_duplicate_id(data_copy, capsys):
    p = data_copy / "claims.csv"
    text = p.read_text(encoding="utf-8").splitlines()
    p.write_text("\n".join(text + [text[1]]) + "\n", encoding="utf-8")
    assert run(data_copy) == 1
    assert "duplicate" in capsys.readouterr().err


def test_header_mismatch(data_copy, capsys):
    p = data_copy / "claims.csv"
    p.write_text(p.read_text(encoding="utf-8").replace("claim_id", "id", 1), encoding="utf-8")
    assert run(data_copy) == 1
    assert "header mismatch" in capsys.readouterr().err


def test_study_missing_from_screening_log(data_copy, capsys):
    p = data_copy / "screening_log.csv"
    lines = [ln for ln in p.read_text(encoding="utf-8").splitlines()
             if "kerala_pilot_2026_unverified" not in ln]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert run(data_copy) == 1
    assert "no matching row in screening_log" in capsys.readouterr().err
