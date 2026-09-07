<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0F172A,45:1D4ED8,75:0F766E,100:059669&height=240&section=header&text=DataGuard-Agent&fontSize=70&fontColor=ffffff&animation=fadeIn" />

# 🛡️ DataGuard-Agent

### Trustworthy AI • Data-Centric ML • Automated Data Readiness Assessment

**An AI-assisted framework for auditing, validating, and preparing real-world datasets before machine learning deployment.**

</div>

---

## 🌍 Research Vision

Machine learning failures often originate before model training begins. DataGuard-Agent focuses on the **data intelligence layer** of ML systems:

📊 Data Quality → 🔍 Leakage Prevention → 📈 Drift Monitoring → 🤖 Explainable AI Assistance

The goal is to build reliable and reproducible ML pipelines where decisions are supported by statistical evidence.

---

## ⚡ Quick Start

```bash
git clone https://github.com/Zahra-Esfandiar/DataGuard-Agent.git
cd DataGuard-Agent
python -m venv .venv
```

Activate the virtual environment for your operating system, then install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app.py
```

Optional AI-assisted explanations can be configured through the environment settings documented in `.env.example`. The deterministic audit pipeline remains usable independently of an LLM provider.

---

## 🔄 End-to-End Audit Workflow

```text
Raw Dataset
    ↓
Data Quality Profiling
    ↓
Feature & Target Leakage Analysis
    ↓
Validation Strategy Recommendation
    ↓
Reference vs Production Drift Detection
    ↓
AI-Assisted Explanation & Reporting
```

---

## 🔍 Core Modules

### 📊 Data Quality Intelligence

- Missingness analysis
- Duplicate detection
- Schema validation
- Data type consistency checks
- Category and feature risk assessment
- Suspicious pattern detection

### 🎯 Leakage Detection Engine

Identifies:

- Target duplication
- Future information leakage
- Post-outcome variables
- Suspicious predictive relationships

### 🔀 Validation Strategy Advisor

Supports recommendations for:

- Time-aware validation
- Group-aware splitting
- Stratified evaluation

### 📈 Production Drift Monitoring

Tracks:

- Distribution changes
- Missingness shifts
- New categories
- Statistical distance measures

---

## 🤖 AI Reviewer Layer

The AI layer does not replace statistical auditing.

Instead:

**Deterministic Engine → Evidence → AI Explanation**

The assistant summarizes findings, prioritizes risks, and suggests next steps while keeping the underlying analysis reproducible.

---

## 🏗️ Architecture

```text
                Dataset
                   |
        +----------+----------+
        |          |          |
 Quality Engine  Leakage   Drift Engine
        |          |          |
        +----------+----------+
                   |
            Audit Report
                   |
            AI Explanation
```

Project implementation includes the Streamlit application, the `dataguard/` package, documentation, a smoke test, and reproducible dependency specification.

---

## 📦 Outputs

✅ Data Readiness Score  
✅ Evidence-based audit report  
✅ Leakage warnings  
✅ Drift analysis report  
✅ Validation recommendations  
✅ Machine-readable summaries

---

## 🛠️ Technology Stack

`Python` `Streamlit` `Pandas` `Scikit-learn` `Statistical Testing` `LLM APIs`

---

## 🚀 Applications

Designed for:

- Healthcare ML pipelines
- Financial analytics
- Enterprise AI systems
- Research reproducibility workflows

---

## 📚 Documentation

- [`README_FA.md`](README_FA.md) — Persian overview
- [`docs/`](docs/) — architecture and supporting documentation
- [`.env.example`](.env.example) — optional environment configuration

---

## 👤 Author

**Zahra Esfandiar**  
Statistics & Data Science Researcher

Research interests: Statistical Machine Learning • Biostatistics • Trustworthy AI • Data-Centric ML
