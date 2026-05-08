from kube_ingress_risk_analyzer.analyzer import analyze_routes, extract_routes, has_findings_at_or_above
from kube_ingress_risk_analyzer.models import Severity


def test_extract_routes_and_detect_core_risks():
    payload = {
        "items": [
            {
                "metadata": {
                    "name": "ing-a",
                    "namespace": "ns-a",
                    "annotations": {"appgw.ingress.kubernetes.io/rule-priority": "200"},
                },
                "spec": {
                    "rules": [
                        {
                            "host": "app.example.com",
                            "http": {
                                "paths": [
                                    {"path": "/", "backend": {"service": {"name": "svc-a"}}},
                                    {"path": "/api", "backend": {"service": {"name": "svc-b"}}},
                                ]
                            },
                        }
                    ]
                },
            },
            {
                "metadata": {"name": "ing-b", "namespace": "ns-b", "annotations": {}},
                "spec": {
                    "rules": [
                        {
                            "host": "app.example.com",
                            "http": {
                                "paths": [
                                    {"path": "/", "backend": {"service": {"name": "svc-c"}}}
                                ]
                            },
                        },
                        {
                            "host": "*.example.com",
                            "http": {
                                "paths": [
                                    {"path": "/", "backend": {"service": {"name": "svc-d"}}}
                                ]
                            },
                        },
                    ]
                },
            },
        ]
    }

    routes = extract_routes(payload)
    assert len(routes) == 4

    report = analyze_routes(routes)
    risk_types = {f.risk_type for f in report.findings}
    assert "duplicate_host_across_namespaces" in risk_types
    assert "wildcard_host_conflict" in risk_types
    assert "missing_rule_priority" in risk_types
    assert "catch_all_shadowing" in risk_types
    assert has_findings_at_or_above(report, Severity.high)
