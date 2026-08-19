import json, os
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from dataguard.audit import run_audit
from dataguard.cleaning import build_validation_spec, generate_cleaning_script
from dataguard.drift import run_drift_checks
from dataguard.gemini_advisor import GeminiAdvisor
from dataguard.io import read_uploaded_file
from dataguard.reporting import html_report, issues_dataframe, markdown_report
from dataguard.roles import infer_roles

load_dotenv()
st.set_page_config(page_title="DataGuard Agent", page_icon="🛡️", layout="wide")
SEV_ORDER=["CRITICAL","HIGH","MEDIUM","LOW","INFO"]

st.title("🛡️ DataGuard Agent")
st.caption(
    "Upload your real dataset → detect quality problems, leakage risk, split mistakes, "
    "and optional production drift → export a Data Readiness Report."
)

with st.sidebar:
    st.header("Audit mode")
    mode=st.radio("Choose mode",["Single dataset audit","Reference vs current drift"])
    st.header("Optional AI reviewer")
    use_ai=st.toggle(
        "Use Gemini to explain/prioritize findings",
        value=False,
        help="The deterministic audit works without any API. Gemini receives the audit summary, not the raw dataframe."
    )
    api_key=""
    model=os.getenv("GEMINI_MODEL","gemini-3.7-flash")
    if use_ai:
        api_key=st.text_input("Gemini API key",value=os.getenv("GEMINI_API_KEY",""),type="password")
        model=st.selectbox("Model",["gemini-3.7-flash","gemini-3.6-flash","gemini-3.5-flash-lite"])
    st.divider()
    st.caption("Supported: CSV, Excel, Parquet. DataGuard never auto-deletes outliers or auto-imputes missing values.")

def severity_counts(issue_df):
    if issue_df.empty: return {s:0 for s in SEV_ORDER}
    vc=issue_df["severity"].value_counts().to_dict()
    return {s:int(vc.get(s,0)) for s in SEV_ORDER}

def show_issues(issue_df):
    if issue_df.empty:
        st.success("No issues detected by the current rule set.")
    else:
        st.dataframe(
            issue_df[["severity","dimension","column","title","evidence","recommendation"]],
            use_container_width=True,hide_index=True
        )

