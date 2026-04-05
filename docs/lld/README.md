# Low-Level Design (LLD) Directory

This directory contains detailed implementation designs for individual features.

## When to Create an LLD

- Feature touches 3+ files
- Business rules or permissions are involved
- Multiple people need to understand the design
- The feature will be demoed or released to users
- You're unsure about scope or approach

## When NOT to Create an LLD

- Single-file bug fix
- Config change (linting, CI, dependency update)
- Copy/text change with no architectural impact
- Trivial feature under 2 files with no business rules

## How to Use

1. Copy `feature-template.md` to `<feature-name>.md`
2. Fill in sections relevant to your feature (skip irrelevant ones)
3. Set metadata header: Status: draft, Source: appropriate value
4. Get user confirmation before implementing
5. Update Status to confirmed after review

## Template

See [feature-template.md](feature-template.md) for the standard LLD format.
