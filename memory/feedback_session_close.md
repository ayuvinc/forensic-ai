---
name: do not close session independently after merge
description: Architect must not close the session on its own after merging a feature branch — only close when AK explicitly asks
type: feedback
---

Do not close the session (update SESSION STATE to CLOSED, write next-action.md, emit session-close handoff) automatically after merging a feature branch to main.

**Why:** Architect closing the session mid-conversation is disruptive — AK may want to continue working in the same session after a merge. Session close is AK's call, not a consequence of a merge completing.

**How to apply:** After merging a branch, stop at the merge commit and HANDOFF envelope. Do not update SESSION STATE, do not write next-action.md as a session-close artifact. Wait for AK to explicitly invoke /session-close or ask you to close the session.
