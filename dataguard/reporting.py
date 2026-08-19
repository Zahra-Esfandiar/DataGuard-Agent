import html
from datetime import datetime
import pandas as pd

def issues_dataframe(audit):
    cols=["severity","dimension","column","title","evidence","recommendation","penalty"]
    rows=audit.get("issues",[])
    if not rows: return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows)[cols]

def markdown_report(audit,ai_summary=None):
    lines=[
        "# DataGuard Agent — Data Readiness Report","",
        f"- **Generated:** {datetime.now().isoformat(timespec='seconds')}",
        f"- **Rows:** {audit['rows']:,}",
        f"- **Columns:** {audit['columns']:,}",
        f"- **Readiness score:** {audit['readiness_score']}/100",
        f"- **Status:** {audit['readiness_label']}","",
        "## Split recommendation","",
        f"**{audit['split_plan'].get('recommended_strategy','')}**","",
        audit["split_plan"].get("priority_reason",""),"",
        f"`{audit['split_plan'].get('implementation','')}`","",
        "## Issues",""
    ]
    if not audit.get("issues"):
        lines.append("No issues were detected by the current rule set.")
    else:
        for idx,i in enumerate(audit["issues"],1):
            col=f" — `{i['column']}`" if i.get("column") else ""
            lines += [
                f"### {idx}. [{i['severity']}] {i['title']}{col}","",
                f"**Dimension:** {i['dimension']}","",
                f"**Evidence:** {i['evidence']}","",
                f"**Recommendation:** {i['recommendation']}",""
            ]
    if ai_summary:
        lines += ["## AI reviewer summary","",ai_summary,""]
    lines += [
        "## Important note","",
        "This report is a screening tool. Potential leakage, outliers, missingness, and drift require domain validation before data is changed or excluded."
    ]
    return "\n".join(lines)

def html_report(audit,ai_summary=None):
    escaped=html.escape(markdown_report(audit,ai_summary))
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>DataGuard Report</title>
<style>body{{font-family:Arial,sans-serif;max-width:1100px;margin:40px auto;padding:0 24px;line-height:1.55}}
pre{{white-space:pre-wrap;font-family:Arial,sans-serif}}</style></head>
<body><pre>{escaped}</pre></body></html>"""
