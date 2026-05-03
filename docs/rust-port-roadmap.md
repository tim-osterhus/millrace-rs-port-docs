# Millrace Rust Port Roadmap

This document defines the working plan for bringing the Rust implementation of
Millrace to behavioral parity with the Python `millrace-ai` runtime.

The Python implementation at `../millrace-py` is the current reference
implementation. At the time this roadmap was written, that checkout is pinned
to `v0.16.1`.

## Parity Definition

Parity means the Rust `millrace` binary preserves the operator-visible contract
of the Python implementation:

- the CLI command surface and exit behavior
- the `millrace-agents/` workspace layout
- canonical markdown work documents
- JSON state, run, mailbox, compile, baseline, and governance artifacts
- compiled-plan semantics and fingerprint currentness
- deterministic runtime tick ordering
- daemon locking, mailbox intake, watcher intake, pause/resume/stop/reload
- plane-concurrent daemon scheduling with serialized result application
- runner request/result contracts
- Codex CLI and Pi RPC adapter behavior
- learning-plane, Arbiter, closure, recovery, and usage-governance behavior

Rust source layout does not need to mirror Python module layout. The stable
surface is the CLI plus the on-disk workspace contract.

## Non-Goals

- Do not make the Rust runtime self-host the port.
- Do not initialize Millrace in this repository until an operator deliberately
  chooses to do that.
- Do not translate Python files one-for-one when a Rust-native module boundary
  better preserves the contract.
- Do not let a test fixture write `millrace-agents/` into the repository root.

## Target Rust Shape

The eventual crate should be split into authority domains rather than one large
CLI implementation:

- `contracts`: typed artifact schemas, enums, stage metadata, terminal markers
- `workspace`: path model, initialization, baseline, queue/state stores, locks
- `assets`: embedded modes, graphs, entrypoints, skills, and registries
- `compiler`: mode resolution, graph materialization, fingerprints, diagnostics
- `runtime`: lifecycle, tick cycle, supervisor, routing, result application
- `runners`: request construction, adapters, normalization, artifacts
- `cli`: operator commands and rendering

Likely crates and libraries:

- `clap` for CLI parsing
- `serde`, `serde_json`, and `toml_edit` for contract and config IO
- `thiserror` and `miette` for structured errors
- `tokio` for daemon worker orchestration
- `notify` for optional native watcher integration
- `time`, `uuid`, and `sha2` or `blake3` for runtime identity and fingerprints
- `assert_cmd`, `tempfile`, `serde_json`, and `insta` for parity tests

## Harness Strategy

The parity harness lives in Rust integration tests under `tests/`.

Always-on tests should be cheap and deterministic. They may read the Python
package version directly from `../millrace-py/src`, but they should not require
Python dependencies unless a test explicitly says so.

Full Python CLI probes should run only when a Python environment with the
reference package dependencies is available. Those probes should use temporary
workspaces and never initialize Millrace in the Rust repository checkout.

The harness compares normalized behavior rather than raw bytes when the two
implementations are expected to differ. Known acceptable differences include:

- Rust crate version vs Python package version
- absolute temporary paths
- timestamps
- generated ids
- run directory names
- ordering where the Python contract does not promise ordering

Golden snapshots are useful after a command surface stabilizes, but the first
priority is explicit structural assertions around required files, JSON fields,
state transitions, and exit codes.

## Large Slices

### Slice 0: Bootstrap Harness

Status: started.

Acceptance:

- Rust CLI exposes `millrace --version` and `millrace version`.
- Test helpers can run the Rust binary and read the Python reference version.
- Test helpers create paired temporary Python/Rust workspaces.
- No test creates `millrace-agents/` in the repository root.

### Slice 1: Contracts

Status: implementation pass complete for the Rust contract boundary; pending
runtime validation.

Port the typed contract layer first:

- stage planes, legal markers, result classes, and stage metadata
- work document models and headed markdown parsing/rendering
- runtime snapshots, recovery counters, mailbox envelopes, compile diagnostics
- stage result envelopes and token usage models

Acceptance:

- Rust parses and renders representative Python fixture documents for tasks,
  specs, incidents, and learning requests.
- JSON contracts round-trip against Python-produced fixtures for runtime
  snapshots, recovery counters, mailbox envelopes, compile diagnostics, stage
  results, runtime errors, and token usage.
