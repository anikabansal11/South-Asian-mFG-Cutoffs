# Data dictionary

All files are UTF-8 CSV with a header row. A blank cell means "not reported" (not zero). Column order is enforced by `scripts/validate.py`; the authoritative definitions and allowed values live in `scripts/schema.py`.

## data/studies.csv (one row per study)

| Column | Meaning |
|---|---|
| `study_id` | Unique slug: `firstauthor_year_place`. Rows not yet checked against the paper end in `_unverified`. |
| `first_author`, `year`, `title`, `journal` | Citation. |
| `doi`, `pmid`, `url` | At least one is needed for included studies. |
| `country`, `locale` | Country and the city, institution or district. |
| `population_group` | `south_asian_resident` or `south_asian_diaspora`. |
| `setting` | `community`, `school`, `university_students`, `hospital_opd`, `clinic_patients`, `unclear`. |
| `recruitment_notes` | How participants were found and excluded. |
| `n_total` | Women analysed. |
| `age_range_text`, `age_mean`, `age_sd` | Age as reported. State in the text whether the range is eligibility or observed. |
| `assessor` | `trained_examiner`, `clinician`, `self_assessed`, `unclear`, `not_reported`. |
| `assessor_notes`, `mfg_method_notes` | Training, agreement statistics, number of body sites, scoring quirks. |
| `cutoff_used` | The mFG threshold the study applied or proposed (0 to 36). Blank if none stated. |
| `cutoff_basis` | `guideline_8`, `percentile_derived`, `roc_derived`, `cluster_derived`, `empirical`, `not_stated`. Required whenever `cutoff_used` is set. |
| `cutoff_notes` | How the cutoff was derived and in which sample. |
| `mean_mfg`, `sd_mfg`, `median_mfg` | Score distribution in the whole sample as reported. |
| `prev_at_8_pct`, `n_hirsute_at_8` | Prevalence of mFG >=8 (percent, count). |
| `prev_at_cutoff_pct`, `n_hirsute_at_cutoff` | Prevalence at the study's own cutoff when it is not 8. |
| `prev_unspecified_pct` | A headline prevalence whose threshold the paper does not state. |
| `quality_flag`, `quality_notes` | `high`, `moderate`, `low`, `unrated`, with reasons. See `PROTOCOL.md`. |
| `inclusion_status` | `included`, `lead` (not yet verified), `excluded`. |
| `source_checked` | `primary_full_text`, `abstract_only`, `secondary` (read about in another paper), `notes_only`. |
| `human_verified` | `yes` once a person has checked the row against the paper. |
| `data_source`, `extractor`, `extraction_date` | Provenance. |
| `notes` | Anything else, including overlaps with other papers. |

Automatic checks: percentages are 0 to 100; counts divided by `n_total` must match the stated percentage to within rounding; `guideline_8` implies `cutoff_used` = 8; prevalence at a non-8 cutoff needs `cutoff_used`; included rows need the fields listed in `schema.py`.

## data/comparators.csv

Cutoffs from outside South Asia (and the guideline range) to plot against. `cutoff_min` equals `cutoff_max` for a single value. `source_checked` uses the same values as above.

## data/claims.csv

Statements that sources disagree on. `direction` says whether the claim is that South Asian cutoffs are `higher`, `lower`, `neutral` or `unclear`. `stated_in` is where it appears and `cited_to` is what that source cites for it.

## data/screening_log.csv

One row per record screened, with stage (`identified`, `title_abstract`, `full_text`), decision (`unscreened`, `include`, `lead`, `exclude`) and, for exclusions, a reason. `study_id` links to `studies.csv`.

## data/reextraction_check.csv

Long format (`study_id, field, first_value, second_value`) for the 20% agreement check; summarised by `scripts/agreement.py`.
