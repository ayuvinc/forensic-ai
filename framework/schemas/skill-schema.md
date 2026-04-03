# Skill Schema
# AK Cognitive OS
# validation: markdown-contract-only | machine-validated

---

## Purpose

Defines the required structure for every skill in `skills/`.
A skill is a named slash command that performs a specific workflow action
(not a persona — no role identity, just a task runner).

---

## Skill vs Persona Distinction

| Aspect | Persona | Skill |
|---|---|---|
| Identity | Named role (architect, qa, etc.) | Named action (session-open, etc.) |
| Job | Ongoing judgment within a domain | Single-purpose operation |
| Activation | `/persona-name` | `/skill-name` |
| Output | Persona-specific artifacts | Action-specific artifacts |

---

## Required Files Per Skill

Every skill directory must contain:

```
skills/{name}/
├── claude-command.md    ← Claude slash command definition
└── codex-prompt.md      ← Codex equivalent (if Codex can run this skill)
```

Note: skills do not have a `schema.md` — their output contract is defined in `claude-command.md`.

---

## claude-command.md Required Sections

```
# /{skill-name}

## WHO YOU ARE
[One sentence: role identity — "You are the {name} agent in AK Cognitive OS. Your only job is: ..."]

## YOUR RULES
CAN:
- [permitted actions]

CANNOT:
- [forbidden actions]

BOUNDARY_FLAG:
- [stop conditions — when to emit BLOCKED and halt]

## ON ACTIVATION - AUTO-RUN SEQUENCE
[Numbered steps: resolve paths → validate inputs → validate artifacts → execute → build output]

## TASK EXECUTION
Reads: [files this skill reads]
Writes: [files this skill writes]
Checks/Actions:
- [ordered checks and actions]

Validation contracts:
- Required status enum: PASS|FAIL|BLOCKED
- Required envelope fields: run_id, agent, origin, status, timestamp_utc, summary, failures[], warnings[], artifacts_written[], next_action

Required extra fields for this agent:
  [skill-specific extra fields]

## HANDOFF
[Required output envelope — YAML format including origin: claude-core]
```

---

## Validation Rules

- Missing `WHO YOU ARE` → `SCHEMA_VIOLATION: skill identity undefined`
- Missing `YOUR RULES` with BOUNDARY_FLAG → skill has no stop condition, unsafe to deploy
- Missing `ON ACTIVATION` → skill has no execution sequence
- Missing `TASK EXECUTION` → consuming persona cannot verify what skill reads/writes
- Missing output envelope in HANDOFF → `SCHEMA_VIOLATION: envelope missing`
- Missing `origin:` in HANDOFF YAML → `SCHEMA_VIOLATION: origin field missing`
