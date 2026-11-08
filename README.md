# R.U.T.H. (Records Uncertainty, Traces History)

> "R.U.T.H. (Records Uncertainty, Traces History) is an SFL-governed technical documentation and orchestration agent. It writes, revises, and audits technical documentation (READMEs, API references, changelogs, postmortems, architecture notes) at Target Intensity 9/10 (High Empirical Grounding)."
> — AGENTS.md:3

## What R.U.T.H. Is

R.U.T.H. is an agent that writes documentation by gathering evidence first, drafting second, auditing third, and locking nothing without a human's approval. This repository — `ruth-agent-workflow`, 77 tracked files on the `development` branch across 4 commits (e03fd05, a488530, 9e470d1, f869448) — packages that agent as a project you can clone and drive. Its root manifest names the agent **ruth**, credits author **b08x**, and declares license MIT (agent.yaml:2-6). That manifest is part of a gate stack, not a self-description: it declares plannotator the agent's sole tool — `plannotator annotate --gate --require-approval` (agent.yaml:24-25) — while both workflows carry a human-approval gate step (workflows/sfl-docs-debate.yaml:100-112; workflows/collaborative-edit.yaml:27-39), and a pre_tool_use hook hands ruth's shell to an allowlist that permits `plannotator annotate` only (hooks/hooks.yaml:8-13; hooks/scripts/check-allowlist.sh:62-67).

Those gates enforce a measurable density, not a slogan. Target Intensity 9/10 means at least 9 of every 10 declarative clauses in a drafted document carry their own verification condition — a `path:line` reference, a `#docid`, an exact measure, or an Escape Hatch naming the check that would confirm it (SOUL.md:6; RULES.md:23-24). A clause claiming something the evidence cannot verify must say so openly and name its hatch. That density — 9 of 10 claims self-verifying, in documents whose checkable claims run past 100 — sounds improbable for machine-drafted prose, but it is checkable in this README itself: its sections hold 60+ path:line anchors; sample any section and count declarative clauses against their citations.

Orchestration is how R.U.T.H. reaches that standard. The agent does not write documents alone; it dispatches sub-agents under the two workflow definitions in `workflows/` — `sfl-docs-debate.yaml` for whole-document creation and major rewrites, `collaborative-edit.yaml` for pairing and review (AGENTS.md:6-8). Both workflows share one non-negotiable rule: "Every workflow mandates that no draft or proposal batch is finalized without passing a human-approved Plannotator review gate" (AGENTS.md:11, referencing tools/plannotator.yaml). The eight subagents behind those workflows, the ten steps of the longer one, and that gate are what the rest of this README documents.

## The Agent Suite

The suite is one root agent — **ruth** — plus eight subagents under `agents/`, each carrying its own `agent.yaml` manifest and `SOUL.md` on disk (e.g., agents/sfl-docs-editor/SOUL.md:1); the root manifest lists all eight at agent.yaml:30-62. Roles follow a five-role segregation scheme — orchestrator, maker, checker, executor, evidence_gatherer (DUTIES.md:7-13; role definitions at agent.yaml:101-127, per-agent assignments at agent.yaml:132-148) — whose conflict matrix forbids the failure mode this suite exists to prevent: an agent that drafts documentation cannot audit or judge its own work (DUTIES.md:17-22). A `document_finalize` handoff accordingly requires both maker and checker, with Approval Required: true (DUTIES.md:28-31).

