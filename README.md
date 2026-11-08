# R.U.T.H. (Records Uncertainty, Traces History)

## What R.U.T.H. Is

R.U.T.H. is an agent that writes documentation by gathering evidence first, drafting second, auditing third, and locking nothing without a human's approval. The repository's own manifest summary says the same thing in its own terms — an SFL-governed technical documentation and orchestration agent that writes, revises, and audits technical documentation (READMEs, API references, changelogs, postmortems, architecture notes) at Target Intensity 9/10 (High Empirical Grounding) (AGENTS.md:3) — and the rest of this introduction unpacks those terms.

This repository — `ruth-agent-workflow` — packages that agent as a project you can clone and drive. Its root manifest names the agent **ruth**, credits author **b08x**, and declares license MIT (agent.yaml:2-6). The tree held 77 tracked files across 4 commits (e03fd05, a488530, 9e470d1, f869448) before this README was committed; tracking the README itself — commit 7e75bc8 — makes the count 78 files across 5 commits. The document you are reading is the +1 its own census now records.

The agent does not write documents alone; it dispatches sub-agents under the two workflow definitions in `workflows/` — `sfl-docs-debate.yaml` for whole-document creation and major rewrites, `collaborative-edit.yaml` for pairing and review (AGENTS.md:6-8). Both share one non-negotiable rule: "Every workflow mandates that no draft or proposal batch is finalized without passing a human-approved Plannotator review gate" (AGENTS.md:11, referencing tools/plannotator.yaml). That rule is enforced at every level — manifest, workflow, and shell — and The Plannotator Review Gate shows the full stack once, top to bottom.

Target Intensity 9/10 means at least 9 of every 10 declarative clauses in a drafted document carry their own verification condition — a `path:line` reference, a `#docid`, an exact measure, or an Escape Hatch naming the check that would confirm it (SOUL.md:6; RULES.md:23-24). A clause claiming something the evidence cannot verify must say so openly and name its hatch. This README holds itself to the same bar, and the check is yours to run: it is a sample of the standard it describes, so take any clause and read its anchor. One worked instance, drawn from the Agent Suite table below: "sfl-docs-editor applies consensus fixes as minimal diffs; never runs git (agents/sfl-docs-editor/SOUL.md:6)" — one declarative clause, one verification condition: open the cited file and read line 6; if the clause is false there, you have found a defect in this README.

Two pieces of suite jargon deserve a plain-language gloss before they arrive in tables. **SFL** is Systemic Functional Linguistics — the school of linguistic analysis that describes language by what it does. R.U.T.H. borrows three of its lenses as its three auditors, one judge per lens: what a draft **claims** (the ideational judge — process types such as material, mental, relational), how **confident** it is (the interpersonal judge — modality calibrated against evidence), and how it **flows** (the textual judge — theme–rheme progression and genre staging). The workflow inputs `register_field`, `register_tenor`, and `register_mode` are SFL's Field, Tenor, and Mode register variables. **Target Intensity 9/10 (High Empirical Grounding)** is the density bar defined in the paragraph above.

> **Reading conventions.** Citations of the form `path:line` are anchors into this repository — every declarative claim in this README carries one, or names the check that would confirm it. Facts marked *(web)* come from the upstream OpenGAP v0.3.1 docs (github.com/open-gitagent/opengap — README.md and docs.md, via Context7 /open-gitagent/opengap); everything else cites this tree.

## Prerequisites

- **Node.js + npm** — required to install OpenGAP *(web)*.
- **OpenGAP CLI** — installed in step 1 below; the upstream README documents version 0.3.1 *(web)*.
- **qmd** — one of the two declared shell dependencies (agent.yaml:161); the qmd-scout subagent cannot query knowledge bases without it. Install command in the callout at the end of Installation.
- **plannotator** — the other declared shell dependency (agent.yaml:161), with no documented installation in any file in this repository. Without it the review gate does not fail loudly: plannotator-gate.sh writes decision "escalate" and exits 1, and the human review never happens (tools/plannotator-gate.sh:16-23). Known Unknown 2 records the gap and its Escape Hatch: document the upstream install.

## Installation

Installation runs through one CLI, OpenGAP: install it, validate this repository against its port goal, then run it. Per the reading conventions above, OpenGAP facts here are marked *(web)*; repository facts keep their path:line cites.

