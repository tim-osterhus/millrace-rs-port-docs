# Runtime Recovery After External Abort

This note records an observed recovery event during the ongoing Millrace Rust
auto-port loop. It is operational evidence for the durability of the daemon
state model during an active autonomous porting run.

## Event Summary

During the active `millrace-ai v0.3.5` auto-port run, an external OpenClaw
operator action aborted both auto-port process trees. The abort removed the
tmux sessions and stopped the daemon and supervisor processes while Millrace
was actively working.

The important result: after restart, Millrace recovered from persisted runtime
state, requeued the interrupted active work, and continued the same
Python-to-Rust parity run.

## Active Run At Abort Time

The active Millrace auto-port state at the time of the abort was:

| Field | Value |
| --- | --- |
| Python source range | `v0.18.4 -> v0.18.6` |
| Rust target | `0.3.5` |
| Active idea | `idea-auto-port-python-v0.18.4-to-v0.18.6-rust-0.3.5` |
| Closure target | open |
| Runtime process | stopped by external abort |
| Runtime ownership lock | stale |
| Runtime error report | none |
| Execution lane | active |
| Learning lane | active |

The persisted runtime snapshot still knew the interrupted execution lane:

| Field | Value |
| --- | --- |
| Active execution stage | `checker` |
| Active execution task | `auto-port-0-18-6-01-parity-harness-scout` |
| Interrupted execution run | `53959355fb3b` |
| Execution queue depth | `7` |

The persisted runtime snapshot also knew the interrupted learning lane:

| Field | Value |
| --- | --- |
| Active learning stage | `professor` |
| Active learning request | `learn-b2e1364a2312` |
| Interrupted learning run | `6b6caa8c42f7` |

The supervisor state ledger still identified the active release:

| Field | Value |
| --- | --- |
| `last_seen_python_version` | `v0.18.6` |
| `last_ported_python_version` | `v0.18.4` |
| `last_released_rust_version` | `0.3.4` |
| `active_python_version` | `v0.18.6` |
| `active_rust_version` | `0.3.5` |

## Recovery Action

The stale-state recovery command was run against the Millrace Rust workspace:

```text
millrace clear-stale-state --workspace <MILLRACE_RS> --reason "recover after OpenClaw abort"
```

It reported:

```text
action: clear_stale_state
mode: direct
applied: true
detail: cleared stale runtime state; requeued=2; runtime_ownership_lock=cleared_stale
```

That result is the key recovery signal. Millrace found two interrupted active
items, cleared the stale daemon ownership lock, and moved those interrupted
items back to actionable runtime state.

The companion Millracer harness had already completed its current release and
was idle when the abort happened. Its recovery command reported:

```text
action: clear_stale_state
mode: direct
applied: true
detail: cleared stale runtime state; requeued=0; runtime_ownership_lock=cleared_stale
```

## Restart

The Millrace daemon and supervisor were restarted in the same WSL-native tmux
layout:

| Process | Runtime mode |
| --- | --- |
| daemon | `learning_codex_auto_port` |
| supervisor | `run_supervisor.py --enqueue --release-checks` |
| deploy flags | enabled |
| evidence updater | enabled |
| evidence upload | enabled |

After restart, Millrace resumed the same `v0.3.5` release target. The daemon
reported:

| Field | Value |
| --- | --- |
| Runtime process | running |
| Runtime ownership lock | active |
| Paused | false |
| Active idea | `idea-auto-port-python-v0.18.4-to-v0.18.6-rust-0.3.5` |
| Closure target | open |
| Runtime error report | none |

The interrupted execution work restarted under a fresh run:

| Field | Value |
| --- | --- |
| Restarted execution stage | `builder` |
| Restarted execution task | `auto-port-0-18-6-01-parity-harness-scout` |
| Restarted execution run | `c1bb0a48d09d` |

The interrupted learning work also restarted under a fresh run:

| Field | Value |
| --- | --- |
| Restarted learning stage | `analyst` |
| Restarted learning request | `learn-b2e1364a2312` |
| Restarted learning run | `82c951a4a6a6` |

The supervisor immediately recognized the same active release and kept the
release gate closed until the normal release conditions were satisfied:

```text
action: active
active_idea_id: idea-auto-port-python-v0.18.4-to-v0.18.6-rust-0.3.5
active_python_version: v0.18.6
active_rust_version: 0.3.5
current_rust_version: 0.3.4
ready: false
blocked: Cargo.toml version 0.3.4 does not match 0.3.5
blocked: runtime queue_depth_execution is not zero
blocked: runtime queue_depth_learning is not zero
blocked: no closed Arbiter closure target for idea-auto-port-python-v0.18.4-to-v0.18.6-rust-0.3.5
```

Those blockers are the expected release-gate blockers for an in-progress port.
They show the supervisor did not lose release context or incorrectly deploy
after the restart.

## Why This Matters

This recovery event demonstrates several useful properties of the autonomous
maintenance loop:

1. Runtime ownership is explicit. When the daemon process disappears, the lock
   becomes stale rather than being mistaken for a healthy active daemon.
2. Active work is durable. The runtime snapshot retained the interrupted
   execution task, learning request, active release idea, queue depth, and
   closure target.
3. Recovery is deterministic. `clear-stale-state` converted interrupted active
   work back into queued/actionable work and cleared only the stale lock.
4. The daemon can resume the same autonomous port. After restart, Millrace
   continued the `v0.18.4 -> v0.18.6` / Rust `0.3.5` run instead of requiring a
   new human-authored plan.
5. The release gate stayed conservative. It continued blocking deploy until
   the Rust version, queues, active runs, and Arbiter closure reached the
   required state.
6. The companion harness behaved correctly. Millracer had already finished its
   own release, so its stale-state recovery cleared the abandoned lock without
   requeueing work.

The recovery is especially meaningful because it happened during a live
maintenance run, with concurrent execution and learning lanes active. The
system was not merely restarted from an idle state; it resumed after losing the
process tree in the middle of active staged work.

