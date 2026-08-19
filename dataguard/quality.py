import math, re
from collections import defaultdict
import numpy as np
import pandas as pd
from .models import Issue

NONNEGATIVE_HINTS = (
    "age","amount","price","cost","revenue","sales","quantity","qty",
    "count","duration","distance","balance","income","salary","weight","height","volume"
)

def _norm_text(x):
    if pd.isna(x): return ""
    return re.sub(r"\s+", " ", str(x).strip().lower())

def _penalty(base, prevalence=1.0):
    return min(base, base * max(0.25, min(1.0, prevalence * 4)))

def run_quality_checks(df, id_columns=None):
    issues = []
    n = len(df)
    if n == 0:
        return [Issue("CRITICAL","Volume","Dataset is empty",
                      evidence="0 rows were loaded.",
                      recommendation="Check the file or upstream extraction.",
                      penalty=100)]

    dup_count = int(df.duplicated().sum())
    if dup_count:
        rate = dup_count / n
        sev = "HIGH" if rate >= 0.05 else "MEDIUM"
        issues.append(Issue(
            sev,"Uniqueness","Duplicate rows detected",
            evidence=f"{dup_count:,} duplicate rows ({rate:.2%}).",
            recommendation="Verify whether duplicates are legitimate events; otherwise deduplicate using a documented business key.",
            penalty=_penalty(8 if sev=="HIGH" else 4, rate)
        ))

    for col in [c for c in (id_columns or []) if c in df.columns]:
        s = df[col]
        dup = int(s.dropna().duplicated().sum())
        miss = int(s.isna().sum())
        if dup:
            rate = dup / max(int(s.notna().sum()),1)
            issues.append(Issue(
                "HIGH","Uniqueness","Candidate identifier is not unique",col,
                f"{dup:,} repeated non-null values ({rate:.2%}).",
                "Confirm the grain. If this is an entity ID rather than a row key, use it as a grouping variable.",
                _penalty(7,rate)
            ))
        if miss:
            rate = miss/n
            issues.append(Issue(
                "MEDIUM","Completeness","Missing values in candidate identifier",col,
                f"{miss:,} missing IDs ({rate:.2%}).",
                "Investigate missing identifiers before joining, deduplicating, or group splitting.",
                _penalty(4,rate)
            ))

    for col in df.columns:
        s = df[col]
        missing = int(s.isna().sum())
        mr = missing/n

        if mr >= .50:
            issues.append(Issue("HIGH","Completeness","Very high missingness",col,
                f"{missing:,} missing values ({mr:.2%}).",
                "Investigate whether the field is usable or structurally missing. Do not impute before understanding the mechanism.",
                _penalty(8,mr)))
        elif mr >= .20:
            issues.append(Issue("MEDIUM","Completeness","High missingness",col,
                f"{missing:,} missing values ({mr:.2%}).",
                "Profile missingness by target, time, and key segments before choosing imputation.",
                _penalty(5,mr)))
        elif mr >= .05:
            issues.append(Issue("LOW","Completeness","Moderate missingness",col,
                f"{missing:,} missing values ({mr:.2%}).",
                "Document and handle missing values explicitly in the modeling pipeline.",
                _penalty(2,mr)))

        nunique = s.nunique(dropna=True)
        if nunique <= 1:
            issues.append(Issue("MEDIUM","Validity","Constant or empty feature",col,
                f"Only {nunique} distinct non-null value(s).",
                "Remove from modeling unless it has a documented operational purpose.",3))
            continue

        if pd.api.types.is_numeric_dtype(s):
            arr = pd.to_numeric(s,errors="coerce")
            clean = arr.replace([np.inf,-np.inf],np.nan)
            inf_count = int(arr.notna().sum() - clean.notna().sum())
            if inf_count:
                issues.append(Issue("HIGH","Validity","Infinite numeric values",col,
                    f"{inf_count:,} infinite values.",
                    "Trace the transformation that created infinity; replace only after validating the cause.",6))
            clean = clean.dropna()
            if len(clean) >= 20:
                q1,q3 = clean.quantile([.25,.75]); iqr = q3-q1
                if pd.notna(iqr) and iqr > 0:
                    lo,hi = q1-3*iqr,q3+3*iqr
                    out = int(((clean<lo)|(clean>hi)).sum())
                    rate = out/len(clean)
                    if rate >= .01:
                        sev = "MEDIUM" if rate >= .05 else "LOW"
                        issues.append(Issue(sev,"Distribution","Extreme values detected",col,
                            f"{out:,} values ({rate:.2%}) fall outside 3×IQR fences [{lo:.4g}, {hi:.4g}].",
                            "Do not delete automatically. Check errors, units, and legitimate tail behavior.",
                            _penalty(4 if sev=="MEDIUM" else 2,rate)))
                if len(clean) >= 100:
                    sk = float(clean.skew())
                    if math.isfinite(sk) and abs(sk)>=3:
                        issues.append(Issue("LOW","Distribution","Highly skewed numeric feature",col,
                            f"Sample skewness = {sk:.2f}.",
                            "Consider robust scaling, a monotonic transform, or robust models.",1))
                low = str(col).lower()
                if any(t in low for t in NONNEGATIVE_HINTS):
                    neg = int((clean<0).sum())
                    if neg:
                        rate=neg/len(clean)
                        issues.append(Issue("MEDIUM","Validity","Negative values in a likely non-negative field",col,
                            f"{neg:,} negative values ({rate:.2%}).",
                            "Verify sign conventions and whether negatives are legitimate reversals/adjustments.",
                            _penalty(4,rate)))

        elif pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s):
            nonnull = s.dropna().astype(str)
            if len(nonnull)==0: continue

            stripped = nonnull.str.strip()
            ws = int((stripped!=nonnull).sum())
            if ws:
                rate=ws/len(nonnull)
                issues.append(Issue("LOW","Consistency","Leading/trailing whitespace",col,
                    f"{ws:,} values ({rate:.2%}) contain surrounding whitespace.",
                    "Normalize whitespace in a reproducible cleaning step.",_penalty(2,rate)))

            numeric = pd.to_numeric(nonnull.str.replace(",","",regex=False),errors="coerce")
            nr = numeric.notna().mean()
            if nr >= .90 and nonnull.nunique()>5:
                issues.append(Issue("MEDIUM","Validity","Numeric values stored as text",col,
                    f"{nr:.2%} of non-null strings can be parsed as numbers.",
                    "Convert after confirming separators, decimal symbols, and units.",4))

            low = str(col).lower()
            if any(t in low for t in ("date","time","timestamp","datetime")):
                parsed = pd.to_datetime(nonnull,errors="coerce")
                pr = parsed.notna().mean()
                if .50 <= pr < .95:
                    issues.append(Issue("HIGH","Validity","Partially invalid date/time values",col,
                        f"Only {pr:.2%} of non-null values parse as datetime.",
                        "Inspect invalid formats and timezone conventions before conversion.",6))

            if nonnull.nunique() <= min(500,max(25,int(n*.20))):
                groups=defaultdict(set)
                for v in nonnull.unique():
                    groups[_norm_text(v)].add(v)
                collisions={k:sorted(v) for k,v in groups.items() if k and len(v)>1}
                if collisions:
                    sample=list(collisions.values())[:5]
                    issues.append(Issue("MEDIUM","Consistency","Inconsistent categorical labels",col,
                        f"{len(collisions)} normalized group(s) have multiple spellings. Examples: {sample}",
                        "Standardize case/whitespace only after confirming semantic equivalence.",4))

            ur = nonnull.nunique()/len(nonnull)
            if nonnull.nunique()>=100 and ur>=.20:
                issues.append(Issue("LOW","Modeling","High-cardinality categorical feature",col,
                    f"{nonnull.nunique():,} unique values ({ur:.2%} unique).",
                    "Check whether this is an identifier; avoid naive one-hot encoding.",2))

            if 2<=nonnull.nunique()<=100:
                vc=nonnull.value_counts(normalize=True)
                rare=vc[vc<.005]
                if len(rare)>=2:
                    issues.append(Issue("LOW","Distribution","Rare categories",col,
                        f"{len(rare)} categories each occur in <0.5%; combined share={rare.sum():.2%}.",
                        "Check stability across splits; merge only when business meaning supports it.",1))
    return issues
