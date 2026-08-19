import pandas as pd
from sklearn.metrics import normalized_mutual_info_score
from .models import Issue

FUTURE_TOKENS=(
    "after","post","future","final","resolved","resolution","outcome","result",
    "approved","rejected","closed","settled","status_after","next_","later","actual_"
)

def infer_target_kind(y):
    z=y.dropna()
    if len(z)==0: return "unknown"
    u=z.nunique()
    if pd.api.types.is_bool_dtype(z) or pd.api.types.is_object_dtype(z) or u<=max(20,int(len(z)*.02)):
        return "classification"
    if pd.api.types.is_numeric_dtype(z): return "regression"
    return "classification"

def run_leakage_checks(df,target):
    if not target or target not in df.columns:
        return [],{}
    issues=[]; y=df[target]; kind=infer_target_kind(y)
    summary={"target":target,"kind":kind,"non_missing":int(y.notna().sum()),
             "missing":int(y.isna().sum()),"unique":int(y.nunique(dropna=True))}
    if kind=="classification":
        vc=y.value_counts(normalize=True,dropna=True)
        summary["class_distribution"]=vc.head(20).to_dict()
        if len(vc)>=2:
            m=float(vc.min())
            if m<.02:
                issues.append(Issue("HIGH","Target","Extreme class imbalance",target,
                    f"Smallest class share={m:.2%}.",
                    "Use stratified/group-aware evaluation and class-sensitive metrics; avoid accuracy alone.",6))
            elif m<.10:
                issues.append(Issue("MEDIUM","Target","Class imbalance",target,
                    f"Smallest class share={m:.2%}.",
                    "Use stratification and metrics appropriate for imbalanced classification.",3))

    for col in df.columns:
        if col==target: continue
        s=df[col]; low=str(col).lower()
        if any(t in low for t in FUTURE_TOKENS):
            issues.append(Issue("HIGH","Leakage","Feature name suggests post-outcome information",col,
                f"Suspicious timing token in column name: {col}",
                "Confirm whether the feature exists at prediction time; exclude it if created after the target event.",7))

        valid=y.notna() & s.notna()
        if valid.sum()>=20:
            eq=(y[valid].astype(str).str.strip().str.lower().to_numpy()
                ==s[valid].astype(str).str.strip().str.lower().to_numpy()).mean()
            if eq>=.995:
                issues.append(Issue("CRITICAL","Leakage","Feature appears to copy the target",col,
                    f"{eq:.2%} of overlapping values match the target exactly.",
                    "Remove this feature and trace how it was produced.",20))
                continue

        if pd.api.types.is_numeric_dtype(y) and pd.api.types.is_numeric_dtype(s):
            pair=pd.concat([pd.to_numeric(y,errors="coerce"),pd.to_numeric(s,errors="coerce")],axis=1).dropna()
            if len(pair)>=30 and pair.iloc[:,0].nunique()>2 and pair.iloc[:,1].nunique()>2:
                corr=pair.iloc[:,0].corr(pair.iloc[:,1])
                if pd.notna(corr):
                    ac=abs(float(corr))
                    if ac>=.995:
                        issues.append(Issue("CRITICAL","Leakage","Near-perfect numeric relationship with target",col,
                            f"|Pearson correlation|={ac:.4f}.",
                            "Verify whether the feature is derived from target or unavailable at prediction time.",16))
                    elif ac>=.98:
                        issues.append(Issue("HIGH","Leakage","Suspiciously strong numeric relationship with target",col,
                            f"|Pearson correlation|={ac:.4f}.",
                            "Investigate provenance and prediction-time availability.",8))

        if kind=="classification":
            sub=pd.DataFrame({"x":s,"y":y}).dropna()
            if len(sub)>=100 and 2<=sub["x"].nunique()<=200:
                nmi=float(normalized_mutual_info_score(sub["y"].astype(str),sub["x"].astype(str)))
                if nmi>=.98:
                    issues.append(Issue("CRITICAL","Leakage","Categorical feature almost determines the target",col,
                        f"Normalized mutual information={nmi:.3f}.",
                        "Check whether this is an encoded outcome, downstream status, or target proxy.",15))
                elif nmi>=.90:
                    issues.append(Issue("HIGH","Leakage","Categorical feature strongly predicts target by itself",col,
                        f"Normalized mutual information={nmi:.3f}.",
                        "Investigate feature timing and provenance before modeling.",7))
    return issues,summary
