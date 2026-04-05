# Release Policy — AK Cognitive OS v3.0
# How framework releases are packaged, tested, and deployed to projects
# Owner: Architect
# Depends on: framework/governance/versioning-policy.md
# Deployment mechanism: scripts/remediate-project.sh

---

## Overview

A framework release is the act of deploying a validated, versioned framework source to one or more active projects. Releases are never automatic — they require a completed pre-release checklist and explicit AK approval before any project is touched. The deployment tool is `scripts/remediate-project.sh`.

---

## Remediation Modes

`scripts/remediate-project.sh` supports three operating modes. The correct mode must be chosen deliberately — the default is `--audit-only`.

| Mode | Flag | What it does |
|---|---|---|
| **Audit Only** | `--audit-only` | Reads the target project and reports all gaps (missing commands, hooks, governance docs, version mismatches) without writing any files. Safe to run at any time. |
| **Safe Remediate** | `--safe-remediate` | Adds missing files and deploys new artifacts. Skips any file that already exists in the target project to avoid overwriting customisation. Does not delete retired commands. |
| **Full Remediate** | `--full-remediate` | Full deployment. Overwrites command files, hook scripts, and settings.json where safe (project data files — `tasks/`, `docs/`, `releases/` — are never overwritten). Removes retired commands. Use when safe-remediate leaves gaps. |

**Rule:** Always run `--audit-only` before any other mode. Do not run `--full-remediate` without first reviewing the `--audit-only` output.

---

## Pre-Release Checklist

Before any project receives a framework deployment, ALL of the following must be true:

- [ ] `bash scripts/validate-framework.sh` exits 0 with no FAIL lines
- [ ] `.ak-cogos-version` is updated to the release version
- [ ] `VERSION=` in `scripts/remediate-project.sh` matches `.ak-cogos-version`
- [ ] `VERSION=` in `scripts/bootstrap-project.sh` matches `.ak-cogos-version`
- [ ] All governance docs for this release are present in `framework/governance/`
- [ ] All new hook scripts are present in `scripts/hooks/` and wired in `project-template/.claude/settings.json`
- [ ] **AK STEP-49 approval gate is cleared** — AK has approved the v3.0 source for project rollout
- [ ] The release is committed to `main` branch (not a feature branch)

If any item is unchecked, the release is blocked. Do not proceed to project deployment.

---

## AK Approval Gate (STEP-49)

The STEP-49 gate is a mandatory hold before any project is touched. It is cleared when:
- All governance docs (STEP-22 through STEP-40) are written and in `framework/governance/`
- All enforcement hooks (STEP-28 through STEP-31) are present and wired
- `bootstrap-project.sh` and `remediate-project.sh` are at v3.0
- `validate-framework.sh` passes with all v3.0 checks active
- AK has explicitly reviewed and signed off on the source

Until STEP-49 is cleared, no project remediation may begin — even if `--audit-only` shows gaps.

---

## Project Deployment Sequence

Projects are remediated in the following order. This sequence is fixed — do not skip ahead. Each project must be fully verified before the next begins.

| Order | Project | Notes |
|---|---|---|
| 1 | Pharma-Base | Clean baseline — best smoke test for v3.0 deployment |
| 2 | forensic-ai | Python `personas/` dir is app code — do not touch |
| 3 | policybrain | `skills/designer.md` duplicate — delete after live run (AK approval required) |
| 4 | mission-control | SESSION STATE was OPEN at last diagnostic — investigate before remediation (AK approval required) |
| 5 | Transplant-workflow | Largest project (50 active tasks) — verify `tasks/todo.md` integrity before run |

---

## Per-Project Deployment Procedure

For each project in the sequence:

**Step 1 — Pre-check**
Read the project's `tasks/todo.md` SESSION STATE. It MUST be CLOSED before remediation begins. Note any active tasks.

**Step 2 — Dry run**
```bash
bash scripts/remediate-project.sh /path/to/project --dry-run --force
```
Review output: confirm correct 20 commands, new hooks listed, retired commands flagged for removal, `design-system.md` placeholder listed.

**Step 3 — Live run**
```bash
bash scripts/remediate-project.sh /path/to/project --force
```
Confirm exit 0.

**Step 4 — Verification**
After live run, verify all of the following in the target project:
- `.claude/commands/` contains exactly 20 files — no more, no fewer
- `scripts/hooks/` contains all hook scripts including `guard-planning-artifacts.sh`
- `.claude/settings.json` has 12 hook entries
- `framework/governance/` contains all 8+ governance docs
- `tasks/design-system.md` placeholder exists
- `.ak-cogos-version` reads the release version (e.g., `3.0.0`)

Only when all verification checks pass may the next project in sequence begin.

---

## Failed Remediation Recovery

If a project remediation fails mid-run (non-zero exit, partial writes, or verification check failures):

1. **Stop immediately.** Do not proceed to the next project in the sequence.
2. Run `--audit-only` on the affected project to assess current state.
3. The Architect reviews the audit output and determines root cause.
4. If the project is in a partially-remediated state, run `--audit-only` to identify remaining gaps, then re-run `--safe-remediate` to fill them without overwriting completed work.
5. If root cause is a bug in `remediate-project.sh`: fix the script, re-run `validate-framework.sh`, and get Architect sign-off before retrying.
6. Record the failure and recovery steps in `tasks/audit-log.md`.
7. Only resume the project sequence after the affected project passes all verification checks.

**Under no circumstances proceed to the next project if the current project has failed verification.**
