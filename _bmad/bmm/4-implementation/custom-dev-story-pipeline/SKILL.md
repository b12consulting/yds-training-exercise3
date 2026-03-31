---
name: custom-dev-story-pipeline
description: Automated epic implementation pipeline that orchestrates independent agent teams to develop, review, and fix each story sequentially. Updates sprint status at every phase and ensures all code is reviewed before completion.
---


# Dev Story Pipeline

## Overview

Automated epic implementation pipeline that orchestrates story development, code review, and quality fixes through independent subagent teams. Processes all stories in an epic sequentially, updating sprint status at each phase, ensuring nothing ships without review.

**Use when:** You have a fully planned epic with story files ready and want automated implementation with built-in quality gates.

**Args:** Epic identifier (e.g., "epic-1", "user-authentication")

## Desired Outcomes

When this workflow completes successfully:

1. **Every story implemented** — All stories in the epic coded and working
2. **Every story reviewed** — Code review findings captured for each story
3. **Critical issues fixed** — Blocking/critical review findings addressed
4. **Sprint status synchronized** — Sprint plan reflects accurate progress at every step
5. **Epic marked complete** — Epic status updated to done
6. **Audit trail preserved** — Development and review reports saved for each story

## Workflow Architecture

This workflow uses **independent subagents** for each phase to prevent context pollution and ensure clean handoffs:

- **Dev Subagent** — Fresh Amelia instance per story, runs `bmad-dev-story`, returns completion status
- **Review Subagent** — Fresh Amelia instance per story, runs `bmad-code-review`, returns findings with severity
- **Fix Subagent** — Fresh Amelia instance when needed, fixes critical/blocking issues, returns fix status

Each subagent is stateless. The orchestrator coordinates sequence, status updates, and error handling.

## Execution Flow

### Phase 1: Epic Discovery & Validation

1. **Load configuration** via `bmad-init` — resolve `{planning_artifacts}` and `{implementation_artifacts}` paths
2. **Locate epic file** — search for epic identifier in artifacts directories
3. **Parse epic structure** — extract story list, validate epic status is ready
4. **Load sprint plan** — validate `sprint-status.yaml` exists and is accessible
5. **Pre-flight check** — confirm all story files exist before starting

If validation fails, stop and report missing/invalid components.

### Phase 2: Story Processing Loop

For each story in the epic (sequential order):

#### Step 2.1: Development Phase

1. **Update sprint status** — mark story as `in-progress` in sprint-status.yaml
2. **Spawn Dev Subagent:**
   - **Persona:** Amelia (Senior Developer)
   - **Task:** Execute `bmad-dev-story` with story file path
   - **Expected output:** Implementation complete, working code, any blockers encountered
   - **Timeout:** Reasonable for story complexity (default: no timeout, let dev complete)
3. **Handle dev outcome:**
   - Success → proceed to review
   - Failure → stop pipeline, report error, preserve sprint status for resume
4. **Update sprint status** — mark story as `review` (ready for review)

#### Step 2.2: Review Phase

1. **Spawn Review Subagent:**
   - **Persona:** Amelia (now in reviewer mode)
   - **Task:** Execute `bmad-code-review` on code changed in this story
   - **Expected output:** Review findings categorized by severity (critical, major, minor), file locations
   - **Timeout:** Reasonable for review scope
2. **Capture findings** — save review report to `{implementation_artifacts}/reviews/story-{id}-review.md`
3. **Assess severity:**
   - **Critical/Blocking issues** → proceed to fix phase
   - **Minor/Informational only** → mark story complete
   - **Review failed** → stop pipeline, report error

#### Step 2.3: Fix Phase (Conditional)

Only runs if critical/blocking issues found:

1. **Update sprint status** — mark story as `in-progress` (fixing review issues)
2. **Spawn Fix Subagent:**
   - **Persona:** Amelia (developer mode)
   - **Task:** Fix critical/blocking issues from review findings
   - **Context:** Story file + review report
   - **Expected output:** Fixes applied, confirmation of resolution
3. **Handle fix outcome:**
   - Success → mark story complete
   - Failure → stop pipeline, report error

**Note:** No re-review after fixes. Trust the fix subagent addressed findings. Re-review can be a future enhancement.

#### Step 2.4: Story Completion

1. **Update sprint status** — mark story as `done`
2. **Log completion** — timestamp, final status
3. **Continue to next story**

### Phase 3: Epic Finalization

After all stories complete:

1. **Update epic status** — mark epic as `done` in epic file
2. **Update sprint plan** — set epic status to `done`, update timestamp
3. **Generate summary report:**
   - Stories completed
   - Total review findings
   - Stories requiring fixes
   - Time metrics if available
4. **Save summary** to `{implementation_artifacts}/epic-{id}-summary.md`
5. **Report completion** to user with summary highlights

## Error Handling

**On any error:**
1. **Stop pipeline immediately** — don't continue to next story
2. **Preserve state** — sprint status shows exactly where pipeline stopped
3. **Report error context:**
   - Which story failed
   - Which phase (dev/review/fix)
   - Error message from subagent
   - How to resume (re-run pipeline, will skip completed stories)
4. **Exit cleanly**

**Resumability:** Pipeline can detect completed stories and skip them on re-run. Sprint status is source of truth.

## Sprint Status Format

Expected structure in `sprint-status.yaml`:

```yaml
epic:
  - id: epic-1
    stories:
      - id: story-1
        status: done  # States: ready-for-dev, in-progress, review, done
      - id: story-2
        status: in-progress
```

Pipeline updates status at each transition.

## Configuration Requirements

Requires these config variables from `bmad-init`:

- `{planning_artifacts}` — where epics and architecture live
- `{implementation_artifacts}` — where stories, reviews, summaries are saved
- `{communication_language}` — for user-facing messages
- `{document_output_language}` — for generated reports

## Usage Examples

**Basic:**
```
Run custom-dev-story-pipeline for epic-1
```

**With explicit epic identifier:**
```
/custom-dev-story-pipeline epic-user-authentication
```

## Success Criteria

Pipeline is successful when:
- All stories transition from `ready-for-dev` → `done`
- Epic status updated to `done`
- Review reports exist for every story
- No errors encountered
- User receives completion summary

## Principles

- **Isolation over continuity** — Each subagent gets fresh context to prevent confusion
- **Status first** — Sprint plan is always accurate, never stale
- **Fail fast** — Stop on first error, don't accumulate failures
- **Trust the agents** — Subagents are experts, don't micromanage their process
- **Audit everything** — Every dev and review phase generates a report

## Limitations & Future Enhancements

**Current:**
- No re-review after fixes (trust fix subagent)
- Sequential only (one story at a time)
- No parallel story processing
- No partial epic processing (all or nothing)

**Future:**
- Re-review cycle after fixes with convergence limit
- Parallel story processing for independent stories
- Resume from specific story
- Epic stage phases (foundation stories first, then features)
