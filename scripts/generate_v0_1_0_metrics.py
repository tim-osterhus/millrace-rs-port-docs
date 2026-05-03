#!/usr/bin/env python3
"""Generate public metrics for the Millrace Rust v0.1.0 port proof."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median


USAGE_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("../millrace-rs"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evidence/v0.1.0/generated"),
    )
    return parser.parse_args()


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def format_seconds(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remainder = seconds % 60
    return f"{hours}h {minutes}m {remainder:.1f}s"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def request_id_from_events_path(path: Path) -> str:
    match = re.match(r"runner_events\.(request-[^.]+)\.jsonl$", path.name)
    if not match:
        raise ValueError(f"unexpected runner event filename: {path}")
    return match.group(1)


def usage_by_request(source: Path) -> dict[str, Counter]:
    usage: dict[str, Counter] = defaultdict(Counter)
    for path in sorted(source.glob("millrace-agents/runs/run-*/runner_events.request-*.jsonl")):
        request_id = request_id_from_events_path(path)
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = event.get("usage")
            if not isinstance(payload, dict):
                continue
            for key, value in payload.items():
                if key in USAGE_KEYS and isinstance(value, int):
                    usage[request_id][key] += value
    return usage


def load_stage_results(source: Path) -> list[dict]:
    stages = []
    for path in sorted(source.glob("millrace-agents/runs/run-*/stage_results/*.json")):
        stage = read_json(path)
        stage["_path"] = str(path.relative_to(source))
        stages.append(stage)
    return stages


def stage_request_id(stage: dict) -> str | None:
    metadata = stage.get("metadata")
    if isinstance(metadata, dict):
        request_id = metadata.get("request_id")
        if isinstance(request_id, str):
            return request_id
    request_id = stage.get("request_id")
    return request_id if isinstance(request_id, str) else None


def group_for_work_item(work_item_id: str | None) -> str:
    value = work_item_id or ""
    groups = (
        ("slice-1-contracts", "idea-slice-1-contracts"),
        ("slice-2-workspace-substrate", "idea-slice-2-workspace-substrate"),
        ("slice-3-assets-and-compiler", "idea-slice-3-assets-and-compiler"),
        ("slice-4-cli-read-write-surface", "idea-slice-4-cli-read-write-surface"),
        ("slice-5-serial-runtime", "idea-slice-5-serial-runtime"),
        ("slice-6-daemon-runtime", "idea-slice-6-daemon-runtime"),
        ("slice-7-runner-adapters", "idea-slice-7-runner-adapters"),
        ("slice-8-advanced-parity", "idea-slice-8-advanced-parity"),
    )
    for group, marker in groups:
        if marker in value:
            return group
    if "slice-7" in value:
        return "slice-7-runner-adapters"
    if "slice-4" in value:
        return "slice-4-cli-read-write-surface"
    if "slice-1" in value:
        return "slice-1-contracts"
    return "learning-side-work" if value.startswith("learn-") else "other"


def md_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def collect_paths(source: Path, pattern: str) -> list[str]:
    return sorted(str(path.relative_to(source)) for path in source.glob(pattern))


def add_usage(target: Counter, source: Counter) -> None:
    for key in USAGE_KEYS:
        target[key] += source.get(key, 0)


def compute_metrics(source: Path) -> dict:
    source = source.resolve()
    stages = load_stage_results(source)
    usage = usage_by_request(source)

    starts = [parse_timestamp(stage.get("started_at")) for stage in stages]
    ends = [parse_timestamp(stage.get("completed_at")) for stage in stages]
    starts = [value for value in starts if value is not None]
    ends = [value for value in ends if value is not None]
    durations = [float(stage.get("duration_seconds") or 0) for stage in stages]

    usage_totals = Counter()
    stage_counts = Counter()
    terminal_counts = Counter()
    result_class_counts = Counter()
    usage_by_stage: dict[str, Counter] = defaultdict(Counter)
    usage_by_plane: dict[str, Counter] = defaultdict(Counter)
    requests_with_usage = 0
    requests_without_usage = 0
    no_usage = []

    groups = defaultdict(
        lambda: {
            "runs": set(),
            "work_items": set(),
            "stage_calls": 0,
            "duration_seconds": 0.0,
            "usage": Counter(),
            "result_classes": Counter(),
            "stages": Counter(),
        }
    )

    for stage in stages:
        plane = stage.get("plane") or "unknown"
        stage_name = stage.get("stage") or "unknown"
        terminal = stage.get("terminal_result") or "unknown"
        result_class = stage.get("result_class") or "unknown"
        work_item_id = stage.get("work_item_id")
        request_id = stage_request_id(stage)
        stage_usage = usage.get(request_id or "", Counter())

        stage_counts[f"{plane}/{stage_name}"] += 1
        terminal_counts[f"{stage_name}/{terminal}"] += 1
        result_class_counts[result_class] += 1
        if stage_usage:
            requests_with_usage += 1
            add_usage(usage_totals, stage_usage)
            add_usage(usage_by_stage[f"{plane}/{stage_name}"], stage_usage)
            add_usage(usage_by_plane[plane], stage_usage)
        else:
            requests_without_usage += 1
            no_usage.append(
                {
                    "run_id": stage.get("run_id"),
                    "request_id": request_id,
                    "plane": plane,
                    "stage": stage_name,
                    "terminal_result": terminal,
                    "result_class": result_class,
                    "work_item_id": work_item_id,
                    "duration_seconds": float(stage.get("duration_seconds") or 0),
                    "path": stage["_path"],
                }
            )

        group = group_for_work_item(work_item_id)
        groups[group]["runs"].add(stage.get("run_id"))
        if work_item_id:
            groups[group]["work_items"].add(work_item_id)
        groups[group]["stage_calls"] += 1
        groups[group]["duration_seconds"] += float(stage.get("duration_seconds") or 0)
        add_usage(groups[group]["usage"], stage_usage)
        groups[group]["result_classes"][result_class] += 1
        groups[group]["stages"][stage_name] += 1

    run_ids = {stage.get("run_id") for stage in stages if stage.get("run_id")}
    first_started = min(starts) if starts else None
    last_completed = max(ends) if ends else None
    wall_seconds = (
        (last_completed - first_started).total_seconds()
        if first_started and last_completed
        else 0.0
    )

    artifact_counts = {
        "ideas_seeded": len(collect_paths(source, "ideas/inbox/*.md")),
        "ideas_contracts": len(collect_paths(source, "millrace-agents/arbiter/contracts/ideas/*.md")),
        "root_specs": len(collect_paths(source, "millrace-agents/arbiter/contracts/root-specs/*.md")),
        "rubrics": len(collect_paths(source, "millrace-agents/arbiter/rubrics/*.md")),
        "targets": len(collect_paths(source, "millrace-agents/arbiter/targets/*.json")),
        "verdicts": len(collect_paths(source, "millrace-agents/arbiter/verdicts/*.json")),
        "arbiter_reports": len(collect_paths(source, "millrace-agents/arbiter/reports/*.md")),
        "incidents_resolved": len(collect_paths(source, "millrace-agents/incidents/resolved/*.md")),
        "learning_blocked": len(collect_paths(source, "millrace-agents/learning/requests/blocked/*.md")),
        "tasks_done": len(collect_paths(source, "millrace-agents/tasks/done/*.md")),
        "tasks_blocked": len(collect_paths(source, "millrace-agents/tasks/blocked/*.md")),
        "specs_done": len(collect_paths(source, "millrace-agents/specs/done/*.md")),
        "specs_blocked": len(collect_paths(source, "millrace-agents/specs/blocked/*.md")),
    }

    seeded_ideas = [
        {
            "path": str(path.relative_to(source)),
            "title": md_title(path),
        }
        for path in sorted(source.glob("ideas/inbox/*.md"))
    ]

    slice_summaries = []
    for group, payload in sorted(groups.items()):
        usage_payload = {key: payload["usage"].get(key, 0) for key in USAGE_KEYS}
        slice_summaries.append(
            {
                "group": group,
                "run_count": len(payload["runs"]),
                "stage_calls": payload["stage_calls"],
                "work_item_count": len(payload["work_items"]),
                "duration_seconds": round(payload["duration_seconds"], 6),
                "duration_hms": format_seconds(payload["duration_seconds"]),
                "usage": usage_payload,
                "result_classes": dict(sorted(payload["result_classes"].items())),
                "stages": dict(sorted(payload["stages"].items())),
            }
        )

    metrics = {
        "version": "v0.1.0",
        "source": "millrace-rs",
        "summary": {
            "run_count": len(run_ids),
            "stage_result_count": len(stages),
            "requests_with_usage": requests_with_usage,
            "requests_without_usage": requests_without_usage,
            "runner_event_file_count": len(
                list(source.glob("millrace-agents/runs/run-*/runner_events.request-*.jsonl"))
            ),
            "first_started_at": first_started.isoformat() if first_started else None,
            "last_completed_at": last_completed.isoformat() if last_completed else None,
            "wall_seconds": round(wall_seconds, 6),
            "wall_hms": format_seconds(wall_seconds),
            "sum_stage_duration_seconds": round(sum(durations), 6),
            "sum_stage_duration_hms": format_seconds(sum(durations)),
            "median_stage_duration_seconds": round(median(durations), 6) if durations else 0,
            "max_stage_duration_seconds": round(max(durations), 6) if durations else 0,
            "input_plus_output_tokens": usage_totals["input_tokens"]
            + usage_totals["output_tokens"],
            "non_cached_input_tokens": usage_totals["input_tokens"]
            - usage_totals["cached_input_tokens"],
            "non_cached_input_plus_output_tokens": usage_totals["input_tokens"]
            - usage_totals["cached_input_tokens"]
            + usage_totals["output_tokens"],
            "cached_input_share": round(
                usage_totals["cached_input_tokens"] / usage_totals["input_tokens"], 12
            ),
        },
        "usage_totals": {key: usage_totals.get(key, 0) for key in USAGE_KEYS},
        "artifact_counts": artifact_counts,
        "stage_counts": dict(sorted(stage_counts.items())),
        "terminal_counts": dict(sorted(terminal_counts.items())),
        "result_class_counts": dict(sorted(result_class_counts.items())),
        "usage_by_stage": {
            key: {usage_key: value.get(usage_key, 0) for usage_key in USAGE_KEYS}
            for key, value in sorted(usage_by_stage.items())
        },
        "usage_by_plane": {
            key: {usage_key: value.get(usage_key, 0) for usage_key in USAGE_KEYS}
            for key, value in sorted(usage_by_plane.items())
        },
        "slice_summaries": slice_summaries,
        "seeded_ideas": seeded_ideas,
        "done_specs": collect_paths(source, "millrace-agents/specs/done/*.md"),
        "done_tasks": collect_paths(source, "millrace-agents/tasks/done/*.md"),
        "resolved_incidents": collect_paths(source, "millrace-agents/incidents/resolved/*.md"),
        "stages_without_usage": no_usage,
    }
    return metrics


def write_stage_summary(metrics: dict, output: Path) -> None:
    rows = []
    for key, calls in metrics["stage_counts"].items():
        usage = metrics["usage_by_stage"].get(key, {})
        plane, stage = key.split("/", 1)
        rows.append(
            {
                "plane": plane,
                "stage": stage,
                "calls": calls,
                **{usage_key: usage.get(usage_key, 0) for usage_key in USAGE_KEYS},
            }
        )
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("plane", "stage", "calls", *USAGE_KEYS),
        )
        writer.writeheader()
        writer.writerows(rows)


def write_slice_summary(metrics: dict, output: Path) -> None:
    rows = []
    for item in metrics["slice_summaries"]:
        usage = item["usage"]
        rows.append(
            {
                "group": item["group"],
                "run_count": item["run_count"],
                "stage_calls": item["stage_calls"],
                "work_item_count": item["work_item_count"],
                "duration_seconds": item["duration_seconds"],
                **{usage_key: usage.get(usage_key, 0) for usage_key in USAGE_KEYS},
            }
        )
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "group",
                "run_count",
                "stage_calls",
                "work_item_count",
                "duration_seconds",
                *USAGE_KEYS,
            ),
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums(output_dir: Path) -> None:
    targets = [
        output_dir / "metrics.json",
        output_dir / "stage-summary.csv",
        output_dir / "slice-summary.csv",
    ]
    lines = [f"{sha256(path)}  {path.name}" for path in targets]
    (output_dir / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    metrics = compute_metrics(args.source)
    (output / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_stage_summary(metrics, output / "stage-summary.csv")
    write_slice_summary(metrics, output / "slice-summary.csv")
    write_checksums(output)
    print(f"wrote metrics to {output}")


if __name__ == "__main__":
    main()
