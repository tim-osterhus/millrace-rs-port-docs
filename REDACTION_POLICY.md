# Redaction Policy

The public evidence bundles are sanitized. Sanitization is a security and
privacy boundary, not an invitation to hand-wave the proof.

## Why Redact

Raw agent runs can include:

- local filesystem paths
- hostnames and usernames
- process state
- environment values
- auth/cookie headers
- runner prompts and completion payloads
- daemon logs with private workspace context

Publishing those raw files directly would increase leak risk without being
necessary for most public verification.

## Removed Or Rejected File Classes

Public bundles reject or omit:

- raw runner event streams
- raw runner prompts
- raw stdout/stderr captures
- completion and invocation payloads
- daemon logs
- process environment dumps
- pycache files
- unknown archive paths outside the expected evidence prefix

## Redacted Values

Public bundles redact:

- absolute workspace roots
- Windows user homes
- Linux user homes
- desktop hostnames
- authorization headers
- cookie headers
- bearer tokens
- token-like query parameters
- secret assignment values

## What Sanitization Does Not Change

Sanitization should not alter:

- stage-result lineage
- work item ids
- Arbiter verdicts
- terminal result classes
- release versions
- generated metrics
- checksums for public payloads
- release-tag snapshots

If a future sanitizer would need to modify those fields, the bundle should fail
and be reviewed manually.

## Audit Boundary

The public evidence level is E3-E5: sanitized bundles plus verification scripts.
That is enough to validate the published summaries, selected stage envelopes,
manifest hashes, checksums, release targets, and sanitizer policy.

It is not the same as a full raw forensic replay. A raw private audit would be
an E4 process with a trusted reviewer and explicit handling rules. A future
independent audit should state whether it reviewed only public bundles or also
private raw artifacts.

