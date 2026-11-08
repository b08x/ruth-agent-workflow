# Plan — Port R.U.T.H to OpenGAP

Goal: turn this repo into a valid, runnable OpenGAP agent reproducing the R.U.T.H suite (ruth + 8 sub-agents, 6 skills, HTIL gates) from `~/.vibe/{agents,prompts,skills}`.

## Solution approach

Fill the existing OpenGAP scaffold at the repo root in place, one concern per step, running `opengap validate -d .` (CLI v0.5.0, installed at `/home/linuxbrew/.linuxbrew/bin/opengap`) after each step so the repo stays valid throughout. Source of truth for content: the Vibe TOMLs, `prompts/ruth.md` + leaf prompts, and the 6 skill directories. Decisions fixed by the grilling session are recorded in `goals/ruth-opengap-port/grilling-decisions.json`; facts in `facts.md`.

Key mappings decided:
- `prompts/ruth.md` decomposes by function: persona → `SOUL.md`, hard constraints/HTIL mandates → `RULES.md`, output schema/task framing → `PROMPT.md`, and the debate procedures → `workflows/*.yaml` (SkillsFlow format — YAML, not markdown).
- Each leaf prompt → that sub-agent's `agents/<name>/SOUL.md`; each TOML's tool enablement → sub-agent `agent.yaml`.
- Vibe allow/denylists → `pre_tool_use` hooks with `fail_open: false` scripts.
- Plannotator gate → `tools/plannotator.yaml` + mandatory workflow step + RULES.md mandate.

## Ordered steps

### 1. Baseline and sources
- Read `~/.vibe/prompts/ruth.md` end-to-end (137 lines; middle section not yet read) and all leaf prompts (`ruth-codebase-scout.md`, `ruth-qmd-scout.md`, five `sfl-docs-*.md` + `sfl-docs-workflow.md.bak`).
- Read all 8 leaf TOMLs fully (tool enablement, disabled lists, permission tables).
- File: none touched.
- Verify: `opengap validate -d .` passes on the untouched scaffold (record baseline output).

### 2. Skills port (`skills/`)
- Copy `doc-style`, `update-docs`, `ruth-voice`, `qmd`, `sfl-technical-writing`, `sift-graph` from `~/.vibe/skills/` into `skills/`, including `references/`, `scripts/`, `templates/`, `examples/`, `output/` support dirs.
- Normalize each SKILL.md frontmatter to the Agent Skills schema: `name` (matches dir, kebab-case), `description` ≤1024 chars, move Vibe-specific frontmatter keys into `metadata:`, add `compatibility: ">=0.1.0"`.
- Remove `skills/example-skill/`.
- Files: `skills/<6 dirs>/**`, delete `skills/example-skill/`.
- Verify: `opengap validate -d .` (validates skill frontmatter, name-matches-dir, description length, instruction size).
- Known tension: `update-docs` SKILL.md is 25,852 chars, above the ~20,000-char guidance the validator may enforce. Resolution order: keep intact first; if the validator rejects it, relocate the body's bulk into `references/` (content preserved, SKILL.md slimmed) — validation wins per the done condition, content is never deleted.

