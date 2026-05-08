"""CLI entrypoint for kube-ingress-risk-analyzer."""

from __future__ import annotations

import argparse
import sys

from .analyzer import analyze_routes, extract_routes, has_findings_at_or_above
from .models import Severity
from .parser import load_ingresses_from_file, load_ingresses_from_live_cluster
from .reporters import render_json, render_markdown, render_terminal_table, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kube-ingress-risk-analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze ingress resources")
    source = analyze.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", help="Path to kubectl ingress JSON file")
    source.add_argument("--live", action="store_true", help="Read ingress from live cluster")

    analyze.add_argument("--context", help="Kubeconfig context for live mode", default=None)
    analyze.add_argument(
        "--output",
        choices=["table", "json", "markdown"],
        default="table",
        help="Output format",
    )
    analyze.add_argument("--out-file", help="Optional file path to write rendered output", default=None)
    analyze.add_argument(
        "--fail-on",
        choices=[s.value for s in Severity],
        default=None,
        help="Exit non-zero when findings at or above the specified severity are present",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "analyze":
        payload = (
            load_ingresses_from_live_cluster(context=args.context)
            if args.live
            else load_ingresses_from_file(args.file)
        )
        routes = extract_routes(payload)
        report = analyze_routes(routes)

        if args.output == "json":
            content = render_json(report)
        elif args.output == "markdown":
            content = render_markdown(report)
        else:
            content = render_terminal_table(report)

        print(content)
        write_report(content, args.out_file)

        if args.fail_on and has_findings_at_or_above(report, Severity(args.fail_on)):
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
