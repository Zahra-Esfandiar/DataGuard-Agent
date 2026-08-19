from .roles import infer_roles
from .quality import run_quality_checks
from .leakage import run_leakage_checks
from .split import recommend_split
from .models import AuditResult

def run_audit(df,target=None,entity_id=None,datetime_col=None):
    roles=infer_roles(df)
    ids=[]
    if entity_id: ids.append(entity_id)
    for c in roles.get("id_candidates",[])[:3]:
        if c not in ids: ids.append(c)

    issues=run_quality_checks(df,ids)
    leakage,target_summary=run_leakage_checks(df,target)
    issues.extend(leakage)
    split_plan=recommend_split(df,target,entity_id,datetime_col)

    rank={"CRITICAL":0,"HIGH":1,"MEDIUM":2,"LOW":3,"INFO":4}
    issues.sort(key=lambda x:(rank.get(x.severity,9),-x.penalty,x.column,x.title))
    return AuditResult(
        rows=len(df),columns=df.shape[1],issues=issues,roles=roles,
        split_plan=split_plan,target_summary=target_summary,
        metadata={"target":target,"entity_id":entity_id,"datetime_col":datetime_col}
    )
