# Duties

System-wide segregation of duties (SOD) policy for R.U.T.H. and associated sub-agents.

## Roles

| Role | Agent | Permissions | Description |
|------|-------|-------------|-------------|
| **orchestrator** | `ruth`, `sfl-docs-workflow` | `create`, `submit`, `execute`, `report` | Coordinates workflows, registers, and dispatches sub-agents; enforces validation gates. |
| **maker** | `sfl-docs-drafter` | `create`, `submit` | Drafts document proposals and initial text from SFL genre templates at Target Intensity 9/10. Holds `write_file` without `edit`. |
| **checker** | `sfl-docs-ideational-judge`, `sfl-docs-interpersonal-judge`, `sfl-docs-textual-judge` | `review`, `audit`, `report` | Audits drafts independently across ideational, interpersonal, and textual lenses. Strictly read-only; no file editing or agent spawning. |
| **executor** | `sfl-docs-editor` | `execute` | Applies deduplicated consensus diffs to target documents. Holds `write_file` and `edit`. |
| **evidence_gatherer** | `codebase-scout`, `qmd-scout` | `review`, `audit` | Gathers factual evidence from codebases and knowledge bases. Strictly read-only; no file modification. |

## Conflict Matrix

No single agent may hold both roles in any conflicting pair:

- **maker / checker**: An agent that drafts documentation cannot audit or judge its own work.
- **maker / auditor**: An agent that drafts documentation cannot perform independent audit functions.
- **maker / executor**: An agent that creates a draft cannot act as the final editing executor applying consensus fixes.
- **executor / checker**: An agent applying fixes cannot audit or certify the resulting diffs.

## Handoff Workflows

Critical actions require sequential multi-role participation:

- **Action:** `document_finalize`
  - **Required Roles:** `maker`, `checker` (sequential handoff: drafter creates draft, three metafunction judges audit and agree on consensus)
  - **Approval Required:** `true` (mandatory human-approved Plannotator review gate before finalization or applying fixes)
  - **Execution:** Once approved through the Plannotator gate, `executor` applies consensus fixes, followed by five-point SFL validation.

## Isolation Policy

- **State isolation:** `full` (Child sub-agent sessions do not share conversation history or mutable state; each sub-agent runs with a fresh context).
- **Credential segregation:** `separate` (Scout and leaf sub-agents operate under isolated tool surfaces and distinct allowlists).

## Enforcement

`strict` (SOD violations and unauthorized cross-role actions are treated as blocking errors).
