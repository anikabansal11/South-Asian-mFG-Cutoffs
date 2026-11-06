"""Row schemas for the CSV files in data/.

Column order in each CSV must match the field order of the model below
(scripts/validate.py checks this).
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

PopulationGroup = Literal["south_asian_resident", "south_asian_diaspora"]
Setting = Literal[
    "community", "school", "university_students", "hospital_opd",
    "clinic_patients", "unclear",
]
Assessor = Literal[
    "trained_examiner", "clinician", "self_assessed", "unclear", "not_reported",
]
CutoffBasis = Literal[
    "guideline_8", "percentile_derived", "roc_derived", "cluster_derived",
    "empirical", "not_stated",
]
Quality = Literal["high", "moderate", "low", "unrated"]
InclusionStatus = Literal["included", "lead", "excluded"]
SourceChecked = Literal[
    "primary_full_text", "abstract_only", "secondary", "notes_only",
]
YesNo = Literal["yes", "no"]

# Prevalence percentages are reported to one decimal; allow rounding slack.
PCT_TOLERANCE = 0.06


class Study(BaseModel):
    model_config = ConfigDict(extra="forbid")

    study_id: str
    first_author: Optional[str] = None
    year: Optional[int] = None
    title: Optional[str] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    url: Optional[str] = None
    country: Optional[str] = None
    locale: Optional[str] = None
    population_group: Optional[PopulationGroup] = None
    setting: Optional[Setting] = None
    recruitment_notes: Optional[str] = None
    n_total: Optional[int] = None
    age_range_text: Optional[str] = None
    age_mean: Optional[float] = None
    age_sd: Optional[float] = None
    assessor: Optional[Assessor] = None
    assessor_notes: Optional[str] = None
    mfg_method_notes: Optional[str] = None
    cutoff_used: Optional[float] = None
    cutoff_basis: Optional[CutoffBasis] = None
    cutoff_notes: Optional[str] = None
    mean_mfg: Optional[float] = None
    sd_mfg: Optional[float] = None
    median_mfg: Optional[float] = None
    prev_at_8_pct: Optional[float] = None
    n_hirsute_at_8: Optional[int] = None
    prev_at_cutoff_pct: Optional[float] = None
    n_hirsute_at_cutoff: Optional[int] = None
    prev_unspecified_pct: Optional[float] = None
    quality_flag: Quality = "unrated"
    quality_notes: Optional[str] = None
    inclusion_status: InclusionStatus
    source_checked: SourceChecked
    human_verified: YesNo = "no"
    data_source: Optional[str] = None
    extractor: Optional[str] = None
    extraction_date: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("year")
    @classmethod
    def _year(cls, v):
        if v is not None and not 1961 <= v <= 2030:
            raise ValueError("year must be between 1961 and 2030")
        return v

    @field_validator("url")
    @classmethod
    def _url(cls, v):
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("url must start with http:// or https://")
        return v

    @field_validator("extraction_date")
    @classmethod
    def _date(cls, v):
        if v is not None:
            import datetime
            datetime.date.fromisoformat(v)
        return v

    @field_validator("prev_at_8_pct", "prev_at_cutoff_pct", "prev_unspecified_pct")
    @classmethod
    def _pct(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError("percentages must be between 0 and 100")
        return v

    @field_validator("cutoff_used", "mean_mfg", "median_mfg")
    @classmethod
    def _score(cls, v):
        # mFG (9 sites x 0-4) has a maximum of 36.
        if v is not None and not 0 <= v <= 36:
            raise ValueError("mFG values must be between 0 and 36")
        return v

    @field_validator("n_total", "n_hirsute_at_8", "n_hirsute_at_cutoff")
    @classmethod
    def _count(cls, v):
        if v is not None and v < 0:
            raise ValueError("counts must be >= 0")
        return v

    @model_validator(mode="after")
    def _cross_field(self):
        errs: list[str] = []

        if self.cutoff_used is not None and self.cutoff_basis is None:
            errs.append("cutoff_basis is required when cutoff_used is set")
        if self.cutoff_basis == "guideline_8" and self.cutoff_used != 8:
            errs.append("cutoff_basis=guideline_8 requires cutoff_used=8")
        if self.cutoff_used == 8 and self.prev_at_cutoff_pct is not None:
            errs.append("cutoff_used is 8: put prevalence in prev_at_8_pct, "
                        "not prev_at_cutoff_pct")
        if self.prev_at_cutoff_pct is not None and self.cutoff_used is None:
            errs.append("prev_at_cutoff_pct needs cutoff_used")
        if self.n_hirsute_at_cutoff is not None and self.prev_at_cutoff_pct is None:
            errs.append("n_hirsute_at_cutoff needs prev_at_cutoff_pct")
        if self.n_hirsute_at_8 is not None and self.prev_at_8_pct is None:
            errs.append("n_hirsute_at_8 needs prev_at_8_pct")

        if self.n_total:
            for n_field, p_field in (
                ("n_hirsute_at_8", "prev_at_8_pct"),
                ("n_hirsute_at_cutoff", "prev_at_cutoff_pct"),
            ):
                n, p = getattr(self, n_field), getattr(self, p_field)
                if n is not None:
                    if n > self.n_total:
                        errs.append(f"{n_field} exceeds n_total")
                    elif p is not None and abs(100 * n / self.n_total - p) > PCT_TOLERANCE:
                        errs.append(
                            f"{p_field}={p} disagrees with {n_field}/n_total="
                            f"{100 * n / self.n_total:.2f}"
                        )

        if self.inclusion_status == "included":
            for f in ("first_author", "year", "country", "population_group",
                      "setting", "n_total", "assessor", "data_source",
                      "extractor", "extraction_date"):
                if getattr(self, f) is None:
                    errs.append(f"{f} is required for included studies")
            if not (self.doi or self.pmid or self.url):
                errs.append("one of doi, pmid or url is required for included studies")
            if self.source_checked not in ("primary_full_text", "abstract_only"):
                errs.append("included studies must be checked against the paper "
                            "itself (primary_full_text or abstract_only)")
            if all(getattr(self, f) is None for f in
                   ("cutoff_used", "mean_mfg", "prev_at_8_pct", "prev_unspecified_pct")):
                errs.append("included studies need at least one of cutoff_used, "
                            "mean_mfg, prev_at_8_pct, prev_unspecified_pct")
        if self.inclusion_status == "excluded" and not self.notes:
            errs.append("excluded studies need a reason in notes")

        if errs:
            raise ValueError("; ".join(errs))
        return self


class Comparator(BaseModel):
    """Non-South-Asian (or pooled) cutoffs to plot against, e.g. P-PUP."""
    model_config = ConfigDict(extra="forbid")

    comparator_id: str
    group: str
    cutoff_min: float
    cutoff_max: float
    basis: str
    source: str
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    source_checked: SourceChecked
    notes: Optional[str] = None

    @model_validator(mode="after")
    def _range(self):
        if self.cutoff_min > self.cutoff_max:
            raise ValueError("cutoff_min > cutoff_max")
        if not 0 <= self.cutoff_min <= 36:
            raise ValueError("cutoff outside 0-36")
        return self


class Claim(BaseModel):
    """Contested statements, recorded with their citation but not resolved."""
    model_config = ConfigDict(extra="forbid")

    claim_id: str
    claim: str
    direction: Literal["higher", "lower", "neutral", "unclear"]
    stated_in: str
    cited_to: Optional[str] = None
    checked: YesNo = "no"
    notes: Optional[str] = None


class ScreeningRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    study_id: Optional[str] = None
    first_author: Optional[str] = None
    year: Optional[int] = None
    title: str
    source_db: str
    search_date: str
    stage: Literal["identified", "title_abstract", "full_text"]
    decision: Literal["unscreened", "include", "lead", "exclude"]
    exclusion_reason: Optional[Literal[
        "not_south_asian", "no_mfg", "no_cutoff_or_prevalence",
        "selected_on_outcome", "duplicate_or_overlap", "comparator_only",
        "not_primary_data", "other",
    ]] = None
    screener: str
    notes: Optional[str] = None

    @field_validator("search_date")
    @classmethod
    def _date(cls, v):
        import datetime
        datetime.date.fromisoformat(v)
        return v

    @model_validator(mode="after")
    def _reason(self):
        if self.decision == "exclude" and self.exclusion_reason is None:
            raise ValueError("exclude decisions need an exclusion_reason")
        if self.decision != "exclude" and self.exclusion_reason is not None:
            raise ValueError("exclusion_reason only applies to exclude decisions")
        return self
