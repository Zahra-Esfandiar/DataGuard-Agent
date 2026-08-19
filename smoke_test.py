"""Smoke test for deterministic engines using scikit-learn's real Breast Cancer Wisconsin dataset."""
from sklearn.datasets import load_breast_cancer
import pandas as pd
from dataguard.audit import run_audit

data=load_breast_cancer(as_frame=True)
df=data.frame.copy()
df["patient_id"]=[f"P{i:04d}" for i in range(len(df))]
result=run_audit(df,target="target",entity_id="patient_id")
print(result.readiness_score,result.readiness_label,len(result.issues))
assert result.rows==len(df)
assert result.columns==df.shape[1]
