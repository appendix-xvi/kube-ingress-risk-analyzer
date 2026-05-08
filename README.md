# kube-ingress-risk-analyzer

`kube-ingress-risk-analyzer` is a production-style DevOps portfolio CLI project that inspects Kubernetes Ingress resources and highlights routing risks before deployment.

## Features

- Read ingress definitions from:
  - `kubectl get ingress -A -o json` file export
  - Live cluster via `kubectl` and kubeconfig context
- Extracts:
  - namespace
  - ingress name
  - ingress class
  - host
  - paths
  - backend service
  - `appgw.ingress.kubernetes.io/rule-priority` annotation
- Detects routing risks:
  - duplicate hosts across namespaces
  - wildcard host conflicts (`*.example.com` vs `app.example.com`)
  - missing Application Gateway rule priority
  - same host with overlapping paths
  - catch-all `/` path that may shadow specific paths
- Output formats:
  - terminal table
  - JSON report
  - Markdown report (CI/CD summary friendly)

## Project structure

```text
kube-ingress-risk-analyzer/
├── .github/workflows/ci.yml
├── kube_ingress_risk_analyzer/
│   ├── analyzer.py
│   ├── cli.py
│   ├── models.py
│   ├── parser.py
│   └── reporters.py
├── samples/
│   └── ingress.json
├── tests/
│   └── test_analyzer.py
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.12+
- `kubectl` (for live mode)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Usage examples

Analyze from file (table output by default):

```bash
kube-ingress-risk-analyzer analyze --file samples/ingress.json
```

Analyze from file and export markdown:

```bash
kube-ingress-risk-analyzer analyze --file samples/ingress.json --output markdown --out-file report.md
```

Analyze from live cluster using specific context:

```bash
kube-ingress-risk-analyzer analyze --live --context my-cluster --output json
```

Fail CI when high-risk findings exist:

```bash
kube-ingress-risk-analyzer analyze --file samples/ingress.json --fail-on high
```

This command exits with status code `2` when findings match or exceed the requested severity threshold.

## How to export source data from cluster

```bash
kubectl get ingress -A -o json > ingress.json
kube-ingress-risk-analyzer analyze --file ingress.json --output markdown
```

## Development

```bash
ruff check .
pytest -q
```

## Docker

Build:

```bash
docker build -t kube-ingress-risk-analyzer:latest .
```

Run against a local file mounted into container:

```bash
docker run --rm -v "$PWD/samples:/data" kube-ingress-risk-analyzer:latest analyze --file /data/ingress.json --output json
```
