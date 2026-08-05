#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Audit a WESAD archive or extracted directory before preprocessing."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


def audit_archive(path: Path) -> dict[str, object]:
    result: dict[str, object] = {
        "path": str(path.resolve()),
        "kind": "zip",
        "exists": path.is_file(),
        "valid": False,
        "size_bytes": path.stat().st_size if path.is_file() else 0,
        "subject_pickles": [],
        "error": None,
    }
    if not path.is_file():
        result["error"] = "Archive does not exist"
        return result
    try:
        with zipfile.ZipFile(path) as archive:
            bad_member = archive.testzip()
            subject_pickles = sorted(
                name
                for name in archive.namelist()
                if name.count("/") >= 2 and name.endswith(".pkl") and "/S" in name
            )
            result["subject_pickles"] = subject_pickles
            if bad_member:
                result["error"] = f"CRC failure: {bad_member}"
            elif not subject_pickles:
                result["error"] = "No subject pickle files found"
            else:
                result["valid"] = True
    except (zipfile.BadZipFile, OSError) as error:
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def audit_directory(path: Path) -> dict[str, object]:
    subject_pickles = sorted(str(item.relative_to(path)) for item in path.glob("S*/S*.pkl"))
    return {
        "path": str(path.resolve()),
        "kind": "directory",
        "exists": path.is_dir(),
        "valid": bool(subject_pickles),
        "size_bytes": None,
        "subject_pickles": subject_pickles,
        "error": None if subject_pickles else "No files matching S*/S*.pkl",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = audit_directory(args.path) if args.path.is_dir() else audit_archive(args.path)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(text, encoding="utf-8")
    raise SystemExit(0 if result["valid"] else 2)


if __name__ == "__main__":
    main()
