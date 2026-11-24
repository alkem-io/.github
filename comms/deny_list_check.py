#!/usr/bin/env python3
"""
deny_list_check.py - scan one or more repositories for deprecated Alkemio
identity values (old LinkedIn slugs, retired taglines, wrong entity names,
wrong licence strings) defined in contracts/deny-list.json.

Usage:
  python3 deny_list_check.py <repo-dir> [<repo-dir> ...]
        [--rules path/to/deny-list.json]
        [--approved D1,D2]        # decisions signed off: their gated rules become errors
        [--format md|json|github] # md report (default), json, or GitHub annotations
        [--ci]                    # exit 1 if any error-level finding

Standard library only, so it runs in any CI image.

Design notes
- Only matches explicit patterns. It never touches LinkedIn *sign-in*
  (Kratos OIDC, AuthenticationType.LINKEDIN, test selectors): those do not
  contain a /company/ URL or a named tagline, so no rule matches them.
- Historical records (specs/, changelogs, archives) are excluded by default:
  we do not rewrite history, we stop repeating it.
- A rule gated on a decision (D1, D2 ...) reports as 'warn' until that
  decision is passed with --approved, then as its declared severity.
"""
import argparse
import fnmatch
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_SIBLING_RULES = os.path.join(HERE, "deny-list.json")
_SPEC_RULES = os.path.join(HERE, "..", "contracts", "deny-list.json")
DEFAULT_RULES = _SIBLING_RULES if os.path.exists(_SIBLING_RULES) else _SPEC_RULES
TEXT_EXT = {
    ".md", ".mdx", ".txt", ".html", ".htm", ".hbs", ".mjml", ".json", ".yaml",
    ".yml", ".toml", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go",
    ".css", ".scss", ".svg", ".xml", ".env", ".ini", ".cfg", ".sh", ".graphql",
}
MAX_BYTES = 2_000_000


def load_rules(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    for r in data["rules"]:
        flags = re.MULTILINE
        r["_re"] = re.compile(r["pattern"], flags)
    return data


def excluded(rel, patterns):
    rel_s = "/" + rel.replace(os.sep, "/")
    for p in patterns:
        if p in rel_s or fnmatch.fnmatch(rel_s, "*" + p):
            return True
    return False


def effective_severity(rule, approved):
    gate = rule.get("gate", "none")
    if gate == "none":
        return rule["severity"]
    # A gated rule is advisory until its decision is signed off, then it blocks.
    return "error" if gate in approved else "warn"


def scan_repo(root, data, approved):
    findings = []
    repo = os.path.basename(os.path.abspath(root))
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        # prune excluded directories early
        dirnames[:] = [
            d for d in dirnames
            if not excluded(os.path.join(rel_dir, d) + "/", data["globalExclude"])
        ]
        for name in filenames:
            rel = os.path.normpath(os.path.join(rel_dir, name))
            if excluded(rel, data["globalExclude"]):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext not in TEXT_EXT and name not in ("Dockerfile", "README", "LICENSE"):
                continue
            full = os.path.join(dirpath, name)
            try:
                if os.path.getsize(full) > MAX_BYTES:
                    continue
                with open(full, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
            except OSError:
                continue
            for rule in data["rules"]:
                rule_ex = [e for e in rule.get("exclude", [])]
                if rule_ex and excluded(repo + "/" + rel, rule_ex):
                    continue
                for m in rule["_re"].finditer(text):
                    line_no = text.count("\n", 0, m.start()) + 1
                    line = text.splitlines()[line_no - 1] if text else ""
                    findings.append({
                        "repo": repo,
                        "path": rel.replace(os.sep, "/"),
                        "line": line_no,
                        "rule": rule["id"],
                        "severity": effective_severity(rule, approved),
                        "gate": rule.get("gate", "none"),
                        "match": m.group(0)[:120],
                        "context": line.strip()[:160],
                        "message": rule["message"],
                        "replacement": rule["replacement"],
                    })
    return findings


def render_md(findings, repos):
    out = ["# Estate sweep report", ""]
    errs = sum(1 for f in findings if f["severity"] == "error")
    warns = len(findings) - errs
    out.append(f"Repositories scanned: **{len(repos)}** · Findings: **{len(findings)}** "
               f"(errors: {errs}, warnings: {warns})")
    out.append("")
    by_rule = {}
    for f in findings:
        by_rule.setdefault(f["rule"], 0)
        by_rule[f["rule"]] += 1
    if by_rule:
        out += ["| Rule | Count |", "|---|---|"]
        out += [f"| {k} | {v} |" for k, v in sorted(by_rule.items())]
        out.append("")
    out += ["| Sev | Rule | Gate | Repo | File:line | Match | Replace with |",
            "|---|---|---|---|---|---|---|"]
    for f in sorted(findings, key=lambda x: (x["severity"] != "error", x["repo"], x["path"], x["line"])):
        match = f["match"].replace("|", "\\|")
        out.append(f"| {f['severity']} | {f['rule']} | {f['gate']} | {f['repo']} | "
                   f"`{f['path']}:{f['line']}` | `{match}` | {f['replacement']} |")
    return "\n".join(out) + "\n"


def render_github(findings):
    lines = []
    for f in findings:
        level = "error" if f["severity"] == "error" else "warning"
        lines.append(f"::{level} file={f['repo']}/{f['path']},line={f['line']},title={f['rule']}::"
                     f"{f['message']} Replace with: {f['replacement']}")
    return "\n".join(lines) + ("\n" if lines else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repos", nargs="+")
    ap.add_argument("--rules", default=DEFAULT_RULES)
    ap.add_argument("--approved", default="")
    ap.add_argument("--format", default="md", choices=["md", "json", "github"])
    ap.add_argument("--ci", action="store_true")
    a = ap.parse_args()

    data = load_rules(a.rules)
    approved = {x.strip() for x in a.approved.split(",") if x.strip()}
    findings = []
    for r in a.repos:
        findings += scan_repo(r, data, approved)

    if a.format == "json":
        sys.stdout.write(json.dumps(findings, indent=2) + "\n")
    elif a.format == "github":
        sys.stdout.write(render_github(findings))
    else:
        sys.stdout.write(render_md(findings, a.repos))

    if a.ci and any(f["severity"] == "error" for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