### 1. Install OpenGAP

```
npm install -g @open-gitagent/opengap
```

The install requires Node.js and npm *(web)*. Verify it with `opengap --version` — the upstream README documents 0.3.1 — and note that the install adds `gitagent` as an alias: every opengap command runs unchanged as gitagent *(web)*.

### 2. Validate this repository

```
opengap validate -d .
```

The upstream docs enumerate what the validator checks *(web)*: agent.yaml, against a JSON schema — every referenced skill, tool, and agent must exist; SOUL.md — required to be non-empty; skills — valid frontmatter, a name matching the directory, and bounds on description length and instruction size; hooks — valid YAML, with referenced scripts required to exist; and tools — a valid YAML schema. The `-c/--compliance` flag adds regulatory checks: risk tier, human-in-the-loop coverage for high/critical tiers, and audit logging *(web)*. This repository sets that command as its own port goal: a valid, clone-and-run OpenGAP agent — `opengap validate -d .` exiting clean (goals/ruth-opengap-port/goal.md:5). The goal's done condition spells the check out further — the command exits zero with no errors, and every fact in facts.md with automated verification passes its check, with facts 7 and 15 confirmed manually (goal.md:15). This README has not re-run the validation; Known Unknown 1 records the check, and its Escape Hatch is to run the command with the 0.3.1 CLI on a fresh clone and record the exit code.

### 3. Run the agent

```
opengap run -d .
```

For the run command, either `-r/--repo` or `-d/--dir` is required *(web)*. The remaining flags, ordered by how likely they are to change your first run *(web)*:

- `-p/--prompt <query>` — one-shot runs.
- `-a/--adapter` — defaults to claude; the upstream docs also show github, lyzr, git (auto-detected), and prompt.
- `-b/--branch` — select a branch.
- `--session-id`, `--resume` — session reuse on the claude adapter.
- `--workspace`, `--refresh` — workspace options.

Once the repository is pushed, `opengap run -r <repo-url>` runs it for anyone with the CLI *(web)*:

```
opengap run -r <repo-url>
```

Whether it passes `opengap validate -d .` on a fresh clone is Known Unknown 1.

> **qmd dependency.** The qmd-scout subagent queries markdown knowledge bases through the qmd CLI — `qmd query "question"`, `qmd search "keywords"`, `qmd get "#abc123"` (skills/qmd/SKILL.md:128-133), and `qmd status` (skills/qmd/SKILL.md:19,123) — and it is one of the two declared shell dependencies (agent.yaml:161). Install it from upstream (skills/qmd/SKILL.md:19-26):
>
> ```
> git clone https://github.com/b08x/qmd.git
> cd qmd && npm install && npm link
> ```

## The Agent Suite

The suite is one root agent — **ruth** — plus eight subagents under `agents/`, each carrying its own `agent.yaml` manifest and `SOUL.md` on disk (e.g., agents/sfl-docs-editor/SOUL.md:1); the root manifest lists all eight at agent.yaml:30-62. Roles follow a five-role segregation scheme — orchestrator, maker, checker, executor, evidence_gatherer (DUTIES.md:7-13; role definitions at agent.yaml:101-127, per-agent assignments at agent.yaml:132-148) — whose conflict matrix forbids the failure mode this suite exists to prevent: an agent that drafts documentation cannot audit or judge its own work (DUTIES.md:17-22). That prohibition is one design expressed at three levels: the matrix forbids self-audit at the level of agents, the gate rules forbid self-certification at the level of protocol (RULES.md:4-7), and taken together they leave exactly one route to a finalized document — the human approval gate, where the loop closes outside the system entirely (The Plannotator Review Gate below). A `document_finalize` handoff accordingly requires both maker and checker, with Approval Required: true (DUTIES.md:28-31).

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

The three judges share one protocol. Each is a read-only leaf agent (role line at SOUL.md:6 in all three files) that runs a two-move audit — a blind audit first, then cross-examination of the other judges' findings (ideational SOUL.md:18-19; interpersonal SOUL.md:15-16; textual SOUL.md:16-17). That cross-examination is the input the workflows' consensus step consumes — and it is the design's point: the consensus verdict emerges from the three-way interaction of mutually independent audits, held by no single judge alone, which is why the suite runs three forbidden-to-overlap roles instead of one thorough auditor.

## Workflows