- Public contract exports expose the typed boundary needed by later workspace,
  compiler, runtime, and runner slices.
- Invalid terminal markers and illegal stage/result combinations fail clearly.

### Slice 2: Workspace Substrate

Status: implementation pass complete for the Rust workspace substrate; pending
runtime validation. The library path model, initialization defaults, managed
asset deployment, baseline manifest IO, Rust `millrace init --workspace` CLI
parity, queue/state stores, offline runtime lock helpers, first doctor checks,
and committed Python-derived init parity evidence are implemented.

Implement filesystem ownership before runtime behavior:

- `millrace init`
- workspace path model
- baseline manifest creation
- managed asset deployment
- queue/state stores
- runtime lock inspection
- doctor checks

Acceptance:

- Python and Rust `init` produce equivalent required tree structure.
- selected bootstrap files match after normalization.
- queue/store unit tests cover claim, transition, block, done, and repair paths.

### Slice 3: Assets And Compiler

Status: implementation pass complete for assets and compiler authority; pending
runtime validation. The compiler contract-model boundary, deterministic
workspace asset resolution, mode resolution, compile-input fingerprints, frozen
graph materialization, persisted compiled-plan authority, currentness
inspection, `compile validate`/`compile show` CLI wiring, and committed
Python-normalized parity fixtures are implemented for initialized workspaces
and supported built-in modes.

Port embedded assets and compile authority:

- modes, graphs, stage-kind registry, entrypoints, skills
- graph materialization
- completion behavior
- learning triggers
- plane concurrency policy
- compile-input fingerprints
- current/stale/missing inspection

Acceptance:

- Rust `compile validate` succeeds for all built-in modes.
- `compiled_plan.json` matches Python structure after normalizing ids and paths.
- stale-plan refusal cases are covered.

### Slice 4: CLI Read/Write Surface

Status: implementation pass complete for the file-backed CLI read/write
surface that can be proven before runtime execution. The initial
command-framework pass is implemented:
`src/main.rs` delegates to `millrace_ai::cli`, and `src/cli/` owns shared
parsing, rendering, initialized-workspace checks, current init/doctor/compile
behavior, primary command-group recognition, compatibility aliases, and
run command parsing with initialized-workspace enforcement; Slice 4 introduced
non-executing run placeholders for runtime behavior that later runtime slices
replace selectively.
The runtime-control/mailbox facade in
`src/workspace/runtime_control.rs` is also implemented for direct offline
mutations and active-daemon mailbox envelopes covering pause, resume, stop,
retry-active, planning retry-active, clear-stale-state, reload-config, and
task/spec/idea intake. The first read-only operator CLI pass now implements
`queue ls/show`, `status`/`status show`/bounded `status watch`, `runs
ls/show/tail`, `modes list/show`, and `config show` without mutating workspace
state or implicitly compiling. Queue intake commands now implement
`queue add-task`, `queue add-spec`, `queue add-idea`, and the top-level
`add-task`/`add-spec`/`add-idea` aliases through typed work-document imports,
direct offline queue/idea writes, and active-daemon mailbox routing. Control
CLI commands and aliases for `pause`, `resume`, `stop`, `retry-active`,
`clear-stale-state`, and `reload-config` now route through the same
runtime-control boundary. `planning retry-active` uses the planning-scoped retry
boundary, `config reload` uses runtime-control routing, and `config validate`
compiles through the persisted compiler facade with default or explicit config
selection. The `millrace skills` group now implements file-backed workspace and
source listing, showing, searching, local/source and fixture/cache-backed remote
install and refresh, learning-mode-gated create/improve request queueing,
source promotion, ZIP export, and unsafe id/source target rejection. `millrace
upgrade` now implements managed baseline preview/apply output, safe package and
missing-asset restoration, conflict refusal, and removed-asset localization
without deleting operator content. Slice 4 originally preserved `millrace run
daemon` as a non-executing placeholder while runtime execution was still out of
scope; later Slice 6 work now replaces that placeholder for deterministic
fake-runner daemon execution. The `run once` parse and workspace guarantees are
now preserved by the Slice 5 serial runtime CLI wiring. `queue repair-lineage`
now wires CLI preview/apply behavior over
the workspace repair boundary, covering Arbiter closure-target loading, typed
task/spec/incident drift scanning, Python-compatible safe repair plans and
reports, active-lock and active-stage apply refusal, snapshot refresh,
`closure_lineage_repaired` event emission, and Python-compatible summary
output. Existing doctor command behavior remains covered by the earlier
workspace doctor pass and current CLI framework.
The Slice 4 CLI parity evidence is consolidated in `tests/parity_cli.rs` and
`tests/fixtures/cli_parity/slice4_cli_parity_evidence.json`.

