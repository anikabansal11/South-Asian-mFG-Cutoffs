"""Copy the CSVs the explorer reads into docs/data/ (GitHub Pages serves docs/).

CI runs this and fails if docs/data differs from what is committed, so the
published site can never drift from data/.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_FILES = ["studies.csv", "comparators.csv", "claims.csv"]

(ROOT / "docs" / "data").mkdir(parents=True, exist_ok=True)
for name in SITE_FILES:
    shutil.copyfile(ROOT / "data" / name, ROOT / "docs" / "data" / name)
print("copied:", ", ".join(SITE_FILES))
