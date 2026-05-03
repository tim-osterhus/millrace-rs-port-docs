# Rust Millrace Efficacy Run

This note records the live efficacy smoke for the published Rust crate
`millrace-ai v0.1.0`.

## Summary

- Date: 2026-04-29 HST / 2026-04-30 UTC
- Crate tested: `millrace-ai v0.1.0` from crates.io
- Binary: `millrace`
- Workspace: `/tmp/millrace-rs-real-efficacy-workspace`
- Run ID: `run-41152-0`
- Task ID: `real-efficacy-task`
- Mode override: `standard_plain`
- Active compiled mode: `default_codex`
- Runner: real Codex CLI via `<HOME_BIN>/codex`
- Outcome: task completed and moved to `tasks/done/real-efficacy-task.md`

The task asked the Rust daemon to create `efficacy-output.txt` at the workspace
root with exact content:

```text
rust-millrace-efficacy-ok
```

The final verification confirmed the file existed and contained exactly that
25-byte value with no trailing content.

## Runtime Timing

The daemon started at `2026-04-30T08:46:39.232258061Z` and completed the run at
`2026-04-30T08:53:12.127128359Z`.

Total run duration from run inspection:

- `392.894870298` seconds
- about `6 minutes 33 seconds`

Stage timings:

| Stage | Terminal Result | Duration |
| --- | --- | ---: |
| builder | `BUILDER_COMPLETE` | `137.533369007s` |
| checker | `CHECKER_PASS` | `121.191242745s` |
| updater | `UPDATE_COMPLETE` | `134.117276054s` |

The monitor log reported the same stage progression:

```text
builder -> checker -> updater -> done
```

## Token Usage

Token usage was extracted from the Codex runner event streams
`runner_events.request-41152-*.jsonl`, specifically their `turn.completed`
usage payloads.

The normalized Millrace `stage_results/*.json` files had `token_usage: null`,
so the source of truth for this table is the raw runner event stream.

| Stage | Input Tokens | Cached Input Tokens | Output Tokens | Reasoning Output Tokens |
| --- | ---: | ---: | ---: | ---: |
| builder | `262,706` | `221,952` | `5,476` | `2,921` |
| checker | `247,352` | `201,472` | `5,136` | `2,258` |
| updater | `265,697` | `204,416` | `5,423` | `2,052` |
| **Total** | **`775,755`** | **`627,840`** | **`16,035`** | **`7,231`** |

Derived values:

- Non-cached input tokens: `147,915`
- Input plus output tokens: `791,790`

`reasoning_output_tokens` is reported as a separate Codex usage field here; this
document leaves it separate rather than assuming whether it is included in
`output_tokens` for billing.

## Commands Exercised

The smoke used the published crate and a fresh disposable workspace:

```bash
cargo install millrace-ai --version 0.1.0 --locked
millrace init --workspace /tmp/millrace-rs-real-efficacy-workspace
millrace compile validate --workspace /tmp/millrace-rs-real-efficacy-workspace
millrace queue add-task /tmp/real-efficacy-task.md --workspace /tmp/millrace-rs-real-efficacy-workspace
millrace run daemon --workspace /tmp/millrace-rs-real-efficacy-workspace --mode standard_plain --config /tmp/millrace-rs-real-efficacy-workspace/millrace-agents/millrace.toml --max-ticks 6 --monitor basic --monitor-log /tmp/millrace-rs-real-efficacy-workspace/millrace-agents/logs/real-efficacy-monitor.log
millrace status --workspace /tmp/millrace-rs-real-efficacy-workspace
millrace queue ls --workspace /tmp/millrace-rs-real-efficacy-workspace
```

Runtime config for the real run:

```toml
[runners.codex]
command = "<HOME_BIN>/codex"
permission_default = "maximum"

[stages.builder]
timeout_seconds = 900

[stages.checker]
timeout_seconds = 900

[stages.updater]
timeout_seconds = 900
```

## Final State

Final status reported:

- `process_running: false`
- `runtime_ownership_lock: absent`
- `active_run_count: 0`
- `execution_queue_depth: 0`
- `planning_queue_depth: 0`
- `learning_queue_depth: 0`

Final queue inspection reported:

- `task_queue_count: 0`
- `task_done_count: 1`
- `task_blocked_count: 0`
- work item `real-efficacy-task` in `done`

## Interpretation

This run proves the published Rust crate can do useful work through the core
daemon path:

- initialize and compile a fresh workspace
- accept a task
- acquire daemon ownership
- dispatch real Codex-backed stages
- route `builder -> checker -> updater`
- persist run artifacts and monitor logs
- move the completed task into `done`
- release runtime ownership cleanly

It does not prove every Rust Millrace surface end to end. Planning decomposition,
learning promotion, Pi runner behavior, watcher intake, and long unattended
operation still need their own live efficacy checks.
