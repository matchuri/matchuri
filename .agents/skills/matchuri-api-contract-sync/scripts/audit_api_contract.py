#!/usr/bin/env python3
"""Lightweight Matchuri API contract drift audit."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys


HTTP_MAPPING = {
    "GetMapping": "GET",
    "PostMapping": "POST",
    "PutMapping": "PUT",
    "PatchMapping": "PATCH",
    "DeleteMapping": "DELETE",
}


@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str
    source: Path
    line: int


@dataclass(frozen=True)
class StatusRow:
    api_id: str
    domain: str
    method: str
    path: str
    status: str
    source_line: int


def normalize_path(path: str) -> str:
    path = path.strip()
    if not path:
        return ""
    path = re.sub(r"/+", "/", path)
    if not path.startswith("/"):
        path = "/" + path
    if len(path) > 1:
        path = path.rstrip("/")
    return path


def extract_annotation_value(annotation: str) -> str:
    match = re.search(r'\(\s*(?:path\s*=\s*|value\s*=\s*)?"([^"]*)"', annotation)
    return match.group(1) if match else ""


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def parse_backend_endpoints(root: Path) -> list[Endpoint]:
    api_root = root / "backend" / "src" / "main" / "java" / "matchuri" / "backend" / "api"
    endpoints: list[Endpoint] = []

    for path in sorted(api_root.rglob("*Controller.java")):
        text = path.read_text(encoding="utf-8")

        class_match = re.search(r"\bclass\s+\w+", text)
        class_prefix = text[: class_match.start()] if class_match else text
        request_mappings = list(re.finditer(r"@RequestMapping\s*\((.*?)\)", class_prefix, re.S))
        base = normalize_path(extract_annotation_value(request_mappings[-1].group(0))) if request_mappings else ""

        pattern = re.compile(r"@(GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping)\s*(\((.*?)\))?", re.S)
        for match in pattern.finditer(text):
            annotation_name = match.group(1)
            annotation_text = match.group(0)
            method_path = normalize_path(extract_annotation_value(annotation_text))
            full_path = normalize_path(base + ("" if method_path == "/" else method_path))

            if not full_path.startswith("/api/v1/") and full_path != "/api/v1":
                continue

            endpoints.append(
                Endpoint(
                    method=HTTP_MAPPING[annotation_name],
                    path=full_path,
                    source=path.relative_to(root),
                    line=line_number(text, match.start()),
                )
            )

    openapi_config = root / "backend" / "src" / "main" / "java" / "matchuri" / "backend" / "global" / "config" / "OpenApiConfig.java"
    if openapi_config.exists():
        text = openapi_config.read_text(encoding="utf-8")
        synthetic_pattern = re.compile(
            r'\.path\s*\(\s*"([^"]+)"\s*,\s*new\s+PathItem\s*\(\)\s*\.\s*(get|post|put|patch|delete)\s*\(',
            re.S,
        )
        for match in synthetic_pattern.finditer(text):
            endpoints.append(
                Endpoint(
                    method=match.group(2).upper(),
                    path=normalize_path(match.group(1)),
                    source=openapi_config.relative_to(root),
                    line=line_number(text, match.start()),
                )
            )

    return endpoints


def parse_status_rows(root: Path) -> list[StatusRow]:
    status_path = root / "docs" / "api" / "api-status.md"
    rows: list[StatusRow] = []
    if not status_path.exists():
        return rows

    for line_no, line in enumerate(status_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.startswith("| `"):
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue

        api_id = cells[0].strip("`")
        method = cells[2].upper()
        endpoint_path = cells[3].strip("`")
        status = cells[4].strip("`")
        if not endpoint_path.startswith("/api/"):
            continue

        rows.append(
            StatusRow(
                api_id=api_id,
                domain=cells[1],
                method=method,
                path=normalize_path(endpoint_path),
                status=status,
                source_line=line_no,
            )
        )

    return rows


def frontend_api_dirs(root: Path) -> list[Path]:
    features = root / "frontend" / "src" / "features"
    if not features.exists():
        return []
    return sorted(
        path.relative_to(root)
        for path in features.rglob("infrastructure/api")
        if path.is_dir()
    )


def report(root: Path) -> tuple[str, bool]:
    endpoints = parse_backend_endpoints(root)
    rows = parse_status_rows(root)

    endpoint_keys = {(item.method, item.path) for item in endpoints}
    row_keys = {(item.method, item.path) for item in rows if item.status != "planned"}

    duplicate_rows: dict[tuple[str, str], list[StatusRow]] = {}
    for row in rows:
        duplicate_rows.setdefault((row.method, row.path), []).append(row)
    duplicate_rows = {key: value for key, value in duplicate_rows.items() if len(value) > 1}

    missing_status = [item for item in endpoints if (item.method, item.path) not in row_keys]
    stale_status = [
        row for row in rows
        if row.status not in {"planned", "deprecated"} and (row.method, row.path) not in endpoint_keys
    ]

    lines = [
        "# API Contract Audit",
        "",
        f"- Backend `/api/v1` endpoints: {len(endpoints)}",
        f"- API status rows: {len(rows)}",
        f"- Duplicate status keys: {len(duplicate_rows)}",
        f"- Backend endpoints missing status row: {len(missing_status)}",
        f"- Status rows not found in backend mappings: {len(stale_status)}",
        f"- Frontend API directories: {len(frontend_api_dirs(root))}",
        "",
    ]

    if duplicate_rows:
        lines.extend(["## Duplicate Status Rows", "", "| Method | Path | Lines |", "| --- | --- | ---: |"])
        for (method, path), dupes in sorted(duplicate_rows.items()):
            lines.append(f"| {method} | `{path}` | {', '.join(str(item.source_line) for item in dupes)} |")
        lines.append("")

    if missing_status:
        lines.extend(["## Backend Endpoints Missing Status Row", "", "| Method | Path | Source |", "| --- | --- | --- |"])
        for item in missing_status:
            lines.append(f"| {item.method} | `{item.path}` | `{item.source.as_posix()}:{item.line}` |")
        lines.append("")

    if stale_status:
        lines.extend(["## Status Rows Not Found In Backend Mappings", "", "| Method | Path | Status line | API ID |", "| --- | --- | ---: | --- |"])
        for item in stale_status:
            lines.append(f"| {item.method} | `{item.path}` | {item.source_line} | `{item.api_id}` |")
        lines.append("")

    api_dirs = frontend_api_dirs(root)
    if api_dirs:
        lines.extend(["## Frontend API Directories", ""])
        lines.extend(f"- `{path.as_posix()}`" for path in api_dirs)
        lines.append("")

    has_findings = bool(duplicate_rows or missing_status or stale_status)
    return "\n".join(lines), has_findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when drift is found")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output, has_findings = report(root)
    print(output)

    if args.strict and has_findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
