import json

def generate_cleaning_script(df,audit):
    lines=[
        "import numpy as np",
        "import pandas as pd",
        "",
        "# Load your real dataset here",
        '# df = pd.read_csv("your_file.csv")',
        "",
        "# Keep a raw copy for auditability",
        "raw_df = df.copy()",
        ""
    ]
    issues=audit.get("issues",[])

    ws=sorted({i["column"] for i in issues if i["title"]=="Leading/trailing whitespace" and i.get("column")})
    if ws:
        lines += [
            "# Safe fix: trim surrounding whitespace",
            f"for col in {ws!r}:",
            "    df[col] = df[col].astype('string').str.strip()",
            ""
        ]

    nums=sorted({i["column"] for i in issues if i["title"]=="Numeric values stored as text" and i.get("column")})
    if nums:
        lines += [
            "# Review separators/units before production use",
            f"for col in {nums!r}:",
            "    cleaned = df[col].astype('string').str.replace(',', '', regex=False)",
            "    df[col] = pd.to_numeric(cleaned, errors='coerce')",
            ""
        ]

    if any(i["title"]=="Duplicate rows detected" for i in issues):
        lines += [
            "# Optional: remove exact duplicates ONLY after confirming they are not valid repeated events",
            "# df = df.drop_duplicates().copy()",
            ""
        ]

    infs=sorted({i["column"] for i in issues if i["title"]=="Infinite numeric values" and i.get("column")})
    if infs:
        lines += [
            "# Represent invalid infinities as missing; still investigate the upstream cause",
            f"for col in {infs!r}:",
            "    df[col] = df[col].replace([np.inf, -np.inf], np.nan)",
            ""
        ]

    leak=sorted({i["column"] for i in issues if i["dimension"]=="Leakage" and i["severity"] in {"CRITICAL","HIGH"} and i.get("column")})
    if leak:
        lines += [
            "# POTENTIAL LEAKAGE: confirm feature timing/provenance before dropping",
            f"potential_leakage = {leak!r}",
            "print('Review potential leakage columns:', potential_leakage)",
            ""
        ]

    lines += [
        "# Missing values and outliers are intentionally NOT auto-imputed/dropped.",
        "# Their treatment depends on the data-generating process and modeling objective.",
        "print('Cleaned shape:', df.shape)"
    ]
    return "\n".join(lines)

def build_validation_spec(audit):
    return {
        "version":1,
        "dataset":{"rows_observed":audit.get("rows"),"columns_observed":audit.get("columns")},
        "recommended_checks":[
            {
                "severity":i["severity"],
                "dimension":i["dimension"],
                "column":i.get("column",""),
                "rule_from_issue":i["title"],
                "recommendation":i["recommendation"]
            } for i in audit.get("issues",[])
        ]
    }
