import re
import pandas as pd

def _tokens(name):
    return [x for x in re.split(r"[^a-zA-Z0-9]+", str(name).lower()) if x]

def infer_roles(df):
    roles = {
        "id_candidates": [],
        "datetime_candidates": [],
        "numeric_columns": list(df.select_dtypes(include="number").columns),
        "categorical_columns": [],
        "possible_targets": [],
    }
    n = max(len(df), 1)
    for col in df.columns:
        s = df[col]
        low = str(col).lower()
        toks = _tokens(col)
        nunique = s.nunique(dropna=True)
        ur = nunique / n

        if pd.api.types.is_datetime64_any_dtype(s):
            roles["datetime_candidates"].append(col)
        elif any(t in low for t in ("date","time","timestamp","created","updated")):
            parsed = pd.to_datetime(s, errors="coerce")
            if parsed.notna().mean() >= 0.70:
                roles["datetime_candidates"].append(col)

        if ur >= 0.90 and nunique > 20 and (
            any(t in toks for t in ("id","uuid","guid","key","code"))
            or s.dtype == "object"
        ):
            roles["id_candidates"].append(col)

        if not pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_datetime64_any_dtype(s):
            roles["categorical_columns"].append(col)

        if (
            low in ("target","label","outcome","response","class","y")
            or low.endswith("_target") or low.startswith("target_")
        ):
            roles["possible_targets"].append(col)
    return roles
