# Artifact Ownership — AK Cognitive OS v3.0
# Ownership matrix: who creates, who reads, who may update, who gates each artifact
# Owner: Architect
# Persona names match .claude/commands/ exactly — 20 commands only

---

## How to Read This Table

| Column | Meaning |
|---|---|
| Artifact Name | Matches the artifact name in `artifact-map.md` — row counts must be equal |
| Owner Persona | The persona that creates this artifact and is responsible for its contents |
| Reader Personas | Personas that read this artifact as input to their work |
| Writer Personas | Personas permitted to update this artifact after it is created |
| Gate Persona | The persona that must sign off before this artifact is consumed downstream — `none` where no formal gate applies |

All persona names are from `.claude/commands/`. Specialist sub-personas (e.g., researcher-business) are referenced via their router parent (researcher, compliance) unless they have their own command file.

---

## Ownership Matrix

| Artifact Name | Owner Persona | Reader Personas | Writer Personas | Gate Persona |
|---|---|---|---|---|
| problem-definition.md | ba | architect, junior-dev, qa, ux, designer, researcher | ba | architect |
| current-state.md | ba | architect, junior-dev | ba | architect |
| assumptions.md | ba | architect, junior-dev, qa | ba, architect | architect |
| risk-register.md | risk-manager | architect, qa, security-sweep, compliance | risk-manager, ba, architect | architect |
| scope-brief.md | architect | architect, ba, junior-dev, qa, ux, designer | architect, ba | architect |
| ba-logic.md | ba | architect, junior-dev | ba | architect |
| decision-log.md | architect | architect, ba, junior-dev | architect, ba | architect |
| hld.md | architect | architect, junior-dev, qa, ux, designer | architect | architect |
| lld/feature-template.md | architect | junior-dev, qa | architect | architect |
| todo.md | architect | architect, ba, junior-dev, qa, ux, designer, session-open, session-close | architect, junior-dev, qa, session-open, session-close | architect |
| next-action.md | architect | architect, session-open, session-close | architect, session-close | architect |
| ux-specs.md | ux | architect, junior-dev, designer | ux | architect |
| design-system.md | designer | junior-dev, architect, ux | designer, ux | architect |
| codex-review.md | codex-prep | codex-read, architect | codex-prep | codex-read |
| teaching-log.md | teach-me | architect, junior-dev | teach-me | none |
| traceability-matrix.md | qa | architect | qa | architect |
| release-truth.md | architect | architect, qa | architect | architect |
| audit-log.md | audit-log | architect, session-open, session-close | audit-log | none |
| lessons.md | lessons-extractor | architect, session-open | lessons-extractor | none |
| channel.md | architect | architect, ba, junior-dev, qa, ux, designer, check-channel | architect, ba, junior-dev, qa, ux, designer, session-open, session-close | none |
| framework-improvements.md | lessons-extractor | architect | architect, lessons-extractor | architect |

**Row count: 21** (must match `artifact-map.md` row count)

---

## Enforcement Notes

- **Owner** = the only persona permitted to create this artifact from scratch. If another persona needs to update it, they must be listed in Writer Personas.
- **Gate Persona** = the persona whose sign-off is recorded (in `channel.md` or via hook) before the artifact is treated as accepted by downstream personas. Where the gate is `none`, the artifact is consumed without formal sign-off.
- **CAN/CANNOT alignment**: Writer Personas here must not contradict the `CANNOT` section of any listed persona's command contract. If a conflict is found, the persona command contract takes precedence and this file must be updated.

---

*See `framework/governance/artifact-map.md` for paths, formats, and lifecycle stage assignments.*
*See individual persona contracts in `.claude/commands/` for CAN/CANNOT file-path restrictions.*