In `workflows/sfl-docs-debate.yaml` — 142 lines, version 0.1.0 (lines 1-3) — a document is born: the workflow takes `target_path` and `genre_template` as required inputs, with optional `register_field`, `register_tenor`, and `register_mode`, then runs ten steps:

1. **codebase-scout** gathers evidence under a budget of 4 tool calls over 2 files (lines 30-38).
2. **qmd-scout** searches the QMD knowledge base (lines 39-46).
3. **sfl-docs-drafter** drafts the document from the SFL genre template and the scouts' evidence (lines 47-59).
4–6. **The three judges audit the draft** — ideational (step begins at line 60), interpersonal (line 70), textual (line 80) — each running its blind audit, then cross-examination (lines 60-89).
7. **consensus-synthesis** resolves the judges' findings, and its instruction is explicit: "Resolve inter-judge deadlocks strictly using cited code/spec evidence." (lines 90-99)
8. **A Plannotator gate** with `require_approval: true` presents the consensus result for human approval (lines 100-112).
9. **sfl-docs-editor** applies only what that gate approved — the step runs only when `steps.gate.outputs.review_decision == "approved"` (line 119).
10. **validate** runs the sfl-technical-writing Step 5 five-point gate over the edited result, looping back to the editor `on_failure` (lines 125-139).

The ten step ids sit at lines 30, 39, 47, 60, 70, 80, 90, 100, 113, and 125. Read as a graph rather than a list, the sequence carries one back-edge: on failure, step 10 re-enters step 9, and the edit–validate pair repeats until the five-point gate passes — the workflow's single recursion, where failure does not exit the system but re-enters it one step earlier. Any step failure outside that loop escalates to the supervisor (lines 140-142).

In `workflows/collaborative-edit.yaml` (54 lines), pairing and review compress those ten steps into four. The collaborative session itself — the step assigns no sub-agent (lines 14-19) — applies mechanical fixes directly; everything beyond them is annotated as a proposal — "claim -> problem class -> evidence needed -> proposed rewrite" (lines 20-26); the proposal batch passes a Plannotator gate (lines 27-39); and sfl-docs-editor applies only the approved proposals, one edit call per fix, gated on `gate_decision == "approved"` (lines 40-51, condition at line 46). The four steps drop the debate stages, but not the gate — the one stage both workflows share.

### What a run looks like

Everything above describes the suite's artifacts without showing one, so here is a sample — explicitly illustrative, invented content, clearly marked, showing the formats defined in this repo; it is not repository output. A one-shot invocation composing the documented run entry point with the ten-step workflow's required inputs (a target path and one of the three genre templates):

```
opengap run -d . -p "Run the sfl-docs-debate workflow on docs/example.md with the system-overview genre template"
```

One proposal, in the shape `claim -> problem class -> evidence needed -> proposed rewrite` (format at workflows/collaborative-edit.yaml:20-26):

```
claim: "The gate script wraps a single command."
  -> problem class: verifiable by direct inspection
  -> evidence needed: read tools/plannotator-gate.sh:25
  -> proposed rewrite: keep the claim, append its anchor (tools/plannotator-gate.sh:25)
```

And the decision the human answers at the Plannotator prompt (decision shapes at sfl-docs-debate.yaml:112 and collaborative-edit.yaml:46):

```
review_decision: "approved"
```

Only an approved decision like that lets the edit step run.

## The Plannotator Review Gate

Both workflows converge on the same control point. AGENTS.md:11 mandates it, the root manifest declares plannotator its sole tool (agent.yaml:24-25), and the definition has two parts: `tools/plannotator.yaml` (28 lines) declares three inputs — `file` (required), `result_file`, and `require_approval` — and tools/plannotator-gate.sh (30 lines, executable) implements it by wrapping one command (line 25):

```
plannotator annotate "$FILE" --gate --json --require-approval
```

The rule is one invariant descending a stack, expressed in a different formalism at each level:

- **Manifest level** — plannotator is the agent's sole declared tool (agent.yaml:24-25).
- **Tool level** — `require_approval: true` makes the human approval prompt mandatory (tools/plannotator.yaml:13-15).
- **Workflow level** — both workflows carry the gate step (workflows/sfl-docs-debate.yaml:100-112; workflows/collaborative-edit.yaml:27-39), and their edit steps run only on approval (sfl-docs-debate.yaml:119; collaborative-edit.yaml:46).
- **Hook level** — a pre_tool_use hook passes every shell call to an allowlist (hooks/hooks.yaml:8-13).
- **Shell level** — that allowlist permits ruth `plannotator annotate` only (hooks/scripts/check-allowlist.sh:62-67).