| Agent | Role | Reads / writes | Evidence |
|---|---|---|---|
| **ruth** (root) | entry point | Declares plannotator its sole tool and routes every draft to the human-approval gate; shell allows `plannotator annotate` only | agent.yaml:24-25; sfl-docs-debate.yaml:100-112; collaborative-edit.yaml:27-39; hooks/scripts/check-allowlist.sh:62-67 |
| **codebase-scout** | evidence_gatherer | Read-only evidence gathering: git read subcommands plus non-mutating file inspection (ls, fd, wc, head, tail, cat, stat, file) — no command that writes | agents/codebase-scout/agent.yaml:4; check-allowlist.sh:70-76 |
| **qmd-scout** | evidence_gatherer | Read-only QMD knowledge-base search; qmd CLI only; runs `env -u CI qmd query` because `CI=true` disables the LLM | agents/qmd-scout/SOUL.md:11; check-allowlist.sh:79-85 |
| **sfl-docs-drafter** | maker | Drafts from SFL genre templates; may create files but not edit existing ones | agents/sfl-docs-drafter/SOUL.md:6 |
| **sfl-docs-editor** | executor | Applies consensus fixes as minimal diffs; never runs git | agents/sfl-docs-editor/SOUL.md:6 |
| **sfl-docs-ideational-judge** | checker | Audits process-type coverage: material, mental, relational | agents/sfl-docs-ideational-judge/agent.yaml:4 |
| **sfl-docs-interpersonal-judge** | checker | Audits modality calibration against evidence; returns a Modality Histogram | agents/sfl-docs-interpersonal-judge/SOUL.md:24 |
| **sfl-docs-textual-judge** | checker | Audits theme–rheme progression and genre staging; returns a Staging & Cohesion Map | agents/sfl-docs-textual-judge/SOUL.md:25 |
| **sfl-docs-workflow** | orchestrator | Owns the register and the validation gate; does not draft prose; skills: sfl-technical-writing + qmd | agents/sfl-docs-workflow/SOUL.md:9,19,50-51 |

The three judges share one protocol. Each is a read-only leaf agent (role line at SOUL.md:6 in all three files) that runs a two-move audit — a blind audit first, then cross-examination of the other judges' findings (ideational SOUL.md:18-19; interpersonal SOUL.md:15-16; textual SOUL.md:16-17). That cross-examination is the input the workflows' consensus step consumes.

## Workflows

That consensus step runs inside the two workflows. In `workflows/sfl-docs-debate.yaml` — 142 lines, version 0.1.0 (lines 1-3) — a document is born: the workflow takes `target_path` and a `genre_template` as required inputs, with optional `register_field`, `tenor`, and `mode`, then runs ten steps:

1. **codebase-scout** gathers evidence under a budget of 4 tool calls over 2 files (lines 30-38).
2. **qmd-scout** searches the QMD knowledge base (lines 39-46).
3. **sfl-docs-drafter** drafts the document from the SFL genre template and the scouts' evidence (lines 47-59).
4–6. **The three judges audit the draft** — ideational (step begins at line 60), interpersonal (line 70), textual (line 80) — each running its blind audit, then cross-examination (lines 60-89).
7. **consensus-synthesis** resolves the judges' findings, and its instruction is explicit: "Resolve inter-judge deadlocks strictly using cited code/spec evidence." (lines 90-99)
8. **A Plannotator gate** with `require_approval: true` presents the consensus result for human approval (lines 100-112).
9. **sfl-docs-editor** applies only what that gate approved — the step runs only when `steps.gate.outputs.review_decision == "approved"` (line 119).
10. **validate** runs the sfl-technical-writing Step 5 five-point gate over the edited result, looping back to the editor `on_failure` (lines 125-139).

The ten step ids sit at lines 30, 39, 47, 60, 70, 80, 90, 100, 113, and 125; any step failure escalates to the supervisor (lines 140-142).

In `workflows/collaborative-edit.yaml` (54 lines), pairing and review compress those ten steps into four. The collaborative session itself — the step assigns no sub-agent (lines 14-19) — applies mechanical fixes directly; everything beyond them is annotated as a proposal — "claim -> problem class -> evidence needed -> proposed rewrite" (lines 20-26); the proposal batch passes a Plannotator gate (lines 27-39); and sfl-docs-editor applies only the approved proposals, one edit call per fix, gated on `gate_decision == "approved"` (lines 40-51, condition at line 46). The four steps drop the debate stages, but not the gate — the one stage both workflows share.

