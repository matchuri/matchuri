#!/usr/bin/env python3
"""Audit Matchuri docs for size, governance bucket, and invalid local links."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import unquote


FORBIDDEN_LINK_PATTERNS = [
    re.compile(r"\]\(matchuri\.wiki[/)]"),
    re.compile(r"`matchuri\.wiki/"),
    re.compile(r"\]\(\.\./docs/"),
]
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\((?P<target>[^)]+)\)")


@dataclass(frozen=True)
class DocEntry:
    path: Path
    size: int
    bucket: str
    reason: str


def classify(path: Path, size: int) -> tuple[str, str]:
    p = path.as_posix()
    name = path.name

    if p == "docs/README.md" or name == "index.md":
        return "KEEP", "navigation entry point"

    if p.startswith("docs/references/") or "/references/" in p:
        return "SKILL", "tool/reference material should be loaded only when needed"

    if p.startswith("docs/api/"):
        if name == "api-numbering-policy.md":
            return "KEEP", "API governance contract"
        if size > 10_000:
            return "HARNESS", "large API detail should move toward OpenAPI/status checks"
        return "KEEP", "concise API contract detail"

    if p.startswith("docs/data/"):
        if name == "policies.md":
            return "KEEP", "durable data policy not derivable from JPA mappings"
        return "KEEP", "data model navigation entry point"

    if p.startswith("docs/backend/"):
        if name in {"index.md", "architecture.md", "guide.md"}:
            return "KEEP", "backend development entry point"
        if name in {"quality-score.md", "security.md", "reliability.md"}:
            return "KEEP", "concise backend governance contract; review procedure lives in skill"
        return "KEEP", "backend reference"

    if p.startswith("docs/frontend/"):
        return "KEEP", "frontend development entry point"

    if p.startswith("docs/product/"):
        if size > 3_000:
            return "WIKI", "product narrative should be human-facing unless it is a contract"
        return "KEEP", "concise product contract"

    if p.startswith("docs/decisions/"):
        if name in {
            "index.md",
            "documentation-source-of-truth.md",
            "domain-language.md",
            "api-docs-strategy.md",
        }:
            return "KEEP", "durable governance or domain decision"
        if size > 10_000:
            return "WIKI", "long decision should be summarized for humans and slimmed in docs"
        return "KEEP", "ADR-grade decision"

    return "KEEP", "default development document"


def find_forbidden_links(root: Path) -> list[tuple[Path, int, str]]:
    findings: list[tuple[Path, int, str]] = []
    search_roots = [root / "README.md", root / "AGENTS.md", root / "docs"]

    files: list[Path] = []
    for item in search_roots:
        if item.is_file():
            files.append(item)
        elif item.is_dir():
            files.extend(item.rglob("*.md"))

    for path in files:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            lines = path.read_text(encoding="utf-8-sig").splitlines()

        for idx, line in enumerate(lines, start=1):
            if any(pattern.search(line) for pattern in FORBIDDEN_LINK_PATTERNS):
                findings.append((path.relative_to(root), idx, line.strip()))

    return findings


def markdown_files(root: Path) -> list[Path]:
    files = [root / "README.md", root / "AGENTS.md"]
    files.extend((root / "docs").rglob("*.md"))
    return [path for path in files if path.is_file()]


def find_broken_local_links(root: Path) -> list[tuple[Path, int, str]]:
    findings: list[tuple[Path, int, str]] = []
    for path in markdown_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            lines = path.read_text(encoding="utf-8-sig").splitlines()

        for line_no, line in enumerate(lines, start=1):
            for match in MARKDOWN_LINK_PATTERN.finditer(line):
                target = match.group("target").strip().strip("<>")
                if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                target = unquote(target.split("#", 1)[0].split("?", 1)[0])
                candidate = (root / target.lstrip("/")) if target.startswith("/") else (path.parent / target)
                if not candidate.resolve().exists():
                    findings.append((path.relative_to(root), line_no, match.group("target")))

    return findings


def build_inventory(root: Path) -> list[DocEntry]:
    docs_root = root / "docs"
    entries: list[DocEntry] = []
    for path in sorted(docs_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        size = path.stat().st_size
        bucket, reason = classify(rel, size)
        entries.append(DocEntry(rel, size, bucket, reason))
    return entries


def markdown_report(root: Path) -> str:
    entries = build_inventory(root)
    total_size = sum(entry.size for entry in entries)
    bucket_counts: dict[str, int] = {}
    for entry in entries:
        bucket_counts[entry.bucket] = bucket_counts.get(entry.bucket, 0) + 1

    lines = [
        "# Docs Governance Inventory",
        "",
        "Generated by `.agents/skills/matchuri-doc-governance/scripts/audit_docs.py`.",
        "",
        "## Summary",
        "",
        f"- Total docs files: {len(entries)}",
        f"- Total docs size: {total_size} bytes",
    ]

    for bucket in ["KEEP", "SKILL", "HARNESS", "WIKI", "REMOVE"]:
        lines.append(f"- {bucket}: {bucket_counts.get(bucket, 0)}")

    lines.extend([
        "",
        "## Largest Files",
        "",
        "| Path | Bytes | Suggested bucket |",
        "| --- | ---: | --- |",
    ])
    for entry in sorted(entries, key=lambda item: item.size, reverse=True)[:15]:
        lines.append(f"| `{entry.path.as_posix()}` | {entry.size} | {entry.bucket} |")

    lines.extend([
        "",
        "## Inventory",
        "",
        "| Path | Bytes | Suggested bucket | Reason |",
        "| --- | ---: | --- | --- |",
    ])
    for entry in entries:
        lines.append(
            f"| `{entry.path.as_posix()}` | {entry.size} | {entry.bucket} | {entry.reason} |"
        )

    forbidden = find_forbidden_links(root)
    lines.extend([
        "",
        "## Forbidden Link Findings",
        "",
    ])
    if forbidden:
        lines.extend(["| Path | Line | Text |", "| --- | ---: | --- |"])
        for path, line_no, text in forbidden:
            safe_text = text.replace("|", "\\|")
            lines.append(f"| `{path.as_posix()}` | {line_no} | `{safe_text}` |")
    else:
        lines.append("No forbidden tracked links found.")

    broken = find_broken_local_links(root)
    lines.extend([
        "",
        "## Broken Local Link Findings",
        "",
    ])
    if broken:
        lines.extend(["| Path | Line | Target |", "| --- | ---: | --- |"])
        for path, line_no, target in broken:
            safe_target = target.replace("|", "\\|")
            lines.append(f"| `{path.as_posix()}` | {line_no} | `{safe_target}` |")
    else:
        lines.append("No broken local links found.")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when forbidden or broken local links are found")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = markdown_report(root)

    print(report)

    if args.strict and (find_forbidden_links(root) or find_broken_local_links(root)):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
