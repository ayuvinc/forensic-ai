# /repo-cleanup

You are acting as Architect for this repository cleanup session.
Do not start any feature work — this session is infrastructure/housekeeping only.

## Goals
1. Make .gitignore comprehensive
2. Prune stale and redundant files (show me the plan first, then execute)
3. Consolidate the folder structure so it is clean and navigable
4. Update README to reflect current state (version, folder structure, removed files)
5. Commit and push all changes to GitHub

## Step 1 — Audit (do this first, output only, no changes yet)
Run the following and show me the results:
a) `git status` — list all untracked files
b) `ls -1` at root — list every root-level item
c) Find any *.bak, *.bak[0-9]*, *.textClipping, *.log at any depth
d) Find any files that look like: notes, drafts, WIP, scratch, old, unused, temp, archive candidates
e) Check .gitignore for missing common patterns (*.bak, *.textClipping, .DS_Store, *.log, .env*)

## Step 2 — Restructure plan (show me, wait for my approval before executing)
Propose how to consolidate the root-level folder structure:
- Identify documentation folders that could live under docs/ (guides/, examples/, harnesses/, reference docs at root)
- Identify any files at root that should move to a subfolder
- List what would stay at root (README, QUICKSTART, CHANGELOG, RELEASE_NOTES, CLAUDE.md, .gitignore, LICENSE, etc.)
- For each proposed move: show `git mv <from> <to>` — preserve git history, no re-creates

## Step 3 — Pruning plan (show me, wait for my approval before executing)
List every file proposed for deletion with a one-line reason why it is safe to delete.
Categories to check:
- Backup files (.bak, .bak[0-9]*)
- Stale planning docs (superseded, empty, or describes completed work with no future value)
- Redundant files (content already captured elsewhere)
- WIP/scratch files
- Auto-generated files that can be regenerated

## Step 4 — Execute (only after I approve Steps 2 and 3)
a) Update .gitignore with any missing patterns
b) Run git mv operations for restructure (in one commit)
c) Delete pruned files (git rm) (in one commit)
d) Update README to reflect current version, new folder structure, removed files
e) Commit and push to GitHub

## Constraints
- Never delete files I have not approved for deletion
- Prefer git mv over delete+recreate to preserve history
- Do not restructure schemas/, framework/, validators/, scripts/ — those have internal cross-references
- Do not touch any tasks/, releases/, or memory/ content
- Update any script echo messages or path references broken by the restructure
- One commit per logical change — restructure, prune, and docs update are three separate commits