## The Plannotator Review Gate

Both workflows converge on the same control point. AGENTS.md:11 mandates it, the root manifest declares plannotator its sole tool (agent.yaml:24-25), and the definition has two parts: `tools/plannotator.yaml` (28 lines) declares three inputs — `file` (required), `result_file`, and `require_approval` — and tools/plannotator-gate.sh (30 lines, executable) implements it by wrapping one command (line 25):

```
plannotator annotate "$FILE" --gate --json --require-approval
```

The gate's semantics are mandatory, not advisory (RULES.md:4-7): the HTIL gate is required; an agent never self-certifies; a denial means folding the feedback back into the work and re-running; and a usage error means fixing the command, not retrying it blindly. The script's failure modes are explicit — when the plannotator CLI is missing, it writes decision "escalate" to the result file (line 19) and to stdout (line 21) and exits 1 (line 22); when the file argument is missing, it exits 2 (lines 11-14). A 30-line shell script decides whether step 8 of a 142-line workflow proceeds; that sounds thin, but every branch of it is specified, and its authority comes from the human answering the approval prompt that `require_approval: true` makes mandatory (tools/plannotator.yaml:13-15), not from the script itself. The shell backs it with an allowlist — `plannotator annotate` only (hooks/scripts/check-allowlist.sh:62-67) — and outside the shell the manifest bounds the remaining routes: plannotator is the sole declared tool (agent.yaml:24-25), and writes require approval (RULES.md:10). No route the manifest declares bypasses the gate.

## Repository Layout

The 77 tracked files (`git ls-files | wc -l`) organize as:

```
agents/                    one directory per subagent: agent.yaml + SOUL.md (agent.yaml:30-62)
workflows/                 sfl-docs-debate.yaml (142 lines); collaborative-edit.yaml (54 lines)
tools/                     plannotator.yaml (28 lines); plannotator-gate.sh (30 lines)
hooks/                     hooks.yaml; scripts/check-allowlist.sh (103 lines)
scripts/                   tracked shell scripts; this README deliberately does not document their contents
compliance/, config/, knowledge/ — tracked directories; their contents are not
                           documented in this README
skills/                    doc-style, qmd, ruth-voice, sfl-technical-writing, sift-graph,
                           update-docs (agent.yaml:16-22)
  skills/sfl-technical-writing/templates/    3 genre templates
goals/                     ruth-opengap-port/
memory/                    MEMORY.md, memory.yaml
top level                  AGENTS.md, PROMPT.md, agent.yaml, SOUL.md, RULES.md, DUTIES.md,
                           .gitignore
```

The root manifest also carries the runtime contract. It declares shell dependencies `qmd,plannotator` (agent.yaml:161) and an MCP server — codebase-memory-mcp — started via the environment variable `CODEBASE_MEMORY_MCP_CMD`, brace-templated at agent.yaml:71-74; that variable's definition is Rationed Unknown 3 below. The manifest further declares that compliance output is retained 6 years, logged as structured_json, immutable (retention at agent.yaml:91, log contents at :92-97, immutable at :98) — a declaration I record as such because I cannot name an in-repo component that enforces that retention on disk. Escape Hatch: identify the enforcement mechanism.

## Installation

Installation runs through one CLI, OpenGAP: install it, validate this repository against its port goal, then run it. One repository dependency ships beside it — qmd, installed in the callout below — and the remaining declared shell dependency, plannotator (`qmd,plannotator`, agent.yaml:161), has no documented installation; Rationed Unknown 2 below records exactly how its gate fails without it. The OpenGAP facts in this section come from the upstream OpenGAP docs (web; source: github.com/open-gitagent/opengap README.md and docs.md, via Context7 /open-gitagent/opengap), marked inline as web evidence; the repository facts keep their path:line cites.

### 1. Install OpenGAP

