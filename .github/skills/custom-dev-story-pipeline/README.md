# Dev Story Pipeline

Automated epic implementation through independent dev and review subagent teams.

## Purpose

Process an entire epic's stories through development → review → fix → done with automatic sprint status synchronization.

## What It Does

1. Takes an epic identifier
2. Finds all stories in that epic
3. For each story in sequence:
   - Spawns dev subagent (Amelia + bmad-dev-story)
   - Spawns review subagent (Amelia + bmad-code-review)  
   - Spawns fix subagent if critical issues found
   - Updates sprint status after each phase
4. Marks epic complete when all stories done
5. Generates summary report

## How to Use

```
Run custom-dev-story-pipeline for epic-authentication
```

The workflow handles everything automatically. It will stop and report if any story fails.

## Prerequisites

- Epic file exists in planning or implementation artifacts
- Epic contains list of stories
- All story files exist
- Sprint status YAML exists and is valid
- Epic status is ready for development

## Output

- Review reports: `{implementation_artifacts}/reviews/story-{id}-review.md`
- Summary report: `{implementation_artifacts}/epic-{id}-summary.md`
- Updated sprint-status.yaml with all stories marked done
- Updated epic file with done status

## Error Handling

Pipeline stops on first error. Sprint status shows exactly where it stopped. Re-run the pipeline to resume (completed stories are skipped).
