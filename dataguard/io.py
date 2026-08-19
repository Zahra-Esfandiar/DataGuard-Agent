from pathlib import Path
import pandas as pd

def _postprocess_dates(df):
    df = df.copy()
    for col in df.columns:
        if df[col].dtype != "object":
            continue
        low = str(col).lower()
        if not any(t in low for t in ("date","time","timestamp","datetime")):
            continue
        parsed = pd.to_datetime(df[col], errors="coerce")
        if parsed.notna().mean() >= 0.80:
            df[col] = parsed
    return df

def read_uploaded_file(uploaded):
    name = uploaded.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded, low_memory=False)
    elif name.endswith((".xlsx",".xls")):
        df = pd.read_excel(uploaded)
    elif name.endswith(".parquet"):
        df = pd.read_parquet(uploaded)
    else:
        raise ValueError("Supported formats: CSV, Excel, Parquet.")
    return _postprocess_dates(df)