Acceptance:

- command exit codes match Python.
- key output lines match normalized snapshots.
- commands never implicitly compile unless Python does.

### Slice 5: Serial Runtime

Status: implemented for the serial fake-runner once-mode boundary. The typed
runtime/runner contract boundary is implemented:
`millrace_ai::runtime` now models `StageRunRequest`, request context
serialization, and the once-mode runtime startup lifecycle, while
`millrace_ai::runners` now models raw runner results, deterministic fake-runner
selection and artifacts, and normalization into `StageResultEnvelope`. Startup
now validates initialized workspaces, loads config, acquires ownership before
compiler/state mutation, compiles or reuses persisted `compiled_plan.json`
authority, loads snapshot and recovery counters, preserves pause state,
projects once-mode snapshot fields, and detects stale active state across
execution/planning/learning surfaces. Serial tick activation now drains
applicable mailbox commands, refreshes queue depths, returns typed
no-work/paused/stopped/blocked outcomes before dispatch, claims at most one
compiled-plan-authorized work item across planning, execution, and learning
surfaces, can activate eligible closure-target Arbiter requests without active
work item identity, constructs full `StageRunRequest` payloads, writes running
markers, projects active-run snapshot state, and emits runtime events. Serial
dispatch/routing now runs the constructed request through the runner boundary,
persists stage request, raw runner result, normalized stage result, terminal
marker, and router decision artifacts, routes normalized results through
compiled graph transitions/resume/threshold/terminal policies, persists
runtime-error context/report evidence for recoverable normalization failures,
updates last terminal/result snapshot status, and records `stage_completed` and
`router_decision` events. Queue/result application now applies routed
`run_stage`, `idle`, `handoff`, and `blocked` outcomes through typed queue and
state-store helpers, updates active-run and final snapshot state, mutates
recovery counters, enqueues typed handoff incidents, and schedules
post-stage application-failure recovery with runtime-error context/report
evidence. Closure-result application now handles Arbiter `ARBITER_COMPLETE`
closure, `REMEDIATION_NEEDED` remediation incident enqueue with report
evidence, queued/active/blocked lineage-work suppression, and repeated
remediation blocking without intervening execution. The `millrace run once`
CLI now starts the once-mode runtime session, honors `--workspace`, `--mode`,
and `--config`, executes exactly one serial tick through the deterministic
fake-runner boundary, renders operator-facing dispatched, idle, paused,
stopped, blocked, startup-failure, and tick-failure outcomes, left `run
daemon` as the explicit placeholder at Slice 5 completion, and releases runtime
ownership after the covered normal and failure paths. Slice 5 parity evidence
is consolidated in
`tests/runtime_serial.rs`, `tests/parity_cli.rs`, and
`tests/fixtures/cli_parity/slice5_serial_runtime_parity_evidence.json`; that
committed evidence maps Rust scenarios to the Python `test_runtime.py`,
`test_result_application.py`, `test_router.py`, and `test_e2e_handoffs.py`
sources while normalizing request ids, run ids, timestamps, absolute paths,
run artifact paths, and incident ids. Slice 6 now adds daemon monitor streaming,
deterministic fake-runner CLI daemon execution, and committed daemon parity
evidence, and Slice 7 now adds runtime-configured real-adapter dispatch for
operator once/daemon paths. Slice 8 now has typed usage-governance state,
ledger, token-window, subscription quota contracts, runtime dispatch
enforcement, auto-resume, monitor evidence, learning trigger enqueueing,
runtime-owned skill revision evidence, Curator promotion record deferral and
application after foreground drain, rejected/blocked Curator decision evidence,
operator-controlled source promotion audit fields, closure-target
creation/backfill from root-spec claims or drained roots, closure readiness
blocking for queued/active/blocked same-root work, lineage drift diagnostics,
Arbiter close/remediation/repeated-remediation behavior, and read-only run
inspection depth for malformed, incomplete, token-bearing, runner-artifact,
governance-linked, closure-target, and skill-evidence-bearing runs, plus
scripted serial E2E handoff coverage for direct task success, repair-loop
fix-contract evidence, malformed and illegal terminal recovery, planning
re-entry, Arbiter completion/remediation, and repeated-remediation blocking;
optional native filesystem watcher integration, live subscription quota
integration remains later work, and consolidated Slice 8 parity evidence/docs
are complete for the fixture-backed advanced surfaces.