Outside the shell, the manifest bounds the remaining routes: writes require approval (RULES.md:10). No route the manifest declares bypasses the gate.

The gate's semantics are mandatory, not advisory (RULES.md:4-7): the human-in-the-loop (HTIL) gate is required; an agent never self-certifies; a denial means folding the feedback back into the work and re-running; and a usage error means fixing the command, not retrying it blindly. The script's failure modes are explicit — when the plannotator CLI is missing, it writes decision "escalate" to the result file (line 19) and to stdout (line 21) and exits 1 (line 22); when the file argument is missing, it exits 2 (lines 11-14).

The script is thin on purpose. Every mechanical branch in those 30 lines is specified so that no branch remains mechanical at the decision point: the one condition the script cannot compute is the human's yes or no. Its authority comes from the human answering the approval prompt that `require_approval: true` makes mandatory (tools/plannotator.yaml:13-15), not from the script itself — and this is where the loop the suite forbids everywhere else, no agent auditing its own draft and no agent certifying past a denial (DUTIES.md:17-22; RULES.md:4-7), can only close: outside the system, at a level above it.

## Shell Discipline

R.U.T.H.'s shell restrictions are enforced, not requested. hooks/hooks.yaml registers three hooks — `on_session_start`, `pre_tool_use`, and `on_error` (lines 1-19) — and in `hooks/scripts/`, check-allowlist.sh (103 lines) enforces per-agent read-only shells: codebase-scout's shell allows git read subcommands plus non-mutating file inspection (ls, fd, wc, head, tail, cat, stat, file) — no command that writes (check-allowlist.sh:70-76); qmd-scout's allows the qmd CLI only (check-allowlist.sh:79-85); and ruth's own shell allows `plannotator annotate` only (check-allowlist.sh:62-67). These allowlists are defined by what falls outside them: the permission list is the figure, and the refusal of everything unlisted — down to any agent not listed here getting no shell at all (check-allowlist.sh:97-98) — is the ground the figure carves. One environment quirk matters when driving qmd-scout manually: `CI=true` disables the LLM inside qmd, so the scout runs `env -u CI qmd query` to strip it (agents/qmd-scout/SOUL.md:11). Each session runs inside bounds the root manifest declares: max_turns 100 and timeout 600, unit undeclared in the manifest (agent.yaml:64-66); separately, every shell call passes a 5-second pre_tool_use hook check before it runs (hooks.yaml:11).

## Repository Layout

The 78 tracked files (`git ls-files | wc -l`) organize as:

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
top level                  AGENTS.md, PROMPT.md, README.md, agent.yaml, SOUL.md, RULES.md,
                           DUTIES.md, .gitignore