```
npm install -g @open-gitagent/opengap
```

The install requires Node.js and npm (upstream OpenGAP docs, web). Verify it with `opengap --version` — the upstream README documents 0.3.1 — and note that the install adds `gitagent` as an alias: every opengap command runs unchanged as gitagent (upstream OpenGAP docs, web).

### 2. Validate this repository

```
opengap validate -d .
```

The upstream docs enumerate what the validator checks (web): agent.yaml, against a JSON schema — every referenced skill, tool, and agent must exist; SOUL.md — required to be non-empty; skills — valid frontmatter, a name matching the directory, and bounds on description length and instruction size; hooks — valid YAML, with referenced scripts required to exist; and tools — a valid YAML schema. The `-c/--compliance` flag adds regulatory checks: risk tier, human-in-the-loop coverage for high/critical tiers, and audit logging (upstream OpenGAP docs, web). This repository sets that command as its own port goal: a valid, clone-and-run OpenGAP agent — `opengap validate -d .` exiting clean (goals/ruth-opengap-port/goal.md:5). The goal's done condition spells the check out further — the command exits zero with no errors, and every fact in facts.md with automated verification passes its check, with facts 7 and 15 confirmed manually (goal.md:15). This README has not re-run the validation; Rationed Unknown 1 records the check.

### 3. Run the agent

```
opengap run -d .
```

For the run command, either `-r/--repo` or `-d/--dir` is required (upstream OpenGAP docs, web). The adapter flag `-a/--adapter` defaults to claude; the upstream docs show github, lyzr, git (auto-detected), and prompt as the other adapters (web). Further flags per the same docs (web): `-b/--branch`; `-p/--prompt <query>` for one-shot runs; `--session-id` and `--resume` on the claude adapter; and `--workspace`, `--refresh`. Once the repository is pushed, `opengap run -r <repo-url>` runs it for anyone with the CLI (upstream OpenGAP docs, web); whether it passes `opengap validate -d .` on a fresh clone is Rationed Unknown 1.

```
opengap run -r <repo-url>
```

> **qmd dependency.** The qmd-scout subagent queries markdown knowledge bases through the qmd CLI — `qmd query "question"`, `qmd search "keywords"`, `qmd get "#abc123"` (skills/qmd/SKILL.md:128-133), and `qmd status` (skills/qmd/SKILL.md:19,123) — and it is one of the two declared shell dependencies (agent.yaml:161). Install it from upstream (skills/qmd/SKILL.md:19-26):
>
> ```
> git clone https://github.com/b08x/qmd.git
> cd qmd && npm install && npm link
> ```

## Shell Discipline

R.U.T.H.'s shell restrictions are enforced, not requested. hooks/hooks.yaml registers three hooks — `on_session_start`, `pre_tool_use`, and `on_error` (lines 1-19) — and in `hooks/scripts/`, check-allowlist.sh (103 lines) enforces per-agent read-only shells: codebase-scout's shell allows git read subcommands plus non-mutating file inspection (ls, fd, wc, head, tail, cat, stat, file) — no command that writes (check-allowlist.sh:70-76); qmd-scout's allows the qmd CLI only (check-allowlist.sh:79-85); and ruth's own shell allows `plannotator annotate` only (check-allowlist.sh:62-67). One environment quirk matters when driving qmd-scout manually: `CI=true` disables the LLM inside qmd, so the scout runs `env -u CI qmd query` to strip it (agents/qmd-scout/SOUL.md:11). Each session runs inside bounds the root manifest declares: max_turns 100 and timeout 600, unit undeclared in the manifest (agent.yaml:64-66); separately, every shell call passes a 5-second pre_tool_use hook check before it runs (hooks.yaml:12).

## Negative Capability & 9 Rationed Unknowns

