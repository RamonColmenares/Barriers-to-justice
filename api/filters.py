"""
Filter parsing and application utilities for the juvenile immigration API.
This centralizes all filter logic so charts and stats use the same behavior.

Aligned with 4_data_analysis.ipynb:
- Time periods ("policy eras") derived from hearing_date_combined/COMP_DATE:
    * Trump Era I:   2018-04-06 <= date < 2021-01-20
    * Biden:         2021-01-20 <= date < 2025-04-01
    * Trump Era II:  2025-04-01 <= date
- Representation normalization identical to the notebook.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, List
import pandas as pd

# Time ranges (inclusive start, exclusive end when present)
TIME_PERIODS: Dict[str, Optional[Tuple[pd.Timestamp, Optional[pd.Timestamp]]]] = {
    "all": None,
    "trump1": (pd.Timestamp("2018-04-06"), pd.Timestamp("2021-01-20")),
    "biden":  (pd.Timestamp("2021-01-20"), pd.Timestamp("2025-04-01")),
    "trump2": (pd.Timestamp("2025-04-01"), None),
}

REPRESENTATION_VALUES = {
    "represented": {"Has Legal Representation", "Yes", "Y", "1", 1, True},
    "unrepresented": {"No Legal Representation", "No", "N", "0", 0, False}
}

# Priority of date columns (first existing will be used)
DATE_COLUMNS_PRIORITY: List[str] = [
    "hearing_date_combined",
    "COMP_DATE",
    "LATEST_HEARING",
    "HEARING_DATE",
    "DECISION_DATE",
    "FILING_DATE",
]

@dataclass(frozen=True)
class Filters:
    time_period: str = "all"        # "all" | "trump1" | "biden" | "trump2"
    representation: str = "all"     # "all" | "represented" | "unrepresented"
    case_type: str = "all"          # "all" | <value from CASE_TYPE>

    @classmethod
    def from_query(cls, args: Dict[str, Any]) -> "Filters":
        # Accept both snake_case and camelCase
        tp = (args.get("time_period") or args.get("timePeriod") or "all")
        rep = (args.get("representation") or "all")
        ct = (args.get("case_type") or args.get("caseType") or "all")
        if isinstance(tp, str):
            tp = tp.strip().lower()
        if isinstance(rep, str):
            rep = rep.strip().lower()
        if isinstance(ct, str):
            ct = ct.strip()
        if tp not in TIME_PERIODS:
            tp = "all"
        if rep not in {"all", "represented", "unrepresented"}:
            rep = "all"
        if not ct:
            ct = "all"
        return cls(time_period=tp, representation=rep, case_type=ct)

def _pick_date_col(df: pd.DataFrame) -> Optional[str]:
    for col in DATE_COLUMNS_PRIORITY:
        if col in df.columns:
            return col
    for col in df.columns:
        if "date" in col.lower():
            return col
    return None

def _ensure_datetime(df: pd.DataFrame, col: str) -> pd.DataFrame:
    out = df.copy()
    out[col] = pd.to_datetime(out[col], errors="coerce", utc=False)
    return out

def _normalize_representation_column(df: pd.DataFrame) -> pd.Series:
    """
    Normalized values:
      "Has Legal Representation" | "No Legal Representation" | "Unknown"
    """
    if "HAS_LEGAL_REP" in df.columns:
        s = df["HAS_LEGAL_REP"]
        def map_val(x):
            if pd.isna(x):
                return "Unknown"
            xv = str(x).strip()
            if xv in REPRESENTATION_VALUES["represented"] or xv.lower() in {"has legal representation", "true"}:
                return "Has Legal Representation"
            if xv in REPRESENTATION_VALUES["unrepresented"] or xv.lower() in {"no legal representation", "false"}:
                return "No Legal Representation"
            return "Unknown"
        return s.map(map_val)
    if "REPRESENTATION_LEVEL" in df.columns:
        s = df["REPRESENTATION_LEVEL"].astype(str).str.strip().str.upper()
        return s.map(
            lambda x: "Has Legal Representation" if x in {"COURT","BOARD"}
            else ("No Legal Representation" if x == "NO_REPRESENTATION" else "Unknown")
        )
    return pd.Series(["Unknown"] * len(df), index=df.index)

def apply_filters(df: pd.DataFrame, filters: Filters) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    data = df.copy()

    # Time period
    date_col = _pick_date_col(data)
    if date_col:
        data = _ensure_datetime(data, date_col)
        if filters.time_period != "all":
            start, end = TIME_PERIODS[filters.time_period]  # type: ignore
            mask = pd.Series(True, index=data.index)
            if start is not None:
                mask &= data[date_col] >= start
            if end is not None:
                mask &= data[date_col] < end
            data = data[mask]

    # Representation
    if filters.representation != "all":
        rep_norm = _normalize_representation_column(data)
        if filters.representation == "represented":
            data = data[rep_norm == "Has Legal Representation"]
        else:
            data = data[rep_norm == "No Legal Representation"]

    # Case type
    if filters.case_type != "all" and "CASE_TYPE" in data.columns:
        data = data[
            data["CASE_TYPE"].astype(str).str.strip().str.lower()
            == str(filters.case_type).strip().lower()
        ]

    return data

def filter_options(df: pd.DataFrame) -> Dict[str, Any]:
    opts: Dict[str, Any] = {
        "time_period": list(TIME_PERIODS.keys()),
        "representation": ["all", "represented", "unrepresented"],
        "case_type": ["all"],
    }
    if df is not None and not df.empty and "CASE_TYPE" in df.columns:
        values = (
            df["CASE_TYPE"].dropna().astype(str).str.strip().replace({"": None}).dropna().unique().tolist()
        )
        values = sorted({v for v in values})
        opts["case_type"] = ["all"] + values
    return opts