### 3. Sub-agents (`agents/<name>/`)
- Create 8 directories: `codebase-scout`, `qmd-scout`, `sfl-docs-drafter`, `sfl-docs-editor`, `sfl-docs-ideational-judge`, `sfl-docs-interpersonal-judge`, `sfl-docs-textual-judge`, `sfl-docs-workflow` (workflow restored from `.toml.bak`/`.md.bak`).
- Each gets `agent.yaml` (spec_version 0.1.0, name, version 0.1.0, description from the TOML, tool enablement from the TOML's `enabled_tools`) and `SOUL.md` (the prompt body, lightly adapted: strip Vibe-only tool names where an OpenGAP equivalent phrase is needed).
- Carry the source segregation: judges read-only; drafter `write_file` without `edit`; editor `write_file`+`edit`; codebase-scout read-only inspection; qmd-scout `qmd` shell + skill access; workflow full toolset (from .bak).
- Files: `agents/<8>/{agent.yaml,SOUL.md}`.
- Verify: `opengap validate -d .` (referenced agents exist); spot-check descriptions match `facts.md` lines 4-5.

### 4. Root manifest (`agent.yaml`)
- Rewrite: `name: ruth` (version 0.1.0), description from `ruth.toml`, model `glm5-3` preferred / `mistral-medium-latest` fallback / temperature 0.1 / max_tokens 8192, `runtime: {max_turns: 100, timeout: 600}`.
- `skills:` = the six ported skills; `tools: [plannotator]`.
- `agents:` block listing all 8 sub-agents with descriptions + `delegation: {mode: explicit}` each; root `delegation.mode: explicit`.
- `mcp_servers`: `codebase-memory-mcp` stdio, `command: ${CODEBASE_MEMORY_MCP_CMD}`, `args: []`.
- Compliance block: risk_tier standard, human_in_the_loop conditional, escalation_triggers (confidence_below 0.7, error_detected true), override_capability + kill_switch true, recordkeeping structured JSON (carried from scaffold values minus the FINRA-specific framework list).
- Files: `agent.yaml`.
- Verify: `opengap validate -d .`; grep assertions for each fact-2 / fact-6 / fact-12 / fact-14 clause.

### 5. Ruth identity docs (`SOUL.md`, `RULES.md`, `PROMPT.md`, `AGENTS.md`)
- `SOUL.md`: R.U.T.H persona from ruth.md's `<role>` block — SFL-governed documentation agent, Records Uncertainty/Traces History, terminology accountability, bounded uncertainty, confessed euphemisms; identity only, no procedure.
- `RULES.md`: hard constraints — mandatory Plannotator gate before any finalize/apply, writes and edits require human approval, edits proposed as suggestions before application, never treat own output as reviewed, `ask_user_question`-only-when-claims-materially-change rule, escalation on confidence 0.7.
- `PROMPT.md`: ruth.md's "5. Required Output Schema" verbatim + task framing header.
- `AGENTS.md`: replace the placeholder; framework-agnostic fallback summary of workflows and gates (points at workflows/).
- Files: `SOUL.md`, `RULES.md`, `PROMPT.md`, `AGENTS.md`.
- Verify: `opengap validate -d .` (SOUL.md non-empty/content check); manual read against facts line 7-8.

### 6. Workflows (`workflows/`)
- `sfl-docs-debate.yaml` (SkillsFlow): steps `scout` (agent: codebase-scout / qmd-scout), `draft` (agent: sfl-docs-drafter), `judge-x3` (agent: the three judges, cross-examination rounds expressed as step prompts), `gate` (tool: plannotator, `depends_on` judges), `edit` (agent: sfl-docs-editor, condition: gate approved), `validate` (skill: sfl-technical-writing, loop-to-edit note in prompt).
- `collaborative-edit.yaml` (SkillsFlow) from ruth.md's Workflow C: mechanical fixes, proposal formatting, gate on proposal batch, one edit per approved fix.
- Prose specifics (Moves 1-3, budget protocol, deadlocks) embedded as per-step `prompt:` overrides.
- Files: `workflows/sfl-docs-debate.yaml`, `workflows/collaborative-edit.yaml`.
- Verify: `opengap validate -d .` (workflow schema is validated); each fact-9 clause appears in one of the files (grep).
- Risk: workflow schema shape (list-steps in the docs example vs map-steps in README example) — resolve empirically by validating; if the schema is stricter than expected, keep step prompts terse and move long prose into knowledge/.

### 7. Duties (`DUTIES.md`)
- Roles matrix: ruth=orchestrator, sfl-docs-drafter=maker, 3 judges=checkers, sfl-docs-editor=executor, scouts=evidence-gatherers (read-only).
- Conflict matrix: maker/checker, maker/auditor, executor/checker; handoff `document_finalize` requires [maker, checker] with approval; enforcement strict; state isolation full.
- Files: `DUTIES.md`.
- Verify: grep for maker/checker/executor/handoff clauses against fact-10.

### 8. Hooks (`hooks/`)
- Extend `hooks/hooks.yaml` with `pre_tool_use` entries (`fail_open: false`, short timeouts) referencing one shared script per scope: `scripts/check-allowlist.sh` — enforcing ruth (plannotator annotate only on shell), codebase-scout (read-only git + ls/fd/wc/head/tail/cat/stat/file list), qmd-scout (qmd only). Allowlists passed per-agent via hook config or env; conform to the hook I/O JSON protocol.
- Before writing: locate the installed opengap distribution (`brew`/`npm` prefix) and read `hooks.schema.json` + `hook-io.schema.json` from `spec/schemas/` to get the exact protocol (fields, stdin/stdout contract). Fall back to fetching the schema files from the open-gitagent/opengap GitHub repo.
- Keep the scaffold's existing on_session_start/on_error hooks.
- Files: `hooks/hooks.yaml`, `hooks/scripts/check-allowlist.sh` (+ per-scope variants if the schema demands it).
- Verify: `opengap validate -d .` (hooks YAML + referenced scripts exist); a manual hook-script test: echo a sample tool-call JSON into the script, expect block on `rm -rf` and allow on `git log` (fact-11).

### 9. Plannotator tool (`tools/`)
- `tools/plannotator.yaml`: name, description (HTIL gate), version, `input_schema` (file, gate mode args), `output_schema` (decision JSON), `implementation` script `tools/plannotator-gate.sh` wrapping `plannotator annotate <file> --gate --json --require-approval`, `annotations: {requires_confirmation: true, read_only: false, cost: medium}`; graceful degradation: when the CLI is absent the script returns the escalate outcome instead of passing.
- Files: `tools/plannotator.yaml`, `tools/plannotator-gate.sh`.
- Verify: `opengap validate -d .` (tools schema); grep for requires_confirmation/cost (fact-13).

### 10. Compliance artifacts (`compliance/`) and knowledge note
- Rewrite `compliance/risk-assessment.md` for ruth at standard tier (documentation workflow, write-approval control); trim `regulatory-map.yaml`/`validation-schedule.yaml` placeholders to match ruth's posture.
- `knowledge/known-gaps.md` — the single short note (fact-15): 3 dropped skills, web-search gap, update-docs size. Register it in `knowledge/index.yaml` (knowledge schema: documents list).
- Files: `compliance/*`, `knowledge/known-gaps.md`, `knowledge/index.yaml`.
- Verify: `opengap validate -d .` (knowledge index schema); content read against fact-15.

### 11. Final verification sweep (facts, one by one)
- `opengap validate -d .` → exit 0, no errors (fact-1).
- Run the per-fact automated checks as a single scratch verification script (kept out of the repo — session-only): file-existence assertions (facts 3, 4, 9, 11, 13), YAML parses (facts 4, 6, 11, 14), grep content assertions (facts 2, 5, 10, 12, 14), skill frontmatter name==dir (fact 3).
- Facts 7 and 15 are manual-verification facts: present the SOUL.md and known-gaps note content to the user for confirmation.
- Commit the port to the `development` branch when the sweep is green.

## Risks / open questions

- **Workflow schema strictness** (step 6): the two documented examples show different step shapes; resolve empirically. Fallback: minimal YAML + prose in knowledge/.
- **update-docs instruction size** (step 2): pre-decided fallback is relocation to `references/`, never deletion.
- **Sub-agent manifest schema**: validate may require more than name/SOUL.md in `agents/<name>/agent.yaml`; if required fields appear, fill the minimal manifest per schema and rerun.
- **Hook I/O protocol** (step 8): unknown exact JSON contract until schemas are read; the shared-script design isolates this risk to one file.
- **`sfl-docs-workflow` semantics** (step 3): exists only as .bak — may reference superseded Vibe workflow concepts; port with an explicit note in its SOUL.md that it takes instructions from ruth's workflow steps, mirroring the .bak's role.
