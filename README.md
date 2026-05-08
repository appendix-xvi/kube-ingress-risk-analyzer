# kube-ingress-risk-analyzer

Work-in-progress DevOps portfolio CLI project for inspecting Kubernetes Ingress resources and identifying routing risks before deployment.

This is a strong project idea, but it should not be presented as a completed CLI until the Python package, tests, sample input, and CI workflow are committed.

## Problem this project targets

Ingress issues are easy to miss during review, especially when multiple teams share the same Kubernetes cluster or Application Gateway / ingress controller.

The analyzer is intended to catch risks such as:

- Duplicate hosts across namespaces
- Wildcard host conflicts such as `*.example.com` vs `app.example.com`
- Missing `appgw.ingress.kubernetes.io/rule-priority` annotation
- Same host with overlapping paths
- Catch-all `/` paths that may shadow more specific routes

## Intended input sources

```text
kubectl get ingress -A -o json > ingress.json
```

Planned modes:

```text
File mode: analyze an exported ingress JSON file
Live mode: call kubectl using the selected kubeconfig context
```

## Planned output formats

```text
terminal table
JSON report
Markdown report for CI/CD summaries
```

## Current repository status

```text
Status: work in progress
Ready to showcase: no
```

## Required files before showcase

```text
kube_ingress_risk_analyzer/analyzer.py
kube_ingress_risk_analyzer/cli.py
kube_ingress_risk_analyzer/models.py
kube_ingress_risk_analyzer/parser.py
kube_ingress_risk_analyzer/reporters.py
samples/ingress.json
tests/test_analyzer.py
Dockerfile
pyproject.toml
.github/workflows/ci.yml
README.md
```

Do not claim installation or CLI commands work until these files are committed and tested.

## Intended CLI examples

Analyze from a file:

```bash
kube-ingress-risk-analyzer analyze --file samples/ingress.json
```

Export a Markdown report:

```bash
kube-ingress-risk-analyzer analyze \
  --file samples/ingress.json \
  --output markdown \
  --out-file report.md
```

Fail CI when high-risk findings exist:

```bash
kube-ingress-risk-analyzer analyze \
  --file samples/ingress.json \
  --fail-on high
```

## Showcase readiness checklist

Before publishing this as a finished portfolio project, verify:

- `pip install -e .[dev]` works.
- `pytest -q` passes.
- `ruff check .` passes.
- Sample input includes duplicate host and wildcard conflict cases.
- Markdown report output is committed as an example.
- Docker build works.
- README commands match actual CLI behavior.

## License

MIT
