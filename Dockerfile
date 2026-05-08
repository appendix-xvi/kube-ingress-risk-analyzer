FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY kube_ingress_risk_analyzer ./kube_ingress_risk_analyzer

RUN pip install --no-cache-dir .

ENTRYPOINT ["kube-ingress-risk-analyzer"]
CMD ["--help"]
