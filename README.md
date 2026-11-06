# mFG hirsutism cutoffs in South Asian populations

An open, structured database of published modified Ferriman-Gallwey (mFG) cutoffs and hirsutism prevalence figures for South Asian and South Asian diaspora women, with an interactive explorer.

**Why.** Hirsutism is usually defined as mFG >= 8, a threshold drawn from Caucasian data. The P-PUP individual-participant-data study (Eur J Endocrinol 2025) derived ethnicity-specific cutoffs from 9,829 women in 8 countries, ranging from 4 to 8, but none of those countries is in South Asia. Published South Asian figures vary a lot: a community study in Bengaluru proposed a cutoff of 5 and found 1.8% prevalence at >=8 versus 9.9% at >=5, while a Peshawar outpatient sample reported 56.9% at >=8. This project collects those figures side by side with how each was measured, so differences in method can be told apart from differences in people.

**Status: early draft.** Three studies are extracted from their papers (two from full text, one from the abstract only) and four more are leads. The formal PubMed and Google Scholar search has not been run. Every row is marked `human_verified = no` until a person has checked it against the paper. Nothing here is medical advice, and the database does not recommend a cutoff.

## What is in the repo

| Path | What |
|---|---|
| `data/studies.csv` | One row per study (see `DATA_DICTIONARY.md`) |
| `data/comparators.csv` | P-PUP and other non-South-Asian cutoffs to compare against |
| `data/claims.csv` | Contested statements, recorded with their citations but not resolved |
| `data/screening_log.csv` | Every record found, screened, included or excluded, and why |
| `PROTOCOL.md` | Question, eligibility, search strings, extraction and quality rules |
| `scripts/schema.py`, `scripts/validate.py` | Schema (pydantic) and validator |
| `scripts/agreement.py` | Agreement statistic for the 20% re-extraction check |
| `docs/` | Static explorer (open `docs/index.html` through any web server, or via GitHub Pages) |
| `.github/workflows/validate.yml` | CI: fails on malformed rows or a stale `docs/data` |

## Working with it

```bash
pip install -r requirements.txt
python scripts/validate.py          # check the CSVs
pytest -q                           # tests for the validator
python scripts/build_site.py        # copy data/ into docs/data/ after any edit
python -m http.server -d docs 8000  # preview the explorer at http://localhost:8000
```

To publish: push to GitHub, then Settings -> Pages -> deploy from branch `main`, folder `/docs`.

## Adding a study

1. Add a row to `data/screening_log.csv` (decision `include`, a `study_id`).
2. Add the matching row to `data/studies.csv`. Copy numbers exactly as printed; leave blanks for anything the paper does not say.
3. Run `python scripts/validate.py`, then `python scripts/build_site.py`, and commit.

## Known limitations

- The seed rows were extracted with AI assistance from open-access pages and need human verification. Several papers have internal inconsistencies, listed in each row's `quality_notes` (for example Bibi 2024's Table I and Table II).
- Samples, assessors and cutoff-derivation methods differ, so the dot plot should be read as a map of what exists, not as a pooled estimate.
- The "2023 guideline 4 to 6" comparator comes from project notes and is unverified. The claim that South Asian cutoffs are lower (or higher) than elsewhere is recorded in `claims.csv` and deliberately not resolved.
- The P-PUP statement that no South Asian country contributed was checked against the abstract only.

## Sources

P-PUP: Eur J Endocrinol 2025;192(3):228-239, doi 10.1093/ejendo/lvaf030. Josyula et al., Indian J Endocrinol Metab 2024;28:391-6. Bibi et al., Pak J Med Sci 2024;40(3):332-6, doi 10.12669/pjms.40.3.8138. Somasundaram et al., Sri Lanka J Diabetes Endocrinol Metab 2015;5:51-5, doi 10.4038/sjdem.v5i1.7274.
