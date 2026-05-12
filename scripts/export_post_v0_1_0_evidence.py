#!/usr/bin/env python3
"""Export sanitized evidence bundles for post-v0.1.0 Millrace Rust releases."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import subprocess
import tarfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


USAGE_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


@dataclass(frozen=True)
class Release:
    version: str
    python_from: str
    python_to: str
    python_commit: str
    task_slug: str

    @property
    def tag(self) -> str:
        return f"v{self.version}"

    @property
    def prefix(self) -> str:
        return f"v{self.version}-port-evidence"

    @property
    def idea_stem(self) -> str:
        return f"auto-port-python-{self.python_from}-to-{self.python_to}-rust-{self.version}"

    @property
    def idea_id(self) -> str:
        return f"idea-{self.idea_stem}"

    @property
    def fixture_slug(self) -> str:
        return self.python_to.replace(".", "_")


RELEASES: tuple[Release, ...] = (
    Release(
        version="0.2.0",
        python_from="v0.16.1",
        python_to="v0.17.3",
        python_commit="a0d6b1bd5b71284eab7e9a5dcc9f76cee6580aaf",
        task_slug="0-17-3",
    ),
    Release(
        version="0.2.1",
        python_from="v0.17.3",
        python_to="v0.17.4",
        python_commit="304e537964ff772c815689b87e4c1e3b805c656c",
        task_slug="0-17-4",
    ),
    Release(
        version="0.3.0",
        python_from="v0.17.4",
        python_to="v0.18.0",
        python_commit="e4ccf099c8345a8b8708cdaa1ac510bdc7851387",
        task_slug="0-18-0",
    ),
    Release(
        version="0.3.1",
        python_from="v0.18.0",
        python_to="v0.18.1",
        python_commit="0396c7852793b212d31345862b38a7d6f3f02854",
        task_slug="0-18-1",
    ),
    Release(
        version="0.3.2",
        python_from="v0.18.1",
        python_to="v0.18.2",
        python_commit="5444cb9485ea90b67b2ed6ba7e0723ae9fe7b79f",
        task_slug="0-18-2",
    ),
)


TAG_SNAPSHOT_PATHS = (
    "Cargo.toml",
    "Cargo.lock",
    "CHANGELOG.md",
    "README.md",
    "ROADMAP.md",
    "docs/rust-port-roadmap.md",
    "docs/source-package-map.md",
    "docs/testing.md",
)


DOC_PATHS = (
    "CHANGELOG.md",
    "ROADMAP.md",
    "docs/rust-port-roadmap.md",
    "docs/source-package-map.md",
    "docs/testing.md",
)


SUMMARY_NAMES = (
    "analyst_summary.md",
    "arbiter_report.md",
    "auditor_summary.md",
    "builder_summary.md",
    "checker_expectations.md",
    "checker_summary.md",
    "curator_skill_update_summary.md",
    "doublecheck_summary.md",
    "fixer_summary.md",
    "manager_summary.md",
    "planner_summary.md",
    "recon_summary.md",
    "release_readiness_remediation.md",
    "troubleshooter_summary.md",
    "updater_summary.md",
)


BLOCKED_BUNDLE_PATH_PATTERNS = (
    re.compile(r"(^|/)runner_(events|prompt|stdout|stderr|last_message|completion|invocation)\."),
    re.compile(r"(^|/)logs/"),
    re.compile(r"\.env$"),
    re.compile(r"\.pyc$"),
)


REDACTION_PATTERNS = (
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
    (re.compile(r"(?i)(set-cookie\s*:\s*)[^\r\n\\\"]+"), r"\1<REDACTED>"),
    (re.compile(r"(?i)(cookie\s*:\s*)[^\r\n\\\"]+"), r"\1<REDACTED>"),
    (re.compile(r"(?i)(authorization\s*:\s*)[^\r\n\\\"]+"), r"\1<REDACTED>"),
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-+/=]{8,}"), "Bearer <REDACTED>"),
    (re.compile(r"(?i)(x-oai-request-id\s*:\s*)[^\r\n\\\"]+"), r"\1<REDACTED>"),
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("../millrace-rs"))
    parser.add_argument("--evidence-root", type=Path, default=Path("evidence"))
    parser.add_argument("--dist-root", type=Path, default=Path("dist"))
    parser.add_argument(
        "--versions",
        nargs="+",
        default=[release.version for release in RELEASES],
        help="Rust release versions to export, or 'all'.",
    )
    return parser.parse_args()


def selected_releases(values: list[str]) -> list[Release]:
    requested = {value.removeprefix("v") for value in values}
    if "all" in requested:
        return list(RELEASES)
    releases = {release.version: release for release in RELEASES}
    missing = sorted(requested - set(releases))
    if missing:
        raise SystemExit(f"unknown versions: {', '.join(missing)}")
    return [releases[version] for version in sorted(requested, key=lambda item: tuple(map(int, item.split('.'))))]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sanitize_text_payload(text: str) -> str:
    for pattern, replacement in REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def sanitize_bytes(data: bytes) -> bytes:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return sanitize_text_payload(text).encode("utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def format_seconds(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remainder = seconds % 60
    return f"{hours}h {minutes}m {remainder:.1f}s"


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def add_path(paths: set[Path], root: Path, relative: str) -> None:
    path = root / relative
    if path.is_file():
        paths.add(path)


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


def matching_stage_paths(source: Path, release: Release, verdict: dict | None) -> list[Path]:
    task_markers = [f"auto-port-{release.task_slug}"]
    if release.version == "0.2.0":
        task_markers.append("arbiter-remediation-auto-port-0-17-3")
    verdict_run = verdict.get("run_id") if verdict else None
    verdict_request = verdict.get("request_id") if verdict else None

    selected: list[Path] = []
    for path in sorted(source.glob("millrace-agents/runs/run-*/stage_results/*.json")):
        stage = read_json(path)
        work_item_id = str(stage.get("work_item_id") or "")
        run_id = stage.get("run_id")
        request_id = stage.get("request_id")
        metadata = stage.get("metadata")
        if isinstance(metadata, dict) and not request_id:
            request_id = metadata.get("request_id")
        if any(marker in work_item_id for marker in task_markers):
            selected.append(path)
        elif verdict_run and verdict_request and run_id == verdict_run and request_id == verdict_request:
            selected.append(path)
    return selected


def request_id_from_stage(stage: dict) -> str | None:
    metadata = stage.get("metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("request_id"), str):
        return metadata["request_id"]
    value = stage.get("request_id")
    return value if isinstance(value, str) else None


def collect_release_paths(source: Path, release: Release) -> tuple[set[Path], dict | None, list[Path]]:
    paths: set[Path] = set()
    for relative in DOC_PATHS:
        add_path(paths, source, relative)

    for relative in (
        f"ideas/inbox/{release.idea_stem}.md",
        f"millrace-agents/auto-port/generated/{release.idea_stem}.md",
        f"millrace-agents/arbiter/contracts/ideas/{release.idea_id}.md",
        f"millrace-agents/arbiter/contracts/root-specs/{release.idea_id}.md",
        f"millrace-agents/arbiter/rubrics/{release.idea_id}.md",
        f"millrace-agents/arbiter/targets/{release.idea_id}.json",
        f"millrace-agents/arbiter/verdicts/{release.idea_id}.json",
        f"millrace-agents/specs/done/{release.idea_id}.md",
    ):
        add_path(paths, source, relative)

    if release.version == "0.2.0":
        add_path(
            paths,
            source,
            "millrace-agents/specs/done/arbiter-remediation-auto-port-0-17-3-clippy-release-readiness.md",
        )

    for pattern in (
        f"millrace-agents/tasks/done/auto-port-{release.task_slug}-*.md",
        f"tests/fixtures/**/*.json",
    ):
        for path in source.glob(pattern):
            if path.is_file():
                if pattern.endswith("*.json") and f"auto_port_{release.fixture_slug}" not in path.name:
                    continue
                paths.add(path)

    if release.version == "0.2.0":
        for path in source.glob("millrace-agents/tasks/done/arbiter-remediation-auto-port-0-17-3-*.md"):
            if path.is_file():
                paths.add(path)
        for path in source.glob("millrace-agents/incidents/resolved/*auto-port*0-17-3*.md"):
            if path.is_file():
                paths.add(path)

    verdict_path = source / f"millrace-agents/arbiter/verdicts/{release.idea_id}.json"
    verdict = read_json(verdict_path) if verdict_path.is_file() else None
    if verdict:
        for relative in (
            verdict.get("report_path"),
            (source / f"millrace-agents/arbiter/reports/{verdict.get('run_id')}.md").relative_to(source).as_posix(),
        ):
            if isinstance(relative, str):
                add_path(paths, source, relative)

    target_path = source / f"millrace-agents/arbiter/targets/{release.idea_id}.json"
    if target_path.is_file():
        target = read_json(target_path)
        for key in ("latest_verdict_path", "latest_report_path", "root_spec_path", "root_idea_path", "rubric_path"):
            value = target.get(key)
            if isinstance(value, str):
                add_path(paths, source, value)

    stage_paths = matching_stage_paths(source, release, verdict)
    paths.update(stage_paths)
    selected_runs = {path.parent.parent for path in stage_paths}
    for run_dir in selected_runs:
        for name in SUMMARY_NAMES:
            path = run_dir / name
            if path.is_file():
                paths.add(path)
        for path in run_dir.glob("*release*readiness*.log"):
            if path.is_file():
                paths.add(path)

    return paths, verdict, stage_paths


def stage_metrics(source: Path, stage_paths: list[Path]) -> tuple[dict, list[dict], list[dict]]:
    stages = []
    for path in stage_paths:
        stage = read_json(path)
        stage["_path"] = rel(path, source)
        stages.append(stage)

    starts = [parse_timestamp(stage.get("started_at")) for stage in stages]
    ends = [parse_timestamp(stage.get("completed_at")) for stage in stages]
    starts = [value for value in starts if value is not None]
    ends = [value for value in ends if value is not None]
    durations = [float(stage.get("duration_seconds") or 0) for stage in stages]

    stage_counts = Counter()
    terminal_counts = Counter()
    result_class_counts = Counter()
    work_items = Counter()
    run_counts = Counter()
    request_ids = set()
    for stage in stages:
        plane = stage.get("plane") or "unknown"
        stage_name = stage.get("stage") or "unknown"
        terminal = stage.get("terminal_result") or "unknown"
        result_class = stage.get("result_class") or "unknown"
        work_item_id = stage.get("work_item_id") or "unknown"
        run_id = stage.get("run_id") or "unknown"
        request_id = request_id_from_stage(stage)
        if request_id:
            request_ids.add(request_id)
        stage_counts[f"{plane}/{stage_name}"] += 1
        terminal_counts[f"{stage_name}/{terminal}"] += 1
        result_class_counts[result_class] += 1
        work_items[work_item_id] += 1
        run_counts[run_id] += 1

    first_started = min(starts) if starts else None
    last_completed = max(ends) if ends else None
    wall_seconds = (
        (last_completed - first_started).total_seconds()
        if first_started and last_completed
        else 0.0
    )

    metrics = {
        "summary": {
            "run_count": len(run_counts),
            "stage_result_count": len(stages),
            "request_id_count": len(request_ids),
            "work_item_count": len(work_items),
            "first_started_at": first_started.isoformat() if first_started else None,
            "last_completed_at": last_completed.isoformat() if last_completed else None,
            "wall_seconds": round(wall_seconds, 6),
            "wall_hms": format_seconds(wall_seconds),
            "sum_stage_duration_seconds": round(sum(durations), 6),
            "sum_stage_duration_hms": format_seconds(sum(durations)),
        },
        "stage_counts": dict(sorted(stage_counts.items())),
        "terminal_counts": dict(sorted(terminal_counts.items())),
        "result_class_counts": dict(sorted(result_class_counts.items())),
        "work_item_stage_counts": dict(sorted(work_items.items())),
        "run_stage_counts": dict(sorted(run_counts.items())),
        "stage_results": [
            {
                "path": stage["_path"],
                "run_id": stage.get("run_id"),
                "request_id": request_id_from_stage(stage),
                "plane": stage.get("plane"),
                "stage": stage.get("stage"),
                "work_item_id": stage.get("work_item_id"),
                "terminal_result": stage.get("terminal_result"),
                "result_class": stage.get("result_class"),
                "duration_seconds": stage.get("duration_seconds"),
            }
            for stage in sorted(stages, key=lambda item: item["_path"])
        ],
    }

    stage_rows = []
    for key, count in sorted(stage_counts.items()):
        plane, stage = key.split("/", 1)
        stage_rows.append({"plane": plane, "stage": stage, "calls": count})

    run_rows = [
        {"run_id": run_id, "stage_results": count}
        for run_id, count in sorted(run_counts.items())
    ]
    return metrics, stage_rows, run_rows


def csv_bytes(rows: list[dict], fieldnames: tuple[str, ...]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def scan_payload(arcname: str, data: bytes) -> list[dict]:
    issues = []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return issues
    for name, pattern in SUSPICIOUS_PATTERNS:
        match = pattern.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            issues.append({"path": arcname, "pattern": name, "line": line})
    return issues


def assert_allowed_bundle_path(arcname: str) -> None:
    for pattern in BLOCKED_BUNDLE_PATH_PATTERNS:
        if pattern.search(arcname):
            raise ValueError(f"blocked bundle path: {arcname}")


def add_payload(payload: dict[str, bytes], arcname: str, data: bytes) -> None:
    assert_allowed_bundle_path(arcname)
    payload[arcname] = sanitize_bytes(data)


def build_readme(release: Release, manifest: dict, tarball_sha256: str | None = None) -> str:
    summary = manifest["metrics"]["summary"]
    sha_line = (
        f"- Tarball SHA256: `{tarball_sha256}`\n"
        if tarball_sha256
        else "- Tarball SHA256: recorded in `tarball.sha256` after export.\n"
    )
    return (
        f"# Millrace Rust v{release.version} Port Evidence\n\n"
        "This directory records sanitized public evidence metadata for the "
        f"Rust `millrace-ai` `{release.version}` port release.\n\n"
        "## Release\n\n"
        f"- Rust release: `v{release.version}`\n"
        f"- Python baseline: `{release.python_from}`\n"
        f"- Python target: `{release.python_to}` (`{release.python_commit}`)\n"
        f"- Auto-port idea: `{release.idea_id}`\n"
        f"- Evidence tarball: `dist/v{release.version}-port-evidence.tar.gz`\n"
        f"{sha_line}\n"
        "## Sanitized Contents\n\n"
        f"- Bundle payload files: {manifest['bundle_file_count']}\n"
        f"- Selected stage results: {summary['stage_result_count']}\n"
        f"- Selected runs: {summary['run_count']}\n"
        f"- Selected work items: {summary['work_item_count']}\n"
        f"- Arbiter verdict: `{manifest['arbiter'].get('verdict')}` / "
        f"`{manifest['arbiter'].get('terminal_result')}`\n\n"
        "The bundle intentionally excludes raw runner prompts, stdout/stderr, "
        "runner event streams, process env dumps, daemon logs, and pycache files.\n\n"
        "## Local Verification\n\n"
        "```bash\n"
        f"python scripts/verify_post_v0_1_0_evidence.py --version {release.version} "
        f"--bundle dist/v{release.version}-port-evidence.tar.gz\n"
        "```\n"
    )


def build_manifest(release: Release, payload: dict[str, bytes], metrics: dict, verdict: dict | None) -> dict:
    source_files = []
    generated_files = []
    for arcname, data in sorted(payload.items()):
        if arcname.endswith("/manifest.json"):
            continue
        item = {
            "path": arcname,
            "bytes": len(data),
            "sha256": sha256_bytes(data),
        }
        if "/generated/" in arcname or arcname.endswith("/README.md"):
            generated_files.append(item)
        else:
            source_files.append(item)

    return {
        "schema_version": "1.0",
        "kind": "post_v0_1_0_port_evidence_manifest",
        "created_at": metrics["summary"].get("last_completed_at") or "1970-01-01T00:00:00+00:00",
        "release": {
            "rust_version": release.version,
            "rust_tag": release.tag,
            "python_from": release.python_from,
            "python_to": release.python_to,
            "python_commit": release.python_commit,
            "idea_id": release.idea_id,
        },
        "arbiter": {
            "run_id": verdict.get("run_id") if verdict else None,
            "request_id": verdict.get("request_id") if verdict else None,
            "verdict": verdict.get("verdict") if verdict else None,
            "terminal_result": verdict.get("terminal_result") if verdict else None,
            "result_class": verdict.get("result_class") if verdict else None,
            "report_path": verdict.get("report_path") if verdict else None,
        },
        "metrics": metrics,
        "bundle_file_count": len(payload),
        "source_files": source_files,
        "generated_files": generated_files,
        "excluded_file_classes": [
            "raw runner prompts",
            "raw runner stdout/stderr",
            "runner event jsonl streams",
            "runner completion/invocation payloads",
            "process env dumps",
            "daemon logs",
            "pycache artifacts",
        ],
    }


def write_tarball(output: Path, payload: dict[str, bytes]) -> None:
    raw_buffer = io.BytesIO()
    with tarfile.open(fileobj=raw_buffer, mode="w") as archive:
        for arcname, data in sorted(payload.items()):
            info = tarfile.TarInfo(arcname)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            archive.addfile(info, io.BytesIO(data))

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=handle,
            mtime=0,
            compresslevel=9,
        ) as gzip_file:
            gzip_file.write(raw_buffer.getvalue())


def write_evidence_dir(evidence_dir: Path, files: dict[str, bytes], tarball: Path) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    generated_dir = evidence_dir / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    for relative, data in files.items():
        path = evidence_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    checksum_targets = sorted(
        path
        for path in evidence_dir.rglob("*")
        if path.is_file() and path.name != "checksums.sha256"
    )
    lines = [
        f"{sha256_file(path)}  {path.relative_to(evidence_dir).as_posix()}"
        for path in checksum_targets
    ]
    if tarball.is_file():
        lines.append(f"{sha256_file(tarball)}  ../../dist/{tarball.name}")
    (generated_dir / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_release(source: Path, evidence_root: Path, dist_root: Path, release: Release) -> dict:
    paths, verdict, stage_paths = collect_release_paths(source, release)
    metrics, stage_rows, run_rows = stage_metrics(source, stage_paths)
    metrics.update(
        {
            "version": f"v{release.version}",
            "source": "millrace-rs",
            "python_from": release.python_from,
            "python_to": release.python_to,
            "idea_id": release.idea_id,
        }
    )

    payload: dict[str, bytes] = {}
    for path in sorted(paths, key=lambda item: rel(item, source)):
        add_payload(payload, f"{release.prefix}/millrace-rs/{rel(path, source)}", path.read_bytes())

    for relative in TAG_SNAPSHOT_PATHS:
        data = run_git_show(source, release.tag, relative)
        if data is not None:
            add_payload(payload, f"{release.prefix}/release-tag/{release.tag}/{relative}", data)

    metrics_bytes = json.dumps(metrics, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    stage_summary_bytes = csv_bytes(stage_rows, ("plane", "stage", "calls"))
    run_summary_bytes = csv_bytes(run_rows, ("run_id", "stage_results"))

    add_payload(payload, f"{release.prefix}/generated/metrics.json", metrics_bytes)
    add_payload(payload, f"{release.prefix}/generated/stage-summary.csv", stage_summary_bytes)
    add_payload(payload, f"{release.prefix}/generated/run-summary.csv", run_summary_bytes)

    provisional_manifest = build_manifest(release, payload, metrics, verdict)
    readme_bytes = build_readme(release, provisional_manifest).encode("utf-8")
    add_payload(payload, f"{release.prefix}/README.md", readme_bytes)

    manifest = build_manifest(release, payload, metrics, verdict)
    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    add_payload(payload, f"{release.prefix}/manifest.json", manifest_bytes)

    issues = []
    for arcname, data in sorted(payload.items()):
        issues.extend(scan_payload(arcname, data))
    review = {
        "schema_version": "1.0",
        "kind": "sanitizer_review",
        "release": f"v{release.version}",
        "redaction_rules": [
            "workspace absolute roots",
            "Windows user homes",
            "Linux user homes and Millrace Python venv path",
            "cookie and authorization headers",
            "bearer tokens",
            "token-like query parameters and secret assignments",
        ],
        "blocked_file_classes": manifest["excluded_file_classes"],
        "issue_count": len(issues),
        "issues": issues,
    }
    if issues:
        raise SystemExit(f"sanitizer review failed for v{release.version}: {issues[:3]}")

    review_bytes = json.dumps(review, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    add_payload(payload, f"{release.prefix}/generated/sanitizer-review.json", review_bytes)

    manifest = build_manifest(release, payload, metrics, verdict)
    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    add_payload(payload, f"{release.prefix}/manifest.json", manifest_bytes)

    tarball = dist_root / f"v{release.version}-port-evidence.tar.gz"
    write_tarball(tarball, payload)
    tarball_sha = sha256_file(tarball)

    evidence_readme = build_readme(release, manifest, tarball_sha).encode("utf-8")
    evidence_files = {
        "README.md": evidence_readme,
        "manifest.json": manifest_bytes,
        "generated/metrics.json": metrics_bytes,
        "generated/stage-summary.csv": stage_summary_bytes,
        "generated/run-summary.csv": run_summary_bytes,
        "generated/sanitizer-review.json": review_bytes,
        "tarball.sha256": f"{tarball_sha}  ../../dist/{tarball.name}\n".encode("utf-8"),
    }
    write_evidence_dir(evidence_root / f"v{release.version}", evidence_files, tarball)
    return {
        "version": f"v{release.version}",
        "tarball": str(tarball),
        "sha256": tarball_sha,
        "files": len(payload),
        "stage_results": metrics["summary"]["stage_result_count"],
        "runs": metrics["summary"]["run_count"],
    }


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    evidence_root = args.evidence_root
    dist_root = args.dist_root
    results = [
        export_release(source, evidence_root, dist_root, release)
        for release in selected_releases(args.versions)
    ]
    for result in results:
        print(
            f"{result['version']}: {result['tarball']} "
            f"sha256={result['sha256']} files={result['files']} "
            f"stage_results={result['stage_results']} runs={result['runs']}"
        )


if __name__ == "__main__":
    main()
