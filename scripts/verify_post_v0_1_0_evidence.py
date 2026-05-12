#!/usr/bin/env python3
"""Verify sanitized post-v0.1.0 Millrace Rust port evidence bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tarfile
import tempfile
from pathlib import Path


SUSPICIOUS_PATTERNS = (
    ("windows_user_home", re.compile(r"C:\\Users\\", re.IGNORECASE)),
    ("windows_workspace_root", re.compile(r"F:[\\/]+_Millrace", re.IGNORECASE)),
    ("wsl_workspace_root", re.compile(r"/mnt/[a-z]/_Millrace", re.IGNORECASE)),
    ("linux_home", re.compile(r"/home/[A-Za-z0-9_.-]+")),
    ("authorization_header", re.compile(r"(?i)authorization\s*:\s*(?!<REDACTED>)\S+")),
    ("cookie_header", re.compile(r"(?i)(set-cookie|cookie)\s*:\s*(?!<REDACTED>)\S+")),
    ("bearer_token", re.compile(r"(?i)\bBearer\s+(?!<REDACTED>)[A-Za-z0-9._\-+/=]{8,}")),
    (
        "secret_assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|"
            r"id[_-]?token|client_secret|password|passwd|secret)\s*[:=]\s*"
            r"(?!<REDACTED>)\S+"
        ),
    ),
)


BLOCKED_BUNDLE_PATH_PATTERNS = (
    re.compile(r"(^|/)runner_(events|prompt|stdout|stderr|last_message|completion|invocation)\."),
    re.compile(r"(^|/)logs/"),
    re.compile(r"\.env$"),
    re.compile(r"\.pyc$"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--sha256")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
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
    if len(candidates) != 1:
        raise ValueError("bundle must contain one top-level evidence directory")
    return candidates[0]


def scan_file(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    issues = []
    for name, pattern in SUSPICIOUS_PATTERNS:
        match = pattern.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            issues.append({"path": str(path), "pattern": name, "line": line})
    return issues


def verify_manifest(root: Path) -> dict:
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("missing manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    listed = manifest.get("source_files", []) + manifest.get("generated_files", [])
    for item in listed:
        relative = item["path"].split("/", 1)[1]
        path = root / relative
        if not path.is_file():
            raise ValueError(f"listed file missing from bundle: {item['path']}")
        digest = sha256_file(path)
        if digest != item["sha256"]:
            raise ValueError(f"sha256 mismatch for {item['path']}: {digest}")
    return manifest


def main() -> None:
    args = parse_args()
    version = args.version.removeprefix("v")
    if args.sha256:
        actual = sha256_file(args.bundle)
        if actual != args.sha256:
            raise SystemExit(f"bundle sha256 mismatch: expected {args.sha256}, got {actual}")

    temp_dir = Path(tempfile.mkdtemp(prefix="millrace-rs-post-proof-"))
    try:
        root = safe_extract(args.bundle, temp_dir)
        expected_name = f"v{version}-port-evidence"
        if root.name != expected_name:
            raise ValueError(f"unexpected top-level directory {root.name}; expected {expected_name}")

        required = (
            "README.md",
            "manifest.json",
            "generated/metrics.json",
            "generated/stage-summary.csv",
            "generated/run-summary.csv",
            "generated/sanitizer-review.json",
        )
        for relative in required:
            if not (root / relative).is_file():
                raise ValueError(f"missing required file: {relative}")

        manifest = verify_manifest(root)
        release = manifest.get("release", {})
        if release.get("rust_version") != version:
            raise ValueError(f"manifest version mismatch: {release.get('rust_version')}")
        if manifest.get("arbiter", {}).get("verdict") != "complete":
            raise ValueError("Arbiter verdict is not complete")
        if manifest.get("metrics", {}).get("summary", {}).get("stage_result_count", 0) <= 0:
            raise ValueError("no selected stage results recorded")

        review = json.loads((root / "generated/sanitizer-review.json").read_text(encoding="utf-8"))
        if review.get("issue_count") != 0:
            raise ValueError(f"sanitizer review reports issues: {review.get('issues')}")

        issues = []
        for path in sorted(root.rglob("*")):
            if path.is_file():
                issues.extend(scan_file(path))
        if issues:
            raise ValueError(f"post-extract sanitizer scan failed: {issues[:3]}")

        print("verification: ok")
        print(f"version: v{version}")
        print(f"files: {manifest.get('bundle_file_count')}")
        print(f"stage_results: {manifest['metrics']['summary']['stage_result_count']}")
        print(f"runs: {manifest['metrics']['summary']['run_count']}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
