"""Core analyzer logic for ingress routing risks."""

from __future__ import annotations

from collections import defaultdict

from .models import AnalysisReport, IngressRoute, RiskFinding, Severity


def extract_routes(payload: dict) -> list[IngressRoute]:
    """Extract normalized route entries from kubectl ingress JSON payload."""

    items = payload.get("items", [])
    routes: list[IngressRoute] = []

    for item in items:
        metadata = item.get("metadata", {})
        spec = item.get("spec", {})
        namespace = metadata.get("namespace", "default")
        ingress_name = metadata.get("name", "unknown")
        annotations = metadata.get("annotations", {})

        ingress_class = spec.get("ingressClassName")
        rule_priority_raw = annotations.get("appgw.ingress.kubernetes.io/rule-priority")
        rule_priority = int(rule_priority_raw) if rule_priority_raw and rule_priority_raw.isdigit() else None

        for rule in spec.get("rules", []):
            host = rule.get("host", "*")
            http = rule.get("http", {})
            for path_obj in http.get("paths", []):
                backend = path_obj.get("backend", {}).get("service", {})
                routes.append(
                    IngressRoute(
                        namespace=namespace,
                        ingress_name=ingress_name,
                        ingress_class=ingress_class,
                        host=host,
                        path=path_obj.get("path", "/"),
                        backend_service=backend.get("name"),
                        rule_priority=rule_priority,
                    )
                )

    return routes


def _has_wildcard_conflict(host_a: str, host_b: str) -> bool:
    if host_a.startswith("*.") and host_b != host_a:
        return host_b.endswith(host_a[1:])
    if host_b.startswith("*.") and host_a != host_b:
        return host_a.endswith(host_b[1:])
    return False


def analyze_routes(routes: list[IngressRoute]) -> AnalysisReport:
    """Analyze routes and produce risk findings."""

    findings: list[RiskFinding] = []

    host_to_routes: dict[str, list[IngressRoute]] = defaultdict(list)
    for route in routes:
        host_to_routes[route.host].append(route)

    for host, host_routes in host_to_routes.items():
        namespaces = {r.namespace for r in host_routes}
        if len(namespaces) > 1:
            findings.append(
                RiskFinding(
                    risk_type="duplicate_host_across_namespaces",
                    severity=Severity.high,
                    message=f"Host '{host}' appears in multiple namespaces",
                    host=host,
                    namespaces=sorted(namespaces),
                    ingresses=sorted({r.ingress_name for r in host_routes}),
                )
            )

        missing_priority = [r for r in host_routes if r.rule_priority is None]
        if missing_priority:
            findings.append(
                RiskFinding(
                    risk_type="missing_rule_priority",
                    severity=Severity.medium,
                    message=f"Host '{host}' has routes without Application Gateway rule priority",
                    host=host,
                    namespaces=sorted({r.namespace for r in missing_priority}),
                    ingresses=sorted({r.ingress_name for r in missing_priority}),
                )
            )

        paths = [r.path for r in host_routes]
        if "/" in paths and len(set(paths)) > 1:
            findings.append(
                RiskFinding(
                    risk_type="catch_all_shadowing",
                    severity=Severity.high,
                    message=f"Host '{host}' includes '/' and may shadow more specific paths",
                    host=host,
                    paths=sorted(set(paths)),
                )
            )

        if len(paths) != len(set(paths)):
            findings.append(
                RiskFinding(
                    risk_type="overlapping_paths",
                    severity=Severity.medium,
                    message=f"Host '{host}' has overlapping path definitions",
                    host=host,
                    paths=sorted(set(paths)),
                )
            )

    all_hosts = list(host_to_routes.keys())
    for i, first in enumerate(all_hosts):
        for second in all_hosts[i + 1 :]:
            if _has_wildcard_conflict(first, second):
                findings.append(
                    RiskFinding(
                        risk_type="wildcard_host_conflict",
                        severity=Severity.high,
                        message=f"Wildcard conflict between '{first}' and '{second}'",
                        host=f"{first} <-> {second}",
                    )
                )

    counts = {sev.value: 0 for sev in Severity}
    for finding in findings:
        counts[finding.severity.value] += 1

    return AnalysisReport(
        total_routes=len(routes),
        total_findings=len(findings),
        findings_by_severity=counts,
        findings=findings,
    )


def has_findings_at_or_above(report: AnalysisReport, threshold: Severity) -> bool:
    order = {Severity.low: 1, Severity.medium: 2, Severity.high: 3}
    return any(order[f.severity] >= order[threshold] for f in report.findings)
