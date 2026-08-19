# 🛡️ DataGuard Agent

**AI-assisted Data Quality, Target Leakage, ML Readiness & Production Drift Auditor for real datasets.**

This is not a "chat with a synthetic CSV" demo.

You upload your **real CSV, Excel, or Parquet file**. DataGuard first runs deterministic checks and creates evidence. Gemini is optional and only explains/prioritizes the findings.

## What it detects

### Data quality
- missing values
- exact duplicate rows
- candidate-ID uniqueness problems
- constant columns
- infinite numeric values
- numeric values stored as text
- partially invalid date/time fields
- whitespace and inconsistent labels
- rare categories
- high-cardinality categoricals
- robust extreme-value screening
- heavy skewness
- suspicious negative values in likely non-negative fields

### Target & leakage risk
If you select a target:
- target type and class imbalance
- exact target copies
- suspicious post-outcome/future feature names
- near-perfect numeric relationships with the target
- near-deterministic categorical target proxies

Leakage flags are screening signals. Feature timing and provenance still need human validation.

### Split strategy
DataGuard recommends:
- **time-based split** for temporal data
- **group-aware split** when customer/patient/entity IDs repeat
- **stratified split** for imbalanced classification
- standard random splitting only when stronger structure is absent

### Reference vs current drift
Upload reference/training data and current/production data to detect:
- missing or new columns
- dtype changes
- increased missingness
- numeric distribution drift with KS statistic
- categorical drift with Jensen-Shannon distance
- unseen categories

## Outputs

- Data Readiness Score
- prioritized issue table with severity/evidence/recommendation
- leakage warnings
- split recommendation
- quick EDA
- Markdown report
- HTML report
- issues CSV
- conservative cleaning starter script
- validation-spec JSON
- production drift report

## Gemini is optional

The core audit works without any API key.

If Gemini is enabled, it receives the **compact audit JSON, not the raw dataframe**, and acts as a reviewer:
- prioritizes fixes
- explains modeling impact
- answers questions about the audit
- separates evidence from heuristic warnings

Default model: `gemini-3.7-flash`.

## Windows: easiest setup

1. Extract the project ZIP.
2. Double-click `install_windows.bat`.
3. Double-click `run_windows.bat`.
4. Upload your own dataset.
5. Optionally choose Target, Entity ID, and Time column.
6. Click **Run DataGuard Audit**.

## Manual setup

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

macOS/Linux:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Project structure

```text
DataGuard-Agent/
├── app.py
├── requirements.txt
├── install_windows.bat
├── run_windows.bat
├── .env.example
├── .gitignore
├── .streamlit/
│   └── config.toml
├── dataguard/
│   ├── audit.py
│   ├── cleaning.py
│   ├── drift.py
│   ├── gemini_advisor.py
│   ├── io.py
│   ├── leakage.py
│   ├── models.py
│   ├── quality.py
│   ├── reporting.py
│   ├── roles.py
│   └── split.py
└── outputs/
```

## Design principle

> **Detect deterministically. Explain with AI. Never let the LLM invent the audit.**

## Important limitations

Data quality is domain-specific. DataGuard intentionally does not automatically:
- delete outliers,
- impute missing values,
- drop every strong predictor as leakage,
- mutate your uploaded dataset.

Use it as a screening and decision-support layer before EDA, modeling, or production scoring.

## Author

**Zahra Esfandiar**

Built for the **Data Elites** educational project series.