Implemented serial runtime pieces include:

- stage request and runner result contracts
- startup lifecycle library boundary
- deterministic tick cycle
- claim ordering
- stage request rendering
- result persistence
- router/result application
- recovery counters
- closure target and Arbiter activation
- `millrace run once` CLI wiring through one fake-runner serial tick
- committed Python-normalized parity evidence for the serial fake-runner
  runtime boundary

Acceptance:

- fake-runner scenarios reproduce Python queue and state transitions.
- runtime-owned mutation remains single-writer.
- stage code never directly mutates authoritative queue state.

### Slice 6: Daemon Runtime

Status: implemented for the deterministic fake-runner daemon boundary. The
daemon startup/config, supervisor/completion, bounded loop/shutdown,
mailbox/reload, watcher poll-intake, basic monitor rendering, deterministic
fake-runner CLI execution, and committed parity-evidence boundaries are
implemented: daemon
startup requires initialized
workspaces, uses the same
compiled-plan authority and mode/config inputs as once mode, projects
`RuntimeMode::Daemon`, loads Python-compatible idle-sleep and watcher config
defaults, prepares deterministic poll watcher-session state without native
filesystem watchers or work claiming, and releases only the matching daemon
session lock on startup failure or close. The supervisor evaluates
compiled-plan plane-concurrency policy against active-run snapshot state, keeps
default modes serial without an enabling policy, allows learning beside allowed
foreground work in learning modes, dispatches deterministic fake-runner workers,
captures typed worker outcomes, drains completed workers before new claims, and
applies completions serially through owner-side metadata validation and the
existing result-application path. The bounded loop runs supervisor cycles,
records completed tick count, supports max-tick/no-work
idle/stop/process-stopped/blocked exits, uses configured or test-controlled
idle sleep, drains completions after cycles and during shutdown, resets stopped
daemon state, closes prepared watcher/session resources, and releases the
matching ownership lock. Daemon mailbox handling drains pause, resume, stop,
retry-active, planning retry-active, clear-stale-state, reload-config, add-task,
add-spec, and add-idea commands in deterministic order; moves commands to
processed or failed `mailbox_archive` artifacts with source/error evidence;
continues after invalid or failed payloads; defers reload while active planes
exist; applies reload after planes drain with watcher-session rebuild plus
config-version and compiled-plan snapshot updates; and preserves the previous
compiled plan on recoverable reload diagnostics. Deterministic watcher poll
intake runs after mailbox drain and before work claims, observes config, task
queue, optional spec queue, and optional `ideas/inbox` changes, debounces
repeated writes, handles missing roots and deleted files safely, normalizes new
idea markdown into headed specs through `QueueStore`, preserves root lineage
and references, skips duplicate idea-derived specs, and records watcher
event/failure/skip evidence without corrupting queue, active, done, blocked,
snapshot, status, or run artifacts. Basic monitor rendering emits stable key
lines for runtime, stage, router, status, idle, pause, stop, reload, watcher,
and governance pause/block/degraded/reconciled or resume events; `millrace run
daemon` now starts the daemon runtime with the runtime-configured runner
dispatcher, keeps default stdout quiet except final summary lines, renders
completed-tick summary keys
including Python-compatible `ticks`, supports `--monitor basic`, and writes
append-mode `--monitor-log` fanout with missing parent-directory creation and
without enabling stdout monitor mode.

Implemented daemon pieces:

