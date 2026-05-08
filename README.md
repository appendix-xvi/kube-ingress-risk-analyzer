# Kubernetes Ingress Risk Analyzer

A Kubernetes analysis tool concept for reviewing Ingress resources and identifying routing, exposure, and configuration risks before they cause production issues.

The goal of this repository is to provide a practical DevOps/SRE utility that helps inspect Kubernetes Ingress definitions and produce a readable risk summary.

## Overview

Kubernetes Ingress configuration can become difficult to review as environments grow. Host rules, wildcard domains, TLS settings, annotations, path matching, and ingress controller behavior can create unexpected routing or exposure risks.

This project is intended to analyze Ingress resources and highlight issues such as:

- Wildcard host usage
- Missing TLS configuration
- Conflicting host rules
- Broad path matching
- Risky annotations
- Ingress class mismatch
- Duplicate hosts across namespaces
- External exposure indicators

## Target Use Cases

- Pre-deployment review of Ingress manifests
- Cluster audit for risky routing rules
- CI/CD validation before applying Kubernetes changes
- Troubleshooting route conflicts
- Documenting ingress exposure across namespaces

## Suggested Input Sources

The analyzer can support one or more input modes:

```bash
kubectl get ingress -A -o json
```

```bash
kubectl get ingress -A -o yaml
```

```bash
./manifests/**/*.yaml
```

## Example Output

```text
Risk Summary
------------
Total ingress resources: 24
High risk: 2
Medium risk: 5
Low risk: 8

Findings
--------
[HIGH] wildcard host detected: *.example.internal
[HIGH] duplicate host across namespaces: api.example.internal
[MEDIUM] TLS not configured for host: admin.example.internal
[LOW] ingress class not explicitly defined
```

## Suggested Repository Structure

```text
kube-ingress-risk-analyzer/
├── README.md
├── src/
├── tests/
├── examples/
│   ├── ingress.json
│   └── ingress.yaml
├── docs/
└── scripts/
```

## Analysis Rules

| Rule | Risk |
|---|---|
| Wildcard host | High |
| Duplicate host across namespaces | High |
| Missing TLS on externally exposed host | High |
| Broad catch-all path | Medium |
| Missing ingress class | Medium |
| Risky ingress controller annotations | Medium |
| Missing owner or service metadata | Low |

## Validation Checklist

A useful analyzer should confirm:

- It parses Kubernetes Ingress JSON and YAML correctly
- It supports multi-namespace input
- It detects wildcard and duplicate hosts
- It separates high, medium, and low risk findings
- It exits non-zero when high-risk findings are detected in CI mode
- It produces readable output for humans and structured output for automation

## Production Considerations

Before using this against a real cluster, review:

- Cluster access permissions
- Namespace scope
- Sensitive hostname handling
- CI/CD failure threshold
- Controller-specific annotation rules
- Report retention and sharing policy

## Notes

- This repository is intended as a DevOps/SRE utility project.
- Use sanitized example manifests for public demos.
- Avoid committing internal domain names, private service names, or production routing data.