if mode=="Single dataset audit":
    uploaded=st.file_uploader("Upload your real dataset",type=["csv","xlsx","xls","parquet"],key="single")
    if uploaded is None:
        st.info("Upload a real dataset to start. No synthetic/demo dataset is required.")
        st.stop()

    signature=(uploaded.name,uploaded.size)
    if st.session_state.get("single_signature")!=signature:
        for key in ["audit","ai_summary"]:
            st.session_state.pop(key,None)
        st.session_state["single_signature"]=signature

    try:
        df=read_uploaded_file(uploaded)
    except Exception as exc:
        st.error(f"Could not read file: {exc}")
        st.stop()

    roles=infer_roles(df)

    st.subheader("Modeling context (optional)")
    a,b,c=st.columns(3)

    target_opts=["— None —"]+list(df.columns)
    sugg=roles.get("possible_targets",[])
    target_idx=target_opts.index(sugg[0]) if sugg and sugg[0] in target_opts else 0
    target_ui=a.selectbox("Target",target_opts,index=target_idx)
    target=None if target_ui=="— None —" else target_ui

    id_opts=["— None —"]+list(df.columns)
    sugg_ids=roles.get("id_candidates",[])
    id_idx=id_opts.index(sugg_ids[0]) if sugg_ids and sugg_ids[0] in id_opts else 0
    entity_ui=b.selectbox("Entity / Customer / Patient ID",id_opts,index=id_idx)
    entity_id=None if entity_ui=="— None —" else entity_ui

    dt_opts=["— None —"]+list(df.columns)
    sugg_dt=roles.get("datetime_candidates",[])
    dt_idx=dt_opts.index(sugg_dt[0]) if sugg_dt and sugg_dt[0] in dt_opts else 0
    dt_ui=c.selectbox("Time column",dt_opts,index=dt_idx)
    datetime_col=None if dt_ui=="— None —" else dt_ui

    st.write(f"Loaded **{len(df):,} rows × {df.shape[1]:,} columns**.")
    with st.expander("Preview",expanded=False):
        st.dataframe(df.head(30),use_container_width=True)

    if st.button("🚀 Run DataGuard Audit",type="primary",use_container_width=True):
        with st.spinner("Scanning quality, leakage risk, and split strategy..."):
            result=run_audit(df,target=target,entity_id=entity_id,datetime_col=datetime_col)
            st.session_state["audit"]=result.to_dict()
            st.session_state["ai_summary"]=None

    audit=st.session_state.get("audit")
    if audit is None:
        st.stop()

    issue_df=issues_dataframe(audit)
    counts=severity_counts(issue_df)

    st.divider()
    m1,m2,m3,m4,m5=st.columns(5)
    m1.metric("Readiness",f"{audit['readiness_score']}/100")
    m2.metric("Critical",counts["CRITICAL"])
    m3.metric("High",counts["HIGH"])
    m4.metric("Medium",counts["MEDIUM"])
    m5.metric("Issues",len(issue_df))

    if audit["readiness_score"]>=85:
        st.success(f"ML Readiness: {audit['readiness_label']}")
    elif audit["readiness_score"]>=70:
        st.warning(f"ML Readiness: {audit['readiness_label']}")
    else:
        st.error(f"ML Readiness: {audit['readiness_label']}")

    t1,t2,t3,t4,t5,t6=st.tabs(["🚨 Issues","🎯 Leakage & Target","✂️ Split Plan","📊 EDA","🤖 AI Reviewer","⬇️ Export"])

    with t1:
        filters=st.multiselect("Severity",SEV_ORDER,default=["CRITICAL","HIGH","MEDIUM","LOW"])
        view=issue_df[issue_df["severity"].isin(filters)] if not issue_df.empty else issue_df
        show_issues(view)
        if not issue_df.empty:
            temp=issue_df.groupby(["severity","dimension"],as_index=False).size()
            fig=px.bar(temp,x="dimension",y="size",color="severity",
                       category_orders={"severity":SEV_ORDER},title="Issues by data-quality dimension")
            st.plotly_chart(fig,use_container_width=True)

    with t2:
        if target:
            st.markdown("#### Target summary")
            st.json(audit.get("target_summary",{}))
            leakage=issue_df[issue_df["dimension"]=="Leakage"] if not issue_df.empty else issue_df
            st.markdown("#### Potential leakage warnings")
            show_issues(leakage)
            st.caption("Leakage flags are screening signals. Confirm feature timing and provenance before excluding a feature.")
        else:
            st.info("Select a target above and rerun the audit to enable target/leakage checks.")

    with t3:
        plan=audit["split_plan"]
        st.markdown(f"### {plan['recommended_strategy']}")
        st.write(plan["priority_reason"])
        st.code(plan["implementation"])
        for warning in plan.get("warnings",[]):
            st.warning(warning)

    with t4:
        st.markdown("#### Quick EDA")
        num_cols=list(df.select_dtypes(include="number").columns)
        if num_cols:
            chosen=st.selectbox("Numeric distribution",num_cols)
            sample=df[[chosen]].dropna()
            if len(sample)>50000:
                sample=sample.sample(50000,random_state=42)
            st.plotly_chart(px.histogram(sample,x=chosen,nbins=50),use_container_width=True)
            if len(num_cols)>=2:
                corr=df[num_cols].corr(numeric_only=True)
                st.plotly_chart(px.imshow(corr,aspect="auto",title="Numeric correlation matrix"),
                                use_container_width=True)
        cat_cols=[x for x in df.columns if (df[x].dtype=="object" or str(df[x].dtype).startswith("category"))
                  and 2<=df[x].nunique(dropna=True)<=50]
        if cat_cols:
            chosen_cat=st.selectbox("Categorical distribution",cat_cols)
            vc=df[chosen_cat].fillna("<MISSING>").astype(str).value_counts().head(30).reset_index()
            vc.columns=[chosen_cat,"count"]
            st.plotly_chart(px.bar(vc,x=chosen_cat,y="count"),use_container_width=True)

    with t5:
        if not use_ai:
            st.info("Gemini is optional. Enable it in the sidebar only if you want explanation/prioritization. The audit itself is deterministic.")
        elif not api_key:
            st.warning("Enter a Gemini API key in the sidebar.")
        else:
            if st.button("Ask Gemini to prioritize the audit"):
                with st.spinner("Reviewing the deterministic audit summary..."):
                    try:
                        advisor=GeminiAdvisor(api_key,model)
                        st.session_state["ai_summary"]=advisor.review_audit(audit)
                    except Exception as exc:
                        st.error(f"Gemini request failed: {exc}")
            if st.session_state.get("ai_summary"):
                st.markdown(st.session_state["ai_summary"])

            question=st.text_input("Ask about the audit",placeholder="Which three issues should I fix before training?")
            if st.button("Ask reviewer",disabled=not bool(question)):
                try:
                    advisor=GeminiAdvisor(api_key,model)
                    st.markdown(advisor.answer_question(audit,question))
                except Exception as exc:
                    st.error(f"Gemini request failed: {exc}")
            st.caption("Gemini receives the audit JSON, not the raw dataset.")

    with t6:
        ai_summary=st.session_state.get("ai_summary")
        md=markdown_report(audit,ai_summary)
        html=html_report(audit,ai_summary)
        cleaning=generate_cleaning_script(df,audit)
        spec=json.dumps(build_validation_spec(audit),indent=2,ensure_ascii=False)

        x1,x2,x3=st.columns(3)
        x1.download_button("Markdown report",md,file_name="dataguard_report.md")
        x2.download_button("HTML report",html,file_name="dataguard_report.html")
        x3.download_button("Issues CSV",issue_df.to_csv(index=False).encode("utf-8"),file_name="dataguard_issues.csv")
        x4,x5=st.columns(2)
        x4.download_button("Cleaning starter",cleaning,file_name="dataguard_cleaning.py")
        x5.download_button("Validation spec",spec,file_name="dataguard_validation_spec.json")
        st.code(cleaning,language="python")