- daemon ownership lock and startup/config projection
- plane-concurrent supervisor scheduling boundary
- serialized result application from worker completions
- bounded daemon loop, idle wait, shutdown drain, and matching lock release
- daemon mailbox command intake and config reload deferral/application
- deterministic watcher poll intake and idea-to-spec normalization
- basic monitor rendering and append-mode monitor-log fanout
- daemon final-summary completed-tick key lines
- runtime-configured `millrace run daemon` CLI execution
- committed Python-normalized parity evidence for the fake-runner daemon
  runtime boundary

Remaining later-slice surfaces:

- optional native filesystem watcher integration
- live subscription quota integration

Acceptance:

- default modes remain serial.
- learning modes allow one learning lane beside permitted foreground work.
- config reload waits for active planes to drain.
- shutdown clears running state without corrupting active artifacts.

### Slice 7: Runner Adapters

Status: implemented for the runner adapter parity boundary, including committed
parity evidence/docs. The shared runner boundary is implemented: canonical
prompt rendering
and `runner_prompt.<request_id>.md` persistence, serde-backed
invocation/completion artifacts, explicit process-result and environment-delta
models, duplicate-aware registry registration, dispatcher resolution by request
runner, caller default, then Python-compatible `codex_cli`, fake-runner prompt
materialization, public exports, and focused runtime/public-export tests. The
Codex CLI adapter is also implemented with Python-compatible command
construction, permission precedence, prompt and runner artifacts, JSONL
event/token handling, timeout/failure evidence, mocked process coverage, and a
real subprocess executor. The Pi RPC adapter is also implemented with
Python-compatible command construction, JSONL prompt lifecycle, filtered
event-log policy, final assistant text and session stats queries, timeout
abort/terminate/hard-kill evidence, failure mapping, mocked client/transport
coverage, and public exports. Runtime runner config loading is implemented for
`[runners]`, `[runners.codex]`, `[runners.pi]`, `[usage_governance]`, and
`[stages.<stage>]`, with path-aware validation for runner names, Codex
permissions, reasoning effort, environment maps, Pi event-log policy and
reserved flags, stage overrides, timeouts, runtime-token rules, and
subscription-quota percent thresholds. Adapter-only command, permission,
environment, and event-log settings are available to runtime startup without
changing compile fingerprints. `millrace run once` and `millrace run daemon`
now construct runtime-configured dispatchers that register `codex_cli` and
`pi_rpc`, preserve fake/mock injection seams, persist request-scoped runner
artifacts, and route serial or daemon adapter failures through existing
normalization, terminal-marker, router-decision, and recovery paths.

The Python-owned runner contract remains
`StageRunRequest -> RunnerRawResult -> StageResultEnvelope`. Rust preserves the
per-run artifact filenames `runner_prompt.<request_id>.md`,
`runner_invocation.<request_id>.json`, `runner_stdout.<request_id>.txt`,
`runner_stderr.<request_id>.txt`, optional
`runner_events.<request_id>.jsonl`, and
`runner_completion.<request_id>.json`. The committed Slice 7 fixture
`tests/fixtures/cli_parity/slice7_runner_adapter_parity_evidence.json` maps the
Rust registry, dispatcher, Codex CLI command/artifact/token/timeout behavior,
Pi RPC lifecycle/event policy/timeout behavior, config validation, and
runtime-dispatch scenarios back to the Python runner architecture docs, runner
modules, and runner/runtime/CLI tests while normalizing volatile ids, paths,
timestamps, process/timing fields, config versions, runner artifact paths, and
token counts. Always-on tests validate that fixture so stale or malformed
evidence fails `cargo test --test parity_cli`. The live smoke surface is
present but opt-in: `cargo test --test runners_live_smoke` only checks the
no-live gates, while
`MILLRACE_REAL_CODEX_SMOKE=1 cargo test --test runners_live_smoke codex_real_adapter_live_smoke -- --ignored --nocapture`
and
`MILLRACE_REAL_PI_SMOKE=1 cargo test --test runners_live_smoke pi_real_adapter_live_smoke -- --ignored --nocapture`
invoke the real Codex CLI and Pi RPC adapters after the operator supplies
external binaries, credentials or subscriptions, and network access. This slice
does not claim broader compiled-plan, queue-state, or stage-machine changes
beyond the runtime-dispatch boundary above; adapter-only command, permission,
environment, and event-log settings remain runtime config and stay out of
compile fingerprints.

