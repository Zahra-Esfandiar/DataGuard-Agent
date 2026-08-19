import pandas as pd
from .leakage import infer_target_kind

def recommend_split(df,target=None,entity_id=None,datetime_col=None):
    plan={"recommended_strategy":"Random holdout / K-fold",
          "priority_reason":"No strong temporal or grouped structure was selected.",
          "implementation":"train_test_split(..., random_state=42)",
          "warnings":[]}
    kind=infer_target_kind(df[target]) if target and target in df.columns else None
    repeated=False
    if entity_id and entity_id in df.columns:
        s=df[entity_id].dropna(); repeated=s.nunique()<len(s)
    usable_time=False
    if datetime_col and datetime_col in df.columns:
        p=pd.to_datetime(df[datetime_col],errors="coerce")
        usable_time=p.notna().mean()>=.80 and p.nunique()>=20

    if usable_time:
        plan.update(
            recommended_strategy="Time-based split",
            priority_reason=f"`{datetime_col}` provides usable temporal ordering. Random splitting can leak future information.",
            implementation=f"Sort by `{datetime_col}`; train on earlier observations and validate/test on later periods. Consider TimeSeriesSplit."
        )
        if repeated:
            plan["warnings"].append(f"`{entity_id}` repeats. Check whether entities crossing time boundaries match deployment.")
    elif repeated:
        plan.update(
            recommended_strategy="Group-aware split",
            priority_reason=f"`{entity_id}` repeats across rows; random row splitting could put the same entity in train and test.",
            implementation=(f"Use StratifiedGroupKFold with groups=`{entity_id}` when feasible."
                            if kind=="classification"
                            else f"Use GroupKFold or GroupShuffleSplit with groups=`{entity_id}`.")
        )
    elif kind=="classification":
        vc=df[target].value_counts(normalize=True,dropna=True)
        if len(vc)>=2 and float(vc.min())<.20:
            plan.update(
                recommended_strategy="Stratified split",
                priority_reason="The target is categorical and imbalanced.",
                implementation="Use train_test_split(..., stratify=y) or StratifiedKFold."
            )
    if target is None:
        plan["warnings"].append("No target selected; modeling-specific split advice is limited.")
    return plan
