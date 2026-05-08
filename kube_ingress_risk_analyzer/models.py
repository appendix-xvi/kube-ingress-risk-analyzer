"""Data models for ingress analysis."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity levels for risk findings."""

    low = "low"
    medium = "medium"
    high = "high"


class IngressRoute(BaseModel):
    """Normalized route entry extracted from a Kubernetes Ingress resource."""

    namespace: str
    ingress_name: str
    ingress_class: str | None = None
    host: str
    path: str = "/"
    backend_service: str | None = None
    rule_priority: int | None = None


class RiskFinding(BaseModel):
    """A risk finding produced by analyzer."""

    risk_type: str
    severity: Severity
    message: str
    host: str | None = None
    namespaces: list[str] = Field(default_factory=list)
    ingresses: list[str] = Field(default_factory=list)
    paths: list[str] = Field(default_factory=list)


class AnalysisReport(BaseModel):
    """Full analysis report."""

    total_routes: int
    total_findings: int
    findings_by_severity: dict[str, int]
    findings: list[RiskFinding]