Remaining later-slice surfaces:

- native filesystem watcher integration
- live subscription quota integration

Acceptance:

- adapter artifacts match the Python contract.
- fake or mocked runners remain the default CI path.
- real adapters have smoke tests gated behind explicit environment variables.
- committed parity evidence maps the Rust adapter behavior to Python references.

### Slice 8: Advanced Parity

Status: implemented for fixture-backed advanced parity. Rust now has
serde-backed usage-governance state, blockers, stage-result token
ledger entries, idempotent ledger reconciliation from stage-result artifacts,
rolling/session/calendar token-window evaluation, subscription quota
status/window telemetry contracts, degraded fail-open/fail-closed policy,
threshold blocker evaluation, path-aware malformed state/JSONL ledger errors,
runtime config parsing for token/quota rules, and read-only status/config
rendering without mutation. Serial and daemon runtime paths now record completed
stage-result token evidence once, reconcile missing ledger entries before new
dispatch, apply governance-owned pause sources independently from operator
pauses, block new work at Python-compatible runtime boundaries, support
rolling-window auto-resume for governance pauses, preserve allowed cleanup and
control paths, and render governance blocked/paused/degraded/resumed/reconciled
events through the basic monitor. Runtime-owned learning promotion and skill
evidence handling now enqueues learning requests from compiler-frozen trigger
rules, preserves stage-request skill revision evidence in run directories,
writes Curator `skill_update` promotion records under learning
update-candidate surfaces, defers promotion while foreground execution or
planning lanes are active, applies deferred records after foreground drain, and
keeps source-packaged skill mutation behind explicit `millrace skills promote`
operator commands with audit fields. Rejected or blocked Curator decisions keep
decision and skill-revision evidence inspectable without creating promotion
records. Closure-lineage runtime parity now creates closure targets from
root-spec claims, backfills targets from drained root specs, refreshes
readiness before Arbiter dispatch, blocks on queued/active/blocked same-root
lineage work and lineage drift diagnostics with concrete blocking ids, emits
completion backfill and drift events, closes targets on `ARBITER_COMPLETE`,
enqueues remediation incidents on `REMEDIATION_NEEDED`, and blocks repeated
remediation without intervening execution while preserving `queue
repair-lineage` behavior. Read-only run inspection now keeps complete,
incomplete, malformed, token-bearing, closure-target, governance-linked,
skill-evidence-bearing, and runner-artifact-bearing run directories visible,
surfaces malformed stage results, primary runner artifacts, aggregate
duration/token evidence, governance ledger links, closure metadata, remediation
references, raw runner exit metadata, and skill-revision evidence, and tails
report, stdout, stderr, event-log, or stage-result payloads without mutating
inspected runtime artifacts. E2E handoff parity now covers direct task success
through runtime-owned queue and status transitions, checker/fixer/doublechecker
repair with fix-contract evidence, malformed and illegal terminal recovery
through Consultant handoff incidents, planning incident re-entry into
execution, lineage-drain Arbiter completion, Arbiter remediation incident
enqueue, and repeated-remediation blocking with scripted fake runners and a
committed `slice8_e2e_handoff_parity_evidence.json` fixture. Consolidated
Slice 8 evidence is committed in
`slice8_advanced_parity_evidence.json`, mapping usage governance,
subscription quota telemetry, learning promotion, skill evidence, closure
transitions, run inspection, and E2E handoffs to Python modules/tests while
rejecting unknown, malformed, stale, or missing Rust test references. Native
filesystem watcher integration and live subscription-provider polling remain
preview-only/deferred.

Remaining high-value edge surfaces:

- optional native filesystem watcher integration
- live subscription quota integration beyond persisted or fixture-friendly
  telemetry status

Acceptance:

- Python fixture scenarios can be replayed through Rust.
- docs state which surfaces are fully compatible and which are still preview.

## Using Python Millrace To Drive The Port

Python Millrace is the right orchestrator once Slice 0 creates rails and the
backlog is decomposed into acceptance-gated work items. The port should be
managed as long-running staged work against `millrace-rs`, with the Python
runtime owning queue state and progress.

That should happen later as an operator action. This repository is prepared not
to track `millrace-agents/`, but this bootstrap does not initialize Millrace.
