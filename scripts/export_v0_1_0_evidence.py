#!/usr/bin/env python3
"""Export a sanitized raw evidence bundle for the Millrace Rust v0.1.0 proof."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import re
import tarfile
from pathlib import Path


INCLUDE_GLOBS = (
    "Cargo.toml",
    "Cargo.lock",
    "README.md",
    "ideas/inbox/*.md",
    "millrace-agents/arbiter/contracts/ideas/*.md",
    "millrace-agents/arbiter/contracts/root-specs/*.md",
    "millrace-agents/arbiter/reports/*.md",
    "millrace-agents/arbiter/rubrics/*.md",
    "millrace-agents/arbiter/targets/*.json",
    "millrace-agents/arbiter/verdicts/*.json",
    "millrace-agents/incidents/resolved/*.md",
    "millrace-agents/learning/requests/blocked/*.md",
    "millrace-agents/logs/runtime_events.jsonl",
    "millrace-agents/tasks/done/*.md",
    "millrace-agents/specs/done/*.md",
    "millrace-agents/runs/run-*/stage_results/*.json",
    "millrace-agents/runs/run-*/runner_events.request-*.jsonl",
    "millrace-agents/runs/run-*/runner_completion.request-*.json",
)

DOCS_REPO_FILES = (
    ("docs/rust-efficacy-run.md", "RUST_EFFICACY_RUN.md"),
    ("docs/rust-port-roadmap.md", "docs/rust-port-roadmap.md"),
    (
        "docs/v0.1.0-autonomous-build-proof.md",
        "docs/v0.1.0-autonomous-build-proof.md",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("../millrace-rs"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/v0.1.0-port-evidence.tar.gz"),
    )
    return parser.parse_args()


def collect_files(source: Path) -> list[Path]:
    paths: set[Path] = set()
    for pattern in INCLUDE_GLOBS:
        for path in source.glob(pattern):
            if path.is_file():
                paths.add(path)
    return sorted(paths, key=lambda path: path.relative_to(source).as_posix())


def sanitize_text_payload(text: str) -> str:
    path_replacements = (
        (re.compile(r"C:\\Users\\[^\\\s\"']+"), "<WINDOWS_USER_HOME>"),
        (
            re.compile(r"/home/[^/\s\"'\\]+/\.venvs/millrace-py-0\.16\.1"),
            "<MILLRACE_PY_VENV>",
        ),
        (re.compile(r"/home/[^/\s\"'\\]+/\.local/bin"), "<HOME_BIN>"),
        (re.compile(r"/home/[^/\s\"'\\]+"), "<HOME>"),
        (re.compile(r"/mnt/[a-z]/_Millrace/millrace-rs-port-docs"), "<MILLRACE_RS_PORT_DOCS>"),
        (re.compile(r"/mnt/[a-z]/_Millrace/millrace-rs"), "<MILLRACE_RS>"),
        (re.compile(r"/mnt/[a-z]/_Millrace/millrace-py"), "<MILLRACE_PY>"),
        (re.compile(r"/mnt/[a-z]/_Millrace"), "<WORKSPACE_ROOT>"),
    )
    for pattern, replacement in path_replacements:
        text = pattern.sub(replacement, text)

    text = re.sub(
        r"((?:local|sanitized) raw evidence export contains \d+ files and has SHA256:"
        r"\n\n```text\n)[0-9a-f]{64}(\n```)",
        r"\1<BUNDLE_SHA256>\2",
        text,
    )

    redactions = (
        (re.compile(r"(?i)(set-cookie\s*:\s*)[^\r\n\\\"]+"), r"\1<REDACTED>"),
        (re.compile(r"(?i)(cookie\s*:\s*)[^\r\n\\\"]+"), r"\1<REDACTED>"),
        (re.compile(r"(?i)(authorization\s*:\s*)[^\r\n\\\"]+"), r"\1<REDACTED>"),
        (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-+/=]{8,}"), "Bearer <REDACTED>"),
        (re.compile(r"(?i)(x-oai-request-id\s*:\s*)[^\r\n\\\"]+"), r"\1<REDACTED>"),
        (
            re.compile(r"(https://a\.nel\.cloudflare\.com/report/v4\?s=)[^\"'\s\\,}]+"),
            r"\1<REDACTED>",
        ),
        (
            re.compile(
                r"(?i)([?&](?:access_token|api_key|client_secret|code|id_token|"
                r"key|refresh_token|secret|sig|signature|token)=)[^&\"'\s\\,}]+"
            ),
            r"\1<REDACTED>",
        ),
        (
            re.compile(
                r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|"
                r"id[_-]?token|client_secret|password|passwd|secret)\s*[:=]\s*"
                r"[\"']?[^\"'\s,;\\]+"
            ),
            r"\1=<REDACTED>",
        ),
    )
    for pattern, replacement in redactions:
        text = pattern.sub(replacement, text)
    return text


def sanitize_bytes(data: bytes) -> bytes:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return sanitize_text_payload(text).encode("utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_file(archive: tarfile.TarFile, source: Path, path: Path, prefix: str) -> None:
    relative = path.relative_to(source).as_posix()
    add_bytes(archive, sanitize_bytes(path.read_bytes()), f"{prefix}/{relative}")


def add_bytes(archive: tarfile.TarFile, data: bytes, arcname: str) -> None:
    info = tarfile.TarInfo(arcname)
    info.size = len(data)
    info.mtime = 0
    info.mode = 0o644
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, io.BytesIO(data))


def add_docs_repo_file(
    archive: tarfile.TarFile,
    docs_root: Path,
    source_relative: str,
    bundle_relative: str,
    prefix: str,
) -> None:
    path = docs_root / source_relative
    if path.is_file():
        add_bytes(archive, sanitize_bytes(path.read_bytes()), f"{prefix}/{bundle_relative}")


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    docs_root = Path(__file__).resolve().parents[1]
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    files = collect_files(source)
    prefix = "v0.1.0-port-evidence"

    raw_buffer = io.BytesIO()
    added_files = 0
    with tarfile.open(fileobj=raw_buffer, mode="w") as archive:
        for path in files:
            add_file(archive, source, path, prefix)
            added_files += 1
        for source_relative, bundle_relative in DOCS_REPO_FILES:
            before = raw_buffer.tell()
            add_docs_repo_file(archive, docs_root, source_relative, bundle_relative, prefix)
            if raw_buffer.tell() != before:
                added_files += 1
        for path in sorted((docs_root / "docs/seeded-ideas").glob("*.md")):
            bundle_relative = f"docs/millrace-ideas/{path.name}"
            add_bytes(archive, sanitize_bytes(path.read_bytes()), f"{prefix}/{bundle_relative}")
            added_files += 1

    with output.open("wb") as handle:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=handle,
            mtime=0,
            compresslevel=9,
        ) as gzip_file:
            gzip_file.write(raw_buffer.getvalue())

    digest = file_sha256(output)
    print(f"bundle: {output}")
    print(f"files: {added_files}")
    print(f"sha256: {digest}")


if __name__ == "__main__":
    main()
