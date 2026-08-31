#!/usr/bin/env python3
"""Write a Base64-encoded GitHub PR body to a UTF-8 temporary Markdown file."""

from __future__ import annotations

import argparse
import base64
import binascii
import os
from pathlib import Path
import tempfile


def decode_body(encoded: str) -> str:
    try:
        raw = base64.b64decode(encoded, validate=True)
        body = raw.decode("utf-8")
    except (binascii.Error, UnicodeDecodeError) as exc:
        raise ValueError("PR body must be valid Base64-encoded UTF-8") from exc
    if not body.strip():
        raise ValueError("PR body must not be empty")
    return body


def write_temp_body(body: str, directory: Path | None = None) -> Path:
    if directory is not None:
        directory = directory.resolve()
        if not directory.is_dir():
            raise ValueError(f"Temporary directory does not exist: {directory}")

    descriptor, raw_path = tempfile.mkstemp(
        prefix="matchuri-pr-",
        suffix=".md",
        dir=directory,
        text=True,
    )
    path = Path(raw_path).resolve()
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(body)
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--body-base64", required=True)
    parser.add_argument("--directory", type=Path)
    args = parser.parse_args()

    print(write_temp_body(decode_body(args.body_base64), args.directory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
