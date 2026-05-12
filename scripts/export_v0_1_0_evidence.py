#!/usr/bin/env python3
"""Export a sanitized public evidence bundle for the Millrace Rust v0.1.0 proof."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path


TAG_SNAPSHOT_PATHS = (
    "Cargo.toml",
    "Cargo.lock",
    "README.md",
    "docs/rust-port-roadmap.md",
    "docs/testing.md",
)

DOCS_REPO_FILES = (
    ("evidence/v0.1.0/README.md", "evidence/v0.1.0/README.md"),
    ("evidence/v0.1.0/generated/checksums.sha256", "evidence/v0.1.0/generated/checksums.sha256"),
    ("evidence/v0.1.0/generated/metrics.json", "evidence/v0.1.0/generated/metrics.json"),
    ("evidence/v0.1.0/generated/slice-summary.csv", "evidence/v0.1.0/generated/slice-summary.csv"),
    ("evidence/v0.1.0/generated/stage-summary.csv", "evidence/v0.1.0/generated/stage-summary.csv"),
    ("docs/how-to-verify.md", "docs/how-to-verify.md"),
    ("docs/limitations.md", "docs/limitations.md"),
    ("docs/rust-efficacy-run.md", "RUST_EFFICACY_RUN.md"),
    ("docs/rust-port-roadmap.md", "docs/rust-port-roadmap.md"),
    (
        "docs/v0.1.0-autonomous-build-proof.md",
        "docs/v0.1.0-autonomous-build-proof.md",
    ),
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
    (
        "secret_assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|"
            r"id[_-]?token|client_secret|password|passwd|secret)\s*[:=]\s*"
            r"(?!<REDACTED>)\S+"
        ),
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


def collect_files(source: Path, docs_root: Path) -> list[Path]:
    metrics = json.loads(
        (docs_root / "evidence/v0.1.0/generated/metrics.json").read_text(encoding="utf-8")
    )
    first_started = parse_timestamp(metrics["summary"].get("first_started_at"))
    last_completed = parse_timestamp(metrics["summary"].get("last_completed_at"))
    paths: set[Path] = set()
    for item in metrics["seeded_ideas"]:
        add_relative_path(paths, source, item["path"])
    for key in ("done_specs", "done_tasks", "resolved_incidents"):
        for relative in metrics[key]:
            add_relative_path(paths, source, relative)

    idea_ids = [Path(item["path"]).stem for item in metrics["seeded_ideas"]]
    for idea_id in idea_ids:
        for relative in (
            f"millrace-agents/arbiter/contracts/ideas/{idea_id}.md",
            f"millrace-agents/arbiter/contracts/root-specs/{idea_id}.md",
            f"millrace-agents/arbiter/rubrics/{idea_id}.md",
            f"millrace-agents/arbiter/targets/{idea_id}.json",
            f"millrace-agents/arbiter/verdicts/{idea_id}.json",
        ):
            add_relative_path(paths, source, relative)

    selected_stage_results = []
    for path in source.glob("millrace-agents/runs/run-*/stage_results/*.json"):
        try:
            stage = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        started = parse_timestamp(stage.get("started_at"))
        completed = parse_timestamp(stage.get("completed_at"))
        if first_started and started and started < first_started:
            continue
        if last_completed and completed and completed > last_completed:
            continue
        selected_stage_results.append((path, stage))
        paths.add(path)

    for _, stage in selected_stage_results:
        if stage.get("stage") == "arbiter" and isinstance(stage.get("run_id"), str):
            add_relative_path(paths, source, f"millrace-agents/arbiter/reports/{stage['run_id']}.md")

    for path in source.glob("millrace-agents/learning/requests/blocked/*.md"):
        created = created_at_from_markdown(path)
        if last_completed and created and created <= last_completed:
            paths.add(path)
    return sorted(paths, key=lambda path: path.relative_to(source).as_posix())


def add_relative_path(paths: set[Path], source: Path, relative: str) -> None:
    path = source / relative
    if path.is_file():
        paths.add(path)


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def created_at_from_markdown(path: Path) -> datetime | None:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("Created-At:"):
            return parse_timestamp(line.split(":", 1)[1].strip())
    return None


def sanitize_text_payload(text: str) -> str:
    path_replacements = (
        (re.compile(r"F:\\_Millrace\\millrace-rs-port-docs", re.IGNORECASE), "<MILLRACE_RS_PORT_DOCS>"),
        (re.compile(r"F:\\_Millrace\\millrace-rs", re.IGNORECASE), "<MILLRACE_RS>"),
        (re.compile(r"F:\\_Millrace\\millrace-py", re.IGNORECASE), "<MILLRACE_PY>"),
        (re.compile(r"F:\\_Millrace", re.IGNORECASE), "<WORKSPACE_ROOT>"),
        (re.compile(r"F:/_Millrace/millrace-rs-port-docs", re.IGNORECASE), "<MILLRACE_RS_PORT_DOCS>"),
        (re.compile(r"F:/_Millrace/millrace-rs", re.IGNORECASE), "<MILLRACE_RS>"),
        (re.compile(r"F:/_Millrace/millrace-py", re.IGNORECASE), "<MILLRACE_PY>"),
        (re.compile(r"F:/_Millrace", re.IGNORECASE), "<WORKSPACE_ROOT>"),
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
        (re.compile(r"DESKTOP-[A-Za-z0-9-]+", re.IGNORECASE), "<DESKTOP_HOST>"),
    )
    for pattern, replacement in path_replacements:
        text = pattern.sub(replacement, text)

    text = re.sub(
        r"((?:local|sanitized|public) (?:raw )?evidence (?:export|bundle) contains \d+ files and has SHA256:"
        r"\n\n```text\n)[0-9a-f]{64}(\n```)",
        r"\1<BUNDLE_SHA256>\2",
        text,
    )
    text = re.sub(r"(- SHA256: `)[0-9a-f]{64}(`)", r"\1<BUNDLE_SHA256>\2", text)
    text = re.sub(r"(--sha256\s+)[0-9a-f]{64}", r"\1<BUNDLE_SHA256>", text)

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
    assert_allowed_bundle_path(arcname)
    data = sanitize_bytes(data)
    issues = scan_payload(arcname, data)
    if issues:
        raise SystemExit(f"sanitizer review failed for {arcname}: {issues[:3]}")
    info = tarfile.TarInfo(arcname)
    info.size = len(data)
    info.mtime = 0
    info.mode = 0o644
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, io.BytesIO(data))


def assert_allowed_bundle_path(arcname: str) -> None:
    for pattern in BLOCKED_BUNDLE_PATH_PATTERNS:
        if pattern.search(arcname):
            raise SystemExit(f"blocked bundle path: {arcname}")


def scan_payload(arcname: str, data: bytes) -> list[dict[str, object]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []
    issues = []
    for name, pattern in SUSPICIOUS_PATTERNS:
        match = pattern.search(text)
        if match:
            issues.append({"path": arcname, "pattern": name, "line": text.count("\n", 0, match.start()) + 1})
    return issues


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


def run_git_show(source: Path, tag: str, relative: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{tag}:{relative}"],
        cwd=source,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    docs_root = Path(__file__).resolve().parents[1]
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    files = collect_files(source, docs_root)
    prefix = "v0.1.0-port-evidence"

    raw_buffer = io.BytesIO()
    added_files = 0
    with tarfile.open(fileobj=raw_buffer, mode="w") as archive:
        for path in files:
            add_file(archive, source, path, prefix)
            added_files += 1
        for relative in TAG_SNAPSHOT_PATHS:
            data = run_git_show(source, "v0.1.0", relative)
            if data is not None:
                add_bytes(archive, data, f"{prefix}/release-tag/v0.1.0/{relative}")
                added_files += 1
        for source_relative, bundle_relative in DOCS_REPO_FILES:
            before = raw_buffer.tell()
            add_docs_repo_file(archive, docs_root, source_relative, bundle_relative, prefix)
            if raw_buffer.tell() != before:
                added_files += 1
        for path in sorted((docs_root / "docs/seeded-ideas").glob("*.md")):
            bundle_relative = f"docs/millrace-ideas/{path.name}"
            add_bytes(archive, path.read_bytes(), f"{prefix}/{bundle_relative}")
            added_files += 1

        review = {
            "schema_version": "1.0",
            "kind": "sanitizer_review",
            "release": "v0.1.0",
            "blocked_file_classes": [
                "raw runner prompts",
                "raw runner stdout/stderr",
                "runner event jsonl streams",
                "runner completion/invocation payloads",
                "process env dumps",
                "daemon logs",
                "pycache artifacts",
            ],
            "issue_count": 0,
            "issues": [],
        }
        add_bytes(
            archive,
            json.dumps(review, indent=2, sort_keys=True).encode("utf-8") + b"\n",
            f"{prefix}/generated/sanitizer-review.json",
        )
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
