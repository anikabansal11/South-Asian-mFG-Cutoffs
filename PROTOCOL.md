# Review protocol

**Question.** What modified Ferriman-Gallwey (mFG) cutoffs and prevalence figures have been published for South Asian and South Asian diaspora populations, how were they derived, and how do they compare with the conventional cutoff of 8 and with the ethnicity-specific cutoffs from P-PUP?

**Status.** Draft v0.1, 2026-11-05. Seeded from web searches and project notes. The formal database search (below) has **not** been run yet.

## Eligibility

Include a study if all of these hold:

1. Participants are women of South Asian origin (India, Pakistan, Bangladesh, Sri Lanka, Nepal, Bhutan, Maldives, Afghanistan) living in South Asia, or South Asian diaspora women anywhere.
2. Hirsutism was scored with the Ferriman-Gallwey or modified Ferriman-Gallwey scale.
3. The paper reports at least one of: a proposed or applied cutoff, a prevalence of hirsutism, or an mFG distribution (mean, median or percentiles) in a sample that was not chosen because it was already hirsute.

Record, but flag, studies from hospital outpatient clinics or selected student samples. Setting and assessor are columns, not exclusion criteria, because differences in method may explain much of the spread in prevalence.

Exclude: samples enrolled because they already had hirsutism or PCOS (no population prevalence or cutoff can be read from them); non-South-Asian populations (keep as comparators only); reviews with no primary data (record their claims in `data/claims.csv`).

## Search

Run each string in PubMed and Google Scholar and log the date, database, string and hit count in `data/screening_log.csv`.

```
("Ferriman" OR hirsutism) AND (India OR Pakistan OR Bangladesh OR "Sri Lanka" OR Nepal OR "South Asian" OR Asian)
("Ferriman" OR hirsutism) AND (cutoff OR "cut-off" OR normative OR prevalence) AND (Indian OR Pakistani OR Bengali OR Sri Lankan OR Nepali)
("Ferriman" OR hirsutism) AND (diaspora OR "British Asian" OR "Asian American" OR "Indian American" OR "UK" OR "US") AND "South Asian"
```

Also: chase reference lists of every included study (Josyula 2024 Table 2 lists Indian studies with their cutoffs), search regional journals (Pak J Med Sci, Indian J Endocrinol Metab, Sri Lanka J Diabetes Endocrinol Metab, Nepal journals via NepJOL, Bangladesh via BanglaJOL) and use "cited by" on Josyula 2024 and on the P-PUP paper.

## Screening and extraction

1. Screen titles and abstracts, then full texts. Record every decision and an exclusion reason (see the enum in `scripts/schema.py`).
2. Extract into `data/studies.csv` using `DATA_DICTIONARY.md`. Copy values exactly as printed. If a number is not in the paper, leave the cell blank; do not compute it, and note any implied value in the notes column.
3. Set `source_checked` honestly. Only `primary_full_text` or `abstract_only` rows can have status `included`.
4. Set `human_verified` to `yes` only after a person has compared the row with the paper.
5. Re-extract about 20% of included studies (a second person, or yourself a week later) into `data/reextraction_check.csv` and run `python scripts/agreement.py`. Resolve every disagreement against the paper.
6. If key numbers are missing, email the corresponding author and log the request in the study's notes.

## Handling overlaps and disagreements

- If two papers appear to use the same cohort (see `somasundaram_2015_srilanka` and screening record SL04), keep both rows, link them in the notes, and exclude one from any pooled counts.
- Do not resolve contradictory claims (for example, whether South Asian cutoffs are higher or lower than elsewhere). Record each in `data/claims.csv` with where it was stated and what it cites.

## Quality flags

`quality_flag` is `unrated` until you have agreed a rubric. A suggested starting point, scored per study and written into `quality_notes`: random or consecutive sampling; community rather than clinic setting; trained assessors with reported agreement; age range reported; exclusion of endocrine disease; cutoff derivation method described. Rate `low` if fewer than two are met, `high` if five or six, otherwise `moderate`.

## Reporting

Follow PRISMA 2020 for the flow diagram. This is a descriptive review without meta-analysis, so a table and the dot plot are the main outputs. Consider registering the protocol (for example on OSF) before the full search, and have a clinician mentor review before anything is made public.
