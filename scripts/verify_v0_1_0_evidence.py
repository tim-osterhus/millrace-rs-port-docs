#!/usr/bin/env python3
"""Verify v0.1.0 proof metrics or a sanitized public evidence bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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

BLOCKED_BUNDLE_PATH_PATTERNS = (
    re.compile(r"(^|/)runner_(events|prompt|stdout|stderr|last_message|completion|invocation)\."),
    re.compile(r"(^|/)logs/"),
    re.compile(r"\.env$"),
    re.compile(r"\.pyc$"),
)

SUSPICIOUS_PATTERNS = (
    ("windows_user_home", re.compile(r"C:\\Users\\", re.IGNORECASE)),
    ("windows_workspace_root", re.compile(r"F:[\\/]+_Millrace", re.IGNORECASE)),
    ("wsl_workspace_root", re.compile(r"/mnt/[a-z]/_Millrace", re.IGNORECASE)),
    ("linux_home", re.compile(r"/home/[A-Za-z0-9_.-]+")),
    ("desktop_hostname", re.compile(r"DESKTOP-[A-Za-z0-9-]+", re.IGNORECASE)),
    ("authorization_header", re.compile(r"(?i)authorization\s*:\s*(?!<REDACTED>)\S+")),
    ("cookie_header", re.compile(r"(?i)(set-cookie|cookie)\s*:\s*(?!<REDACTED>)\S+")),
    ("bearer_token", re.compile(r"(?i)\bBearer\s+(?!<REDACTED>)[A-Za-z0-9._\-+/=]{8,}")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9][A-Za-z0-9_-]{20,}")),
    ("github_token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}")),
    ("huggingface_token", re.compile(r"\bhf_[A-Za-z0-9]{20,}")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
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
            for pattern in BLOCKED_BUNDLE_PATH_PATTERNS:
                if pattern.search(member.name):
                    raise ValueError(f"blocked bundle path: {member.name}")
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


def scan_file(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    issues = []
    for name, pattern in SUSPICIOUS_PATTERNS:
        match = pattern.search(text)
        if match:
            issues.append({"path": str(path), "pattern": name, "line": text.count("\n", 0, match.start()) + 1})
    return issues


def verify_sanitized_bundle(root: Path, expected: dict) -> dict:
    embedded = root / "evidence" / "v0.1.0" / "generated" / "metrics.json"
    if not embedded.is_file():
        raise ValueError("sanitized bundle is missing evidence/v0.1.0/generated/metrics.json")
    embedded_metrics = json.loads(embedded.read_text(encoding="utf-8"))
    failures = compare(expected, embedded_metrics)
    if failures:
        raise ValueError(f"embedded metrics mismatch: {', '.join(failures)}")

    review = root / "generated" / "sanitizer-review.json"
    if not review.is_file():
        raise ValueError("sanitized bundle is missing generated/sanitizer-review.json")
    review_payload = json.loads(review.read_text(encoding="utf-8"))
    if review_payload.get("issue_count") != 0:
        raise ValueError(f"sanitizer review reports issues: {review_payload.get('issues')}")

    issues = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            issues.extend(scan_file(path))
    if issues:
        raise ValueError(f"post-extract sanitizer scan failed: {issues[:3]}")

    stage_results = len(list(root.glob("millrace-agents/runs/run-*/stage_results/*.json")))
    if stage_results != expected["summary"]["stage_result_count"]:
        raise ValueError(
            f"stage result count mismatch: expected {expected['summary']['stage_result_count']}, got {stage_results}"
        )
    return embedded_metrics


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
        runner_events = list(source.glob("millrace-agents/runs/run-*/runner_events.request-*.jsonl"))
        if args.bundle and not runner_events:
            actual = verify_sanitized_bundle(source, expected)
        else:
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