What the suite does not do is part of its design, stated as plainly as what it does. The orchestrator, sfl-docs-workflow, owns the register and the validation gate but does not draft prose (agents/sfl-docs-workflow/SOUL.md:9,19). No judge writes — the three judges are read-only leaf agents (ideational SOUL.md:6,18-19; interpersonal SOUL.md:6,15-16; textual SOUL.md:6,16-17). The drafter may create files but cannot edit existing ones (agents/sfl-docs-drafter/SOUL.md:6). The editor applies fixes but never runs git (agents/sfl-docs-editor/SOUL.md:6). No draft or proposal batch finalizes without a human-approved gate (AGENTS.md:11), and no agent self-certifies past a denial — denial feedback is folded back and the gate re-run (RULES.md:4-7). Memory carries a declared bound, not an enforced one: MEMORY.md states "Max 200 lines" (memory/MEMORY.md:3); I cannot name a component that enforces it. There is no package.json, Makefile, justfile, or Taskfile among the 77 tracked files; installation runs through the OpenGAP and qmd CLIs documented above — plus plannotator, a declared shell dependency whose installation this repo does not document (Rationed Unknown 2). This README's own density stays checkable the way its opening states: 60+ path:line anchors across its nine sections, in a document whose checkable claims run past 100.

Beyond those bounds I record nine rationed unknowns. Each is a rationed uncertainty — not a verified fact — and each names the exact act that would resolve it (its Escape Hatch):

1. The OpenGAP runtime now has a documented install — `npm install -g @open-gitagent/opengap` (upstream OpenGAP docs, web) — but this README has not re-run `opengap validate -d .` against this repository, so the port goal's clean exit (goals/ruth-opengap-port/goal.md:5) is recorded as a goal, not verified here. **Escape Hatch:** run `opengap validate -d .` with the 0.3.1 CLI on a fresh clone and record the exit code.
2. The plannotator CLI's installation is undocumented in every file I read. When the CLI is missing, plannotator-gate.sh writes decision "escalate" to the result file (:19) and to stdout (:21) and exits 1 (:22) — the human review the annotate call would have prompted never happens (tools/plannotator-gate.sh:16-23). **Escape Hatch:** document the upstream install.
3. The environment variable `CODEBASE_MEMORY_MCP_CMD` is referenced (agent.yaml:73) and defined in none of the 77 tracked files I read; a grep across those files would close the question. **Escape Hatch:** `git grep -ln CODEBASE_MEMORY_MCP_CMD` across the 77 tracked files, then document the MCP launch command.
4. The Python scripts in skills/sift-graph — sift_graph.py, sift_graph_crewai.py, sift_graph_mcp.py — have no dependency manifest, and I could not verify that they run. **Escape Hatch:** execute them against a target repo with dependencies pinned.
5. The model values that commit a488530 replaced are not reconstructed here. **Escape Hatch:** `git show a488530^:agent.yaml`.
6. Of the 6 skills the root manifest mounts (agent.yaml:16-22), only 3 genre templates exist — in skills/sfl-technical-writing/templates/ — and agents/sfl-docs-workflow/SOUL.md:63 mentions adapting staging for API reference, troubleshooting, and security docs, but no template files for those genres exist. **Escape Hatch:** author the additional template files.
7. agent.yaml:6 declares an MIT license, but no LICENSE file is tracked. **Escape Hatch:** add a LICENSE file to match the declaration.
8. `examples/`, `examples/scenarios/`, and `memory/archive/` exist as empty directories (0 tracked files); their intended use is undocumented. **Escape Hatch:** document them or remove them.
9. The goal statement quotes its payload counts — "the 15 accepted, testable outcomes" (goal.md:9) and "the approved 11-step execution plan" (goal.md:10) — but facts.md and plan.md are not audited line-by-line here. **Escape Hatch:** audit facts.md and plan.md.

## License

agent.yaml:6 declares `license: MIT`. No LICENSE file exists among the 77 tracked files — the declaration and the repository contents do not currently match; Rationed Unknown 7 above records the fix.
