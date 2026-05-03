#!/usr/bin/env python3
"""Verify v0.1.0 proof metrics against raw Millrace evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
from pathlib import Path

from generate_v0_1_0_metrics import compute_metrics


COMPARE_KEYS = (
    "summary",
    "usage_totals",
    "artifact_counts",
    "stage_counts",
    "terminal_counts",
    "result_class_counts",
    "usage_by_stage",
    "usage_by_plane",
    "slice_summaries",
    "seeded_ideas",
    "done_specs",
    "done_tasks",
    "resolved_incidents",
    "stages_without_usage",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--source", type=Path)
    source.add_argument("--bundle", type=Path)
    parser.add_argument(
        "--expected",
        type=Path,
        default=Path("evidence/v0.1.0/generated/metrics.json"),
    )
    parser.add_argument("--sha256")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_extract(bundle: Path, target: Path) -> Path:
    with tarfile.open(bundle, "r:*") as archive:
        members = archive.getmembers()
        for member in members:
            destination = (target / member.name).resolve()
            if not str(destination).startswith(str(target.resolve())):
                raise ValueError(f"unsafe tar path: {member.name}")
        archive.extractall(target)

    candidates = [path for path in target.iterdir() if path.is_dir()]
    if len(candidates) == 1:
        return candidates[0]
    return target


def compare(expected: dict, actual: dict) -> list[str]:
    failures = []
    for key in COMPARE_KEYS:
        if expected.get(key) != actual.get(key):
            failures.append(key)
    return failures


def main() -> None:
    args = parse_args()
    temp_dir = None
    source = args.source

    if args.bundle:
        if args.sha256:
            actual_hash = sha256(args.bundle)
            if actual_hash != args.sha256:
                raise SystemExit(
                    f"bundle sha256 mismatch: expected {args.sha256}, got {actual_hash}"
                )
        temp_dir = Path(tempfile.mkdtemp(prefix="millrace-rs-proof-"))
        source = safe_extract(args.bundle, temp_dir)

    try:
        expected = json.loads(args.expected.read_text(encoding="utf-8"))
        actual = compute_metrics(source)
        failures = compare(expected, actual)
        if failures:
            print("verification: failed")
            for key in failures:
                print(f"mismatch: {key}")
            raise SystemExit(1)
        print("verification: ok")
        print(f"stage_results: {actual['summary']['stage_result_count']}")
        print(f"runs: {actual['summary']['run_count']}")
        print(f"input_tokens: {actual['usage_totals']['input_tokens']}")
        print(f"cached_input_tokens: {actual['usage_totals']['cached_input_tokens']}")
        print(f"output_tokens: {actual['usage_totals']['output_tokens']}")
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
