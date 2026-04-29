"""Pruner CLI — `pruner` entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from pruner_wrapper import __version__, lore
from pruner_wrapper.allowlist import AllowlistError, apply_allowlist, load_allowlist
from pruner_wrapper.cisco_runner import PINNED_VERSION as CISCO_PINNED_VERSION
from pruner_wrapper.cisco_runner import cisco_version, run_cisco
from pruner_wrapper.cisco_runner import is_available as cisco_is_available
from pruner_wrapper.compose import build_report
from pruner_wrapper.pack_runner import filter_by_threshold, load_pack, scan_tree
from pruner_wrapper.policy import PolicyError, load_policy
from pruner_wrapper.policy import evaluate as evaluate_policy
from pruner_wrapper.sarif import findings_from_sarif, write_sarif
from pruner_wrapper.types import SEVERITY_RANK, Finding, Severity, ToolEntry

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_RULES_DIR = REPO_ROOT / "rules"

EXIT_OK = 0
EXIT_FINDINGS_BELOW = 1
EXIT_FINDINGS_ABOVE = 2
EXIT_INTERNAL = 3


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pruner",
        description="Pruner — Coroboros's attestation chain for agent skill repositories.",
    )
    parser.add_argument("--version", action="version", version=f"pruner {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan a target path")
    scan.add_argument("path", type=Path)
    scan.add_argument("--rules", type=Path, default=None,
                      help="Rules directory (default: ./rules in this repo)")
    scan.add_argument("--severity-threshold",
                      choices=["critical", "high", "medium", "low", "info"],
                      default="info")
    scan.add_argument("--format", choices=["sarif", "json", "terminal"], default="terminal")
    scan.add_argument("--allowlist", type=Path, default=None)
    scan.add_argument("--policy", type=Path, default=None)
    scan.add_argument("--output", type=Path, default=None)
    scan.add_argument("--skill-pattern", default="skills/*/SKILL.md")
    scan.add_argument("--with-cisco", dest="with_cisco", action="store_true", default=True)
    scan.add_argument("--without-cisco", dest="with_cisco", action="store_false")
    scan.add_argument("--with-snyk", dest="with_snyk", action="store_true", default=False)
    scan.add_argument("--without-snyk", dest="with_snyk", action="store_false")
    scan.add_argument("--fail-on", choices=["critical", "high", "medium", "low", "never"],
                      default="never",
                      help="Exit 2 if any finding meets or exceeds this severity.")
    scan.add_argument("--target-repo", default="<local>",
                      help="Target repo identifier for the report metadata.")

    compose = sub.add_parser("compose", help="Compose a report from one or more SARIF files.")
    compose.add_argument("--inputs", nargs="+", type=Path, required=True)
    compose.add_argument("--output", type=Path, required=True)
    compose.add_argument("--allowlist", type=Path, default=None)
    compose.add_argument("--policy", type=Path, default=None)
    compose.add_argument("--target-repo", default="<local>")
    compose.add_argument("--target-commit", default=None)

    badge = sub.add_parser("badge", help="Render a badge SVG from a report.")
    badge.add_argument("--report", type=Path, required=True)
    badge.add_argument("--output", type=Path, required=True)
    badge.add_argument("--engine-sha", default=None)

    gate = sub.add_parser("gate", help="Exit 2 if findings exceed the fail-on threshold.")
    gate.add_argument("--report", type=Path, required=True)
    gate.add_argument("--fail-on", choices=["critical", "high", "medium", "low", "never"],
                      default="critical")

    return parser


def _resolve_rules_dir(arg: Path | None) -> Path:
    if arg is not None:
        return arg
    cwd_rules = Path.cwd() / "rules"
    if cwd_rules.exists():
        return cwd_rules
    return DEFAULT_RULES_DIR


def _scan(args: argparse.Namespace) -> int:
    target: Path = args.path.resolve()
    if not target.exists():
        print(lore.message("missing_input", field=str(target)), file=sys.stderr)
        return EXIT_INTERNAL

    rules_dir = _resolve_rules_dir(args.rules).resolve()
    rules = load_pack(rules_dir)
    if not rules:
        print(f"warning: no rules loaded from {rules_dir}", file=sys.stderr)

    scan_pd = False
    policy = None
    if args.policy is not None:
        try:
            policy = load_policy(args.policy)
            scan_pd = bool(policy and policy.scan_prompt_defense_posture)
        except PolicyError as exc:
            print(lore.message("config_error"), exc, file=sys.stderr)
            return EXIT_INTERNAL

    findings: list[Finding] = scan_tree(
        root=target,
        rules=rules,
        skill_pattern=args.skill_pattern,
        scan_prompt_defense=scan_pd,
    )

    tools: list[ToolEntry] = [
        ToolEntry(name="pruner-wrapper", version=__version__, mode="policy-pack"),
    ]

    if args.with_cisco:
        if cisco_is_available():
            cisco_sarif = run_cisco(target)
            if cisco_sarif is not None:
                cisco_findings = findings_from_sarif(
                    cisco_sarif, default_tool_name="cisco-ai-skill-scanner"
                )
                findings.extend(cisco_findings)
                tools.append(
                    ToolEntry(
                        name="cisco-ai-skill-scanner",
                        version=cisco_version() or CISCO_PINNED_VERSION,
                        mode="primary",
                    )
                )
        else:
            print(
                lore.message("cisco_drift")
                + " (binary `skill-scanner` missing — install pinned engine via setup-cisco.sh)",
                file=sys.stderr,
            )

    allowlist_entries = []
    if args.allowlist is not None:
        try:
            allowlist_entries = load_allowlist(args.allowlist)
        except AllowlistError as exc:
            print(lore.message("config_error"), exc, file=sys.stderr)
            return EXIT_INTERNAL
        findings, applied = apply_allowlist(findings, allowlist_entries)
    else:
        applied = []

    threshold: Severity = args.severity_threshold
    visible = filter_by_threshold(findings, threshold)

    target_paths = [
        str(p.relative_to(target)) for p in target.rglob("*") if p.is_file()
    ][:200]

    if args.format == "sarif":
        out_path = args.output or Path(".pruner/coroboros.sarif")
        write_sarif(
            visible, out_path, tool_name="pruner-wrapper", tool_version=__version__
        )
        print(str(out_path))
    elif args.format == "json":
        report = build_report(
            findings=visible,
            allowlisted=applied,
            tools=tools,
            target_repo=args.target_repo,
            target_commit=None,
            target_path=str(target),
            policy_evaluation=evaluate_policy(
                policy,
                findings=visible,
                allowlisted=applied,
                tools=tools,
                score=100,
                target_paths=target_paths,
            ),
        )
        out = json.dumps(report, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(out, encoding="utf-8")
        else:
            print(out)
    else:
        _terminal_report(visible, applied, threshold)

    return _exit_code(visible, args.fail_on)


def _terminal_report(
    findings: list[Finding], applied: list[Any], threshold: Severity
) -> None:
    print(lore.message("scan_start", threshold=threshold))
    if not findings:
        print(lore.message("scan_clean"))
        return
    has_critical = any(f.severity_effective == "critical" for f in findings)
    if has_critical:
        print(lore.message("scan_critical"))
    else:
        print(lore.message("scan_below_threshold", count=len(findings)))
    for f in findings:
        loc = f"{f.location.path}:{f.location.line or 1}"
        print(f"  [{f.severity_effective.upper()}] {f.id} — {loc} — {f.message}")
    if applied:
        print(f"({len(applied)} allowlisted entries applied)")


def _exit_code(findings: list[Finding], fail_on: str) -> int:
    if fail_on == "never":
        return EXIT_OK if not findings else EXIT_FINDINGS_BELOW
    cutoff = SEVERITY_RANK[fail_on]  # type: ignore[index]
    above = [f for f in findings if SEVERITY_RANK[f.severity_effective] >= cutoff]
    if above:
        return EXIT_FINDINGS_ABOVE
    if findings:
        return EXIT_FINDINGS_BELOW
    return EXIT_OK


def _compose(args: argparse.Namespace) -> int:
    findings: list[Finding] = []
    tools: list[ToolEntry] = []
    for input_path in args.inputs:
        if not input_path.exists():
            continue
        try:
            sarif = json.loads(input_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        # Discover tool name from the SARIF run for the tools[] entry
        for run in sarif.get("runs", []):
            driver = run.get("tool", {}).get("driver", {})
            tool_name = driver.get("name", "external")
            tool_version = driver.get("version", "0.0.0")
            mode = "primary" if tool_name == "cisco-ai-skill-scanner" else "policy-pack"
            if tool_name == "gitleaks":
                mode = "secrets"
            elif tool_name == "snyk-agent-scan":
                mode = "second-opinion"
            tools.append(ToolEntry(name=tool_name, version=tool_version, mode=mode))  # type: ignore[arg-type]
        findings.extend(findings_from_sarif(sarif))

    try:
        allowlist_entries = load_allowlist(args.allowlist)
    except AllowlistError as exc:
        print(lore.message("config_error"), exc, file=sys.stderr)
        return EXIT_INTERNAL
    findings, applied = apply_allowlist(findings, allowlist_entries)

    try:
        policy = load_policy(args.policy)
    except PolicyError as exc:
        print(lore.message("config_error"), exc, file=sys.stderr)
        return EXIT_INTERNAL

    report = build_report(
        findings=findings,
        allowlisted=applied,
        tools=tools or [ToolEntry(name="pruner-wrapper", version=__version__, mode="policy-pack")],
        target_repo=args.target_repo,
        target_commit=args.target_commit,
        policy_evaluation=evaluate_policy(
            policy,
            findings=findings,
            allowlisted=applied,
            tools=tools,
            score=100,
            target_paths=[],
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return EXIT_OK


def _badge(args: argparse.Namespace) -> int:
    from pruner_wrapper.badge import render_badge_svg

    report = json.loads(args.report.read_text(encoding="utf-8"))
    grade = report.get("summary", {}).get("grade", "F")
    engine_sha = args.engine_sha or _engine_sha_from_tools(report.get("tools", []))
    svg = render_badge_svg(grade=grade, engine_sha=engine_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")
    return EXIT_OK


def _engine_sha_from_tools(tools: list[dict[str, Any]]) -> str:
    for tool in tools:
        if tool.get("name") == "cisco-ai-skill-scanner":
            sha = tool.get("sha") or tool.get("version") or ""
            return str(sha)[:8]
    return CISCO_PINNED_VERSION


def _gate(args: argparse.Namespace) -> int:
    report = json.loads(args.report.read_text(encoding="utf-8"))
    findings_raw = report.get("findings", [])
    findings = [
        Finding(
            id=f["id"],
            category=f["category"],
            severity_declared=f["severity_declared"],
            severity_effective=f["severity_effective"],
            tool=f["tool"],
            location=__import__(
                "pruner_wrapper.types", fromlist=["Location"]
            ).Location(path=f["location"]["path"]),
            message=f["message"],
        )
        for f in findings_raw
    ]
    return _exit_code(findings, args.fail_on)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        return _scan(args)
    if args.command == "compose":
        return _compose(args)
    if args.command == "badge":
        return _badge(args)
    if args.command == "gate":
        return _gate(args)
    parser.print_help()
    return EXIT_INTERNAL


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())


# Ensure yaml import is referenced for static-analysis tooling
_ = yaml