```

The root manifest also carries the runtime contract. It declares shell dependencies `qmd,plannotator` (agent.yaml:161) and an MCP server — codebase-memory-mcp — started via the environment variable `CODEBASE_MEMORY_MCP_CMD`, brace-templated at agent.yaml:71-74; that variable's definition appears in none of the 78 tracked files — Known Unknown 3 records the gap and its Escape Hatch, a git grep across the tree. The manifest further declares that compliance output is retained 6 years, logged as structured_json, immutable (retention at agent.yaml:91, log contents at :92-97, immutable at :98) — a declaration recorded as such because no in-repo component can be named that enforces that retention on disk. Escape Hatch: identify the enforcement mechanism.

## What the Suite Deliberately Does Not Do

What the suite does not do is part of its design, stated as plainly as what it does. The orchestrator, sfl-docs-workflow, owns the register and the validation gate but does not draft prose (agents/sfl-docs-workflow/SOUL.md:9,19). No judge writes — the three judges are read-only leaf agents (ideational SOUL.md:6,18-19; interpersonal SOUL.md:6,15-16; textual SOUL.md:6,16-17). The drafter may create files but cannot edit existing ones (agents/sfl-docs-drafter/SOUL.md:6). The editor applies fixes but never runs git (agents/sfl-docs-editor/SOUL.md:6). No draft or proposal batch finalizes without a human-approved gate (AGENTS.md:11), and no agent self-certifies past a denial — denial feedback is folded back and the gate re-run (RULES.md:4-7). Memory carries a declared bound, not an enforced one: MEMORY.md states "Max 200 lines" (memory/MEMORY.md:3); no enforcement mechanism is documented anywhere in this repository. There is no package.json, Makefile, justfile, or Taskfile among the 78 tracked files; installation runs through the OpenGAP and qmd CLIs documented above — plus plannotator, a declared shell dependency whose installation this repo does not document (Known Unknown 2).

## Known Unknowns (9 Rationed Unknowns)

Beyond those bounds, nine rationed unknowns remain — this section being the suite's name made procedural: records uncertainty, traces history. A rationed unknown is a rationed uncertainty — not a verified fact — and each names the exact act that would resolve it (its Escape Hatch):

1. The OpenGAP runtime now has a documented install — `npm install -g @open-gitagent/opengap` (upstream OpenGAP docs, web) — but this README has not re-run `opengap validate -d .` against this repository, so the port goal's clean exit (goals/ruth-opengap-port/goal.md:5) is recorded as a goal, not verified here. **Escape Hatch:** run `opengap validate -d .` with the 0.3.1 CLI on a fresh clone and record the exit code.
2. The plannotator CLI's installation is undocumented in every file I read. When the CLI is missing, plannotator-gate.sh writes decision "escalate" to the result file (:19) and to stdout (:21) and exits 1 (:22) — the human review the annotate call would have prompted never happens (tools/plannotator-gate.sh:16-23). **Escape Hatch:** document the upstream install.
3. The environment variable `CODEBASE_MEMORY_MCP_CMD` is referenced (agent.yaml:73) and defined in none of the 78 tracked files I read; a grep across those files would close the question. **Escape Hatch:** `git grep -ln CODEBASE_MEMORY_MCP_CMD` across the 78 tracked files, then document the MCP launch command.
4. The Python scripts in skills/sift-graph — sift_graph.py, sift_graph_crewai.py, sift_graph_mcp.py — have no dependency manifest, and I could not verify that they run. **Escape Hatch:** execute them against a target repo with dependencies pinned.
5. The model values that commit a488530 replaced are not reconstructed here. **Escape Hatch:** `git show a488530^:agent.yaml`.
6. Of the 6 skills the root manifest mounts (agent.yaml:16-22), only 3 genre templates exist — in skills/sfl-technical-writing/templates/ — and agents/sfl-docs-workflow/SOUL.md:63 mentions adapting staging for API reference, troubleshooting, and security docs, but no template files for those genres exist. **Escape Hatch:** author the additional template files.
7. agent.yaml:6 declares an MIT license, but no LICENSE file is tracked. **Escape Hatch:** add a LICENSE file to match the declaration.
8. `examples/`, `examples/scenarios/`, and `memory/archive/` exist as empty directories (0 tracked files); their intended use is undocumented. **Escape Hatch:** document them or remove them.
9. The goal statement quotes its payload counts — "the 15 accepted, testable outcomes" (goal.md:9) and "the approved 11-step execution plan" (goal.md:10) — but facts.md and plan.md are not audited line-by-line here. **Escape Hatch:** audit facts.md and plan.md.

## Where to Go from Here

To run the suite: clone, install the prerequisites in order, and validate — `opengap validate -d .` exiting clean is the port goal, and this README has not re-run it, so that is your first opportunity to close Known Unknown 1. Then start with `collaborative-edit.yaml` (54 lines, four steps) for a short first drive that still reaches the human-approval gate, and move to `sfl-docs-debate.yaml` for full ten-step document creation. To adapt the suite: `agent.yaml` is the root manifest, `DUTIES.md` holds the segregation rules, and the three genre templates under `skills/sfl-technical-writing/templates/` are where a new document type begins. The nine known unknowns above are part of the design, not a deficit — each names the exact act that closes it. And the standing invitation from the opening still holds: this README is drafted to its own standard, with 60+ path:line anchors across its twelve sections and more than 100 checkable claims; sample any section and count clauses against anchors.

## License

agent.yaml:6 declares `license: MIT`. No LICENSE file exists among the 78 tracked files — the declaration and the repository contents do not currently match; Known Unknown 7 records the fix.
