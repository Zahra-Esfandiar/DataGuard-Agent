import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import ks_2samp
from .models import Issue

def _probs(a,b):
    cats=sorted(set(a.dropna().astype(str).unique())|set(b.dropna().astype(str).unique()))
    if not cats: return np.array([]),np.array([])
    pa=a.dropna().astype(str).value_counts(normalize=True).reindex(cats,fill_value=0).to_numpy()+1e-12
    pb=b.dropna().astype(str).value_counts(normalize=True).reindex(cats,fill_value=0).to_numpy()+1e-12
    return pa,pb

def run_drift_checks(reference,current):
    issues=[]
    rc,cc=set(reference.columns),set(current.columns)
    missing=sorted(rc-cc); added=sorted(cc-rc)
    if missing:
        issues.append(Issue("CRITICAL","Schema Drift","Columns missing from current data",
            evidence=f"Missing columns: {missing}",
            recommendation="Restore expected schema or explicitly version the downstream pipeline.",penalty=18))
    if added:
        issues.append(Issue("MEDIUM","Schema Drift","New columns in current data",
            evidence=f"New columns: {added}",
            recommendation="Review whether downstream transformations and governance rules should include them.",penalty=3))

    for col in sorted(rc&cc):
        r,c=reference[col],current[col]
        rnum,cnum=pd.api.types.is_numeric_dtype(r),pd.api.types.is_numeric_dtype(c)
        rdt,cdt=pd.api.types.is_datetime64_any_dtype(r),pd.api.types.is_datetime64_any_dtype(c)
        if rnum!=cnum or rdt!=cdt:
            issues.append(Issue("HIGH","Schema Drift","Data type changed",col,
                f"Reference dtype={r.dtype}; current dtype={c.dtype}.",
                "Align parsing/casting before comparison or model scoring.",6))
            continue

        rm,cm=float(r.isna().mean()),float(c.isna().mean()); delta=cm-rm
        if delta>=.10:
            sev="HIGH" if delta>=.25 else "MEDIUM"
            issues.append(Issue(sev,"Completeness Drift","Missingness increased",col,
                f"Reference={rm:.2%}; current={cm:.2%}; change={delta:+.2%}.",
                "Investigate source-system or transformation changes.",6 if sev=="HIGH" else 3))

        if rnum and cnum:
            rr=pd.to_numeric(r,errors="coerce").replace([np.inf,-np.inf],np.nan).dropna()
            cc2=pd.to_numeric(c,errors="coerce").replace([np.inf,-np.inf],np.nan).dropna()
            if len(rr)>=50 and len(cc2)>=50:
                rr=rr.sample(min(len(rr),20000),random_state=42) if len(rr)>20000 else rr
                cc2=cc2.sample(min(len(cc2),20000),random_state=42) if len(cc2)>20000 else cc2
                stat,p=ks_2samp(rr,cc2)
                if stat>=.20:
                    sev="HIGH" if stat>=.35 else "MEDIUM"
                    issues.append(Issue(sev,"Distribution Drift","Numeric distribution shifted",col,
                        f"KS statistic={stat:.3f}, p-value={p:.3g}.",
                        "Compare quantiles and segments; retrain only after confirming persistent relevant drift.",
                        6 if sev=="HIGH" else 3))
        else:
            rr,cc2=r.dropna().astype(str),c.dropna().astype(str)
            if 2<=rr.nunique()<=200 and 2<=cc2.nunique()<=200:
                p,q=_probs(rr,cc2)
                if len(p):
                    js=float(jensenshannon(p,q,base=2.0))
                    unseen=set(cc2.unique())-set(rr.unique())
                    ur=float(cc2.isin(unseen).mean()) if unseen else 0.0
                    if js>=.25 or ur>=.05:
                        sev="HIGH" if js>=.40 or ur>=.20 else "MEDIUM"
                        issues.append(Issue(sev,"Distribution Drift","Categorical distribution shifted",col,
                            f"Jensen-Shannon distance={js:.3f}; unseen-category share={ur:.2%}.",
                            "Inspect new/changed categories and confirm encoders/business rules can handle them.",
                            6 if sev=="HIGH" else 3))
    return issues
