from dataclasses import dataclass, asdict, field
from typing import Any

@dataclass
class Issue:
    severity: str
    dimension: str
    title: str
    column: str = ""
    evidence: str = ""
    recommendation: str = ""
    penalty: float = 0.0
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class AuditResult:
    rows: int
    columns: int
    issues: list[Issue] = field(default_factory=list)
    roles: dict[str, Any] = field(default_factory=dict)
    split_plan: dict[str, Any] = field(default_factory=dict)
    target_summary: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def readiness_score(self) -> int:
        penalty = sum(max(0.0, x.penalty) for x in self.issues)
        return int(max(0, round(100 - min(100, penalty))))

    @property
    def readiness_label(self) -> str:
        s = self.readiness_score
        if s >= 85: return "READY"
        if s >= 70: return "NEEDS MINOR FIXES"
        if s >= 50: return "NEEDS WORK"
        return "NOT READY"

    def to_dict(self):
        return {
            "rows": self.rows,
            "columns": self.columns,
            "readiness_score": self.readiness_score,
            "readiness_label": self.readiness_label,
            "issues": [x.to_dict() for x in self.issues],
            "roles": self.roles,
            "split_plan": self.split_plan,
            "target_summary": self.target_summary,
            "metadata": self.metadata,
        }
