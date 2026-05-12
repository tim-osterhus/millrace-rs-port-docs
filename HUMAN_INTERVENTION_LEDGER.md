# Human Intervention Ledger

This ledger separates "no manual code edits" from broader claims such as "no
human involvement." The latter is usually too vague to be useful.

## Terms

- **Manual code edit**: a human directly writes or patches the Rust crate code
  during the evidence window.
- **Mid-run continuation prompt**: a human prompts the agent to continue,
  redirect, or fix a specific implementation task while the autonomous run is
  in progress.
- **Queue mutation**: a human directly edits runtime queues, done/blocked task
  files, Arbiter targets, or generated work items.
- **Release gate**: deterministic code outside the Millrace stage graph that
  performs packaging and release actions only after Arbiter closure.
- **Operator action**: starting a daemon, enabling a deployment flag, publishing
  an evidence asset, or performing repository administration.

## Initial Rust Port: `millrace-ai v0.1.0`

| Phase | Human action? | What happened |
| --- | --- | --- |
| Seeded parity ideas | Yes | The operator provided eight large parity-slice ideas. |
| Planning/spec/task decomposition | No manual decomposition claimed | Millrace generated specs, tasks, closure targets, and remediation work. |
| Rust code implementation | No manual code edits claimed | The evidence package attributes the implementation campaign to Python Millrace stages. |
| Mid-run implementation prompts | Not part of the claim | The public proof focuses on run artifacts, not a full raw terminal replay. |
| Queue mutation | No manual queue mutation claimed for completed work | Queue and closure artifacts are part of the evidence bundle. |
| Tests/checks | Mixed | Millrace stages performed checks; humans performed independent post-run verification. |
| Commit/tag/publish | Yes | Publishing, release tagging, and repository administration were operator actions outside the v0.1.0 autonomous stage graph. |
| Evidence packaging/upload | Yes | The public bundle was sanitized and published as a release asset. |

## Maintenance Releases: `v0.2.0` Through `v0.3.2`

| Phase | Human action? | What happened |
| --- | --- | --- |
| Python reference changes | Yes, outside Rust auto-port scope | The Python project remained the upstream source of truth. |
| Python release detection | No | The auto-port script fetched/inspected the reference checkout and detected the latest semver tag. |
| Rust version selection | No | The configured version policy mapped Python minor/patch changes to Rust minor/patch changes. |
| Auto-port idea generation | No | The loop generated one auto-port idea per detected release. |
| Rust code implementation | No manual code edits claimed | Millrace stages performed implementation, checking, remediation, and update work. |
| Arbiter closure | No | The release gate waited for closed Arbiter targets before deployment. |
| Release checks | No | The deterministic release gate ran release checks. |
| Commit/tag/push/publish | Gate-executed when operator-enabled | The release gate performed these actions when deployment was explicitly enabled. |
| Evidence packaging/upload | Operator assisted for current public packets | Existing public packets were assembled/sanitized/uploaded outside the Millrace stage graph. A future Blogger flow should automate this. |

## Downstream Millracer Port

Millracer has its own evidence repository. Its human-intervention ledger should
live there because it has different source versions, release targets, daemon
state, and proof packets.

This repo should not blur Millrace self-port evidence with downstream Millracer
evidence. It should link out and state the downstream status plainly.

