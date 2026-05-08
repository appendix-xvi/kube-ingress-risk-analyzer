"""Output formatters for analysis reports."""

from __future__ import annotations

import json

from .models import AnalysisReport


def render_terminal_table(report: AnalysisReport) -> str:
    headers = ["Severity", "Risk Type", "Host", "Message"]
    rows = [headers]
    for f in report.findings:
        rows.append([f.severity.value.upper(), f.risk_type, f.host or "-", f.message])

    col_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    sep = " | "
    line = "-+-".join("-" * w for w in col_widths)

    out = []
    out.append(sep.join(cell.ljust(col_widths[i]) for i, cell in enumerate(rows[0])))
    out.append(line)
    for row in rows[1:]:
        out.append(sep.join(cell.ljust(col_widths[i]) for i, cell in enumerate(row)))

    if not report.findings:
        out.append("No findings detected.")

    return "\n".join(out)


def render_json(report: AnalysisReport) -> str:
    return report.model_dump_json(indent=2)


def render_markdown(report: AnalysisReport) -> str:
    summary = (
        f"- Total routes: **{report.total_routes}**\n"
        f"- Total findings: **{report.total_findings}**\n"
        f"- High: **{report.findings_by_severity['high']}**, "
        f"Medium: **{report.findings_by_severity['medium']}**, "
        f"Low: **{report.findings_by_severity['low']}**"
    )

    lines = ["# Ingress Risk Analysis Report", "", "## Summary", summary, "", "## Findings", ""]
    if not report.findings:
        lines.append("No findings detected.")
    else:
        lines.append("| Severity | Risk Type | Host | Message |")
        lines.append("| --- | --- | --- | --- |")
        for finding in report.findings:
            lines.append(
                f"| {finding.severity.value} | {finding.risk_type} | {finding.host or '-'} | {finding.message} |"
            )
    return "\n".join(lines)


def write_report(content: str, path: str | None) -> None:
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