else:
    st.subheader("Reference vs current / production data")
    a,b=st.columns(2)
    ref_file=a.file_uploader("Reference / training dataset",type=["csv","xlsx","xls","parquet"],key="ref")
    cur_file=b.file_uploader("Current / production dataset",type=["csv","xlsx","xls","parquet"],key="cur")
    if not ref_file or not cur_file:
        st.info("Upload both datasets to scan schema, missingness, and distribution drift.")
        st.stop()

    try:
        reference=read_uploaded_file(ref_file)
        current=read_uploaded_file(cur_file)
    except Exception as exc:
        st.error(f"Could not read files: {exc}")
        st.stop()

    drift_sig=(ref_file.name,ref_file.size,cur_file.name,cur_file.size)
    if st.session_state.get("drift_signature")!=drift_sig:
        st.session_state.pop("drift_audit",None)
        st.session_state.pop("drift_ai",None)
        st.session_state["drift_signature"]=drift_sig

    if st.button("🔄 Run Drift Audit",type="primary",use_container_width=True):
        with st.spinner("Comparing schemas and distributions..."):
            items=run_drift_checks(reference,current)
            score=max(0,int(100-min(100,sum(i.penalty for i in items))))
            st.session_state["drift_audit"]={
                "rows":len(current),"columns":current.shape[1],
                "readiness_score":score,"readiness_label":"DRIFT REVIEW",
                "issues":[i.to_dict() for i in items],
                "roles":{},"target_summary":{},
                "split_plan":{
                    "recommended_strategy":"Production drift review",
                    "priority_reason":"Compare current data with the selected reference dataset.",
                    "implementation":"Investigate high-severity schema/distribution changes before scoring or retraining.",
                    "warnings":[]
                },
                "metadata":{"reference_rows":len(reference),"current_rows":len(current)}
            }

    drift=st.session_state.get("drift_audit")
    if drift:
        issue_df=issues_dataframe(drift); counts=severity_counts(issue_df)
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Drift score",f"{drift['readiness_score']}/100")
        m2.metric("Critical",counts["CRITICAL"]); m3.metric("High",counts["HIGH"]); m4.metric("Medium",counts["MEDIUM"])
        show_issues(issue_df)

        if use_ai and api_key:
            if st.button("Ask Gemini to summarize drift"):
                try:
                    st.session_state["drift_ai"]=GeminiAdvisor(api_key,model).review_audit(drift)
                except Exception as exc:
                    st.error(f"Gemini request failed: {exc}")
            if st.session_state.get("drift_ai"):
                st.markdown(st.session_state["drift_ai"])

        report=markdown_report(drift,st.session_state.get("drift_ai"))
        st.download_button("Download drift report",report,file_name="dataguard_drift_report.md")
