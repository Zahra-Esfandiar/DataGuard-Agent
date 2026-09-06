<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1E1B4B,45:4338CA,75:2563EB,100:0F766E&height=220&section=header&text=DataGuard-Agent&fontSize=65&fontColor=ffffff&animation=fadeIn" />

# 🛡️ DataGuard-Agent

### AI-Assisted Data Quality • Leakage Detection • ML Readiness • Production Drift Monitoring

**A trustworthy AI framework for preparing real-world datasets before machine learning deployment.**

</div>

---

## 🎯 Why DataGuard-Agent?

Modern machine learning systems often fail not because of the model, but because of hidden problems in data:

- Poor data quality
- Target leakage
- Invalid evaluation strategies
- Distribution shifts after deployment

DataGuard-Agent provides an evidence-based audit layer before modeling.

> Detect deterministically. Explain with AI. Never let the LLM invent the audit.

---

## 🔄 Intelligent Data Audit Workflow

```
Dataset
   ↓
Quality Assessment
   ↓
Leakage & Feature Risk Detection
   ↓
Train/Test Split Recommendation
   ↓
Reference vs Production Drift Analysis
   ↓
AI-Assisted Explanation & Reporting
```

---

## 🔍 Core Capabilities

### 📊 Data Quality Intelligence

Detects:

- Missing values
- Duplicate records
- Constant features
- Invalid data types
- Inconsistent labels
- Rare and high-cardinality categories
- Extreme values and suspicious patterns

### 🎯 Target Leakage Analysis

Identifies potential risks including:

- Target copies
- Future information leakage
- Suspicious feature relationships
- Post-outcome variables

### 🔀 ML Split Strategy Advisor

Recommends appropriate validation strategies:

- Time-based split
- Group-aware split
- Stratified split

### 📈 Production Drift Monitoring

Compares reference and current datasets using:

- Missingness changes
- Schema changes
- KS statistics
- Jensen-Shannon distance
- New/unseen categories

---

## 🤖 AI Assistant Layer

Gemini integration is optional.

The model receives only compact audit evidence and helps with:

- Prioritizing issues
- Explaining modeling impact
- Suggesting next steps

The core auditing engine remains deterministic and reproducible.

---

## 📦 Outputs

DataGuard generates:

✅ Data Readiness Score  
✅ Evidence-based issue reports  
✅ Leakage warnings  
✅ Drift reports  
✅ HTML/Markdown summaries  
✅ Validation specification JSON  
✅ Conservative cleaning suggestions  

---

## 🏗️ Architecture

```
Input Data
   |
   ├── Quality Engine
   ├── Leakage Engine
   ├── Drift Engine
   ├── Split Strategy Engine
   |
   ↓
Audit Report
   |
   ↓
AI Reviewer
```

---

## 🛠️ Technology Stack

`Python` `Streamlit` `Pandas` `Scikit-learn` `Statistical Testing` `LLM APIs`

---

## 🚀 Research & Engineering Vision

DataGuard-Agent explores the intersection of:

📐 Statistical Reliability  →  🤖 Artificial Intelligence  →  🏭 Production ML Systems

The goal is to make machine learning workflows more trustworthy, explainable, and reproducible.

---

## 👤 Author

**Zahra Esfandiar**  
Statistics & Data Science Researcher  

Interests: Statistical Machine Learning • Healthcare AI • Trustworthy AI • Data-Centric ML
