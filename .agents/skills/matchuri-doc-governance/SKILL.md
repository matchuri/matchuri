---
name: matchuri-doc-governance
description: Govern Matchuri documentation structure and context weight. Use when auditing docs, deciding whether content belongs in docs, GitHub Wiki, AGENTS.md, repo-local skills, or harness scripts, creating a documentation inventory, or checking that tracked docs do not link to ignored local wiki paths.
---

# Matchuri Doc Governance

## Overview

Use this skill to keep Matchuri docs lean. It separates human-facing narrative, durable development contracts, reusable agent workflows, and deterministic validation.

## Classification

Classify each document or proposed addition into exactly one primary bucket.

| Bucket | Meaning | Typical destination |
| --- | --- | --- |
| KEEP | Current development contract or index that must travel with the repo | `docs/` |
| SKILL | Repeated agent workflow or procedural checklist | `.agents/skills/<skill>/SKILL.md` |
| HARNESS | Rule that should be checked mechanically | skill `scripts/`, repo scripts, tests, or CI |
| WIKI | Human-readable project narrative or portfolio explanation | GitHub Wiki |
| REMOVE | Duplicate, stale, or superseded content | Delete after confirming no unique contract |

## Workflow

1. Read root `AGENTS.md` and the closest nested `AGENTS.md`.
2. Run the inventory harness when auditing `docs/`:

   ```powershell
   python .agents\skills\matchuri-doc-governance\scripts\audit_docs.py --root .
   ```

   To refresh the stored first-pass inventory:

   ```powershell
   python .agents\skills\matchuri-doc-governance\scripts\audit_docs.py --root . --output .agents\skills\matchuri-doc-governance\references\current-docs-inventory.md
   ```

3. Treat generated classifications as a first pass, not final truth.
4. Keep `docs/` focused on implementation source of truth, API/data indexes, and ADR-grade decisions.
5. Move repeated procedures into skills instead of making `docs/` longer.
6. Move mechanically checkable rules into harness scripts instead of prose.
7. Move project story, portfolio explanation, and readable summaries into GitHub Wiki.
8. Do not add tracked links to ignored local wiki paths such as `matchuri.wiki/...`.
9. Do not read or search `matchuri.wiki/` unless the current task explicitly asks to create, edit, audit, or move content into the Wiki.

## Keep In Docs

Keep short documents that answer one of these questions:

- What is the current implementation contract?
- Where is the authoritative API, data, backend, or frontend entry point?
- What durable architectural decision prevents repeated debate?
- What domain language must code, tests, and agents share?

Prefer indexes and concise decision records over long tutorial-style prose.

## Convert To Skills

Create or update a repo-local skill under `.agents/skills` when content describes a repeatable agent workflow, such as:

- API contract change flow
- Data model change flow
- Backend feature implementation flow
- Frontend API integration flow
- GitHub Wiki writing flow
- Documentation slimming and drift review

Keep `SKILL.md` concise. Put deterministic operations in `scripts/`.

## Convert To Harness

Prefer a script, test, or CI check when a rule can be verified without human judgment:

- forbidden links in tracked docs
- stale API status entries
- OpenAPI endpoint drift
- schema/index drift
- required docs touched for API or data changes
- oversized docs or duplicated headings

## GitHub Wiki Boundary

GitHub Wiki is a separate human-facing document space. Tracked repo docs may link to the GitHub Wiki URL, but must not link to ignored local paths such as `matchuri.wiki/Home.md`.

Wiki documents should be self-contained and should not use root-relative links back to `docs/`, `backend/`, or `frontend/`.

For ordinary development, API, data, backend, and frontend work, ignore local `matchuri.wiki/`. Use code and `docs/` for implementation truth. Open Wiki files only when producing or revising human-facing Wiki content.

## Reporting

When finishing an audit, report:

- total file count and total size
- largest docs by size
- bucket counts
- immediate edits made
- next migration candidates
