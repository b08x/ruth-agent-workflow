# R.U.T.H. (Records Uncertainty, Traces History)

R.U.T.H. is an agent suite that writes technical documentation the way a careful team would: gather evidence first, draft second, audit third — and apply nothing until a human approves. The rule that makes the whole design worth reading about is stated once in the suite's own instructions and then engineered into every layer: "Every workflow mandates that no draft or proposal batch is finalized without passing a human-approved Plannotator review gate." Everything you'll meet below — the role segregation, the three judges, the shell allowlists — exists to make that one rule impossible to route around.

The repository packages the agent as a clone-and-run project. The root manifest (`agent.yaml`) names the agent **ruth** — author b08x, license MIT (a declaration with a gap; see License). Under ruth sit eight subagents, driven through two workflow definitions in `workflows/`:

- **`sfl-docs-debate.yaml`** — whole-document creation and major rewrites; ten steps.
- **`collaborative-edit.yaml`** — pairing and review sessions; four steps.

Between them they cover the documentation genres the suite is built for: READMEs, API references, changelogs, postmortems, architecture notes.

Two pieces of suite jargon get plain-language glosses now, because they arrive everywhere. **SFL** (Systemic Functional Linguistics) is a school of linguistics that describes language by what it *does* — what it claims, how confident it sounds, how it flows. R.U.T.H. borrows three of its lenses and turns them into the three auditors of every draft. **Plannotator** is an external command-line tool — the suite's window to a human. When a workflow "runs the Plannotator gate," it means the machine stops, shows a person the work, and waits for an answer before anything is written.

> **Reading conventions.** Every claim in this README is verifiable against the files in this repository — commands and paths are quoted verbatim. Check anything against the tree; the invitation stands. Facts about the OpenGAP CLI itself come from the upstream v0.3.1 documentation, since that tool lives outside this tree.

## Prerequisites

- **Node.js and npm.** Required by both CLIs below.
- **OpenGAP CLI.** The runner; the upstream README documents version 0.3.1.
- **qmd.** A markdown knowledge-base search CLI. The qmd-scout subagent cannot query knowledge bases without it. Install steps appear at the end of Installation.
- **plannotator.** The review-gate CLI. Its installation is undocumented anywhere in this repository — and the gap has teeth: when the CLI is missing, the gate script writes decision "escalate" and exits 1, and the human review silently never happens. Install it before you drive anything through a gate. Known Unknown 2 tracks the gap; its Escape Hatch — the exact step that would resolve an unknown — is to document the upstream install.

## Installation

One CLI to install, one command to validate the repo against its port goal, one to run.

### 1. Install OpenGAP

```
npm install -g @open-gitagent/opengap
```

Verify with `opengap --version`; the upstream README documents 0.3.1. The install also adds `gitagent` as an alias, so every opengap command runs unchanged as gitagent.

### 2. Validate this repository

```
opengap validate -d .
```

The validator checks `agent.yaml` against a JSON schema, requiring every referenced skill, tool, and agent to actually exist; requires `SOUL.md` to be non-empty; checks skills for valid frontmatter, a name matching their directory, and bounds on description length and instruction size; checks hooks for valid YAML, with referenced scripts required to exist; and checks tools against a valid schema. The `-c/--compliance` flag adds regulatory checks on top: risk tier, human-in-the-loop coverage for high and critical tiers, and audit logging.

This repository sets that command as its own port goal: `opengap validate -d .` exiting clean — command exits zero with no errors — with every fact in the goal's facts file that has an automated check passing it, and two facts confirmed manually. In the suite's own spirit, the honest line comes next: this README has not re-run the validation. A clean exit is the goal, not a verified fact, and your fresh clone is the first place to confirm it (Known Unknown 1).

### 3. Run the agent

```
opengap run -d .
```

Either `-r/--repo` or `-d/--dir` is required. The flags most likely to matter on a first run:

- `-p/--prompt <query>` — one-shot runs.
- `-a/--adapter` — defaults to claude; the upstream docs also show github, lyzr, git (auto-detected), and prompt.
- `-b/--branch` — select a branch.
- `--session-id`, `--resume` — session reuse on the claude adapter.
- `--workspace`, `--refresh` — workspace options.

Once the repository is pushed, `opengap run -r <repo-url>` lets anyone with the CLI drive it remotely:

```
opengap run -r <repo-url>
```

> **qmd, the other CLI.** qmd-scout searches markdown knowledge bases through the qmd CLI — `qmd query "question"`, `qmd search "keywords"`, `qmd get "#abc123"`, `qmd status`. The root manifest names qmd and plannotator as its two shell dependencies. Install qmd from upstream:
>
> ```
> git clone https://github.com/b08x/qmd.git
> cd qmd && npm install && npm link
> ```

## The agent suite: nine agents, five roles, one separation

The suite is one root agent plus eight subagents, each carrying its own `agent.yaml` manifest and `SOUL.md` on disk. Every agent holds exactly one of five roles — orchestrator, maker, checker, executor, evidence_gatherer — and the assignments follow a segregation scheme whose point is the conflict it forbids: **an agent that drafts documentation cannot audit or judge its own work.** The duty matrix forbids self-audit at the level of agents; the protocol rules forbid self-certification at the level of gate practice; together they leave exactly one route to a finalized document — the human approval gate, where the loop closes outside the system entirely. A `document_finalize` handoff accordingly requires both a maker and a checker, with Approval Required: true.

| Agent | Role | What it can do |
|---|---|---|
| **ruth** (root) | entry point | Declares plannotator its sole tool and routes every draft to the human-approval gate; its shell permits `plannotator annotate` only |
| **codebase-scout** | evidence_gatherer | Read-only evidence gathering: git read subcommands plus non-mutating file inspection (`ls`, `fd`, `wc`, `head`, `tail`, `cat`, `stat`, `file`) — nothing that writes |
| **qmd-scout** | evidence_gatherer | Read-only QMD knowledge-base search through the qmd CLI; runs `env -u CI qmd query` (the reason appears under Shell discipline) |
| **sfl-docs-drafter** | maker | Drafts from SFL genre templates; may create files but cannot edit existing ones |
| **sfl-docs-editor** | executor | Applies consensus fixes as minimal diffs; never runs git |
| **sfl-docs-ideational-judge** | checker | Audits process-type coverage: material, mental, relational |
| **sfl-docs-interpersonal-judge** | checker | Audits modality calibration against evidence; returns a Modality Histogram |
| **sfl-docs-textual-judge** | checker | Audits theme–rheme progression and genre staging; returns a Staging & Cohesion Map |
| **sfl-docs-workflow** | orchestrator | Owns the register and the validation gate; does not draft prose; mounts the sfl-technical-writing and qmd skills |

The three judges are read-only leaf agents that share one protocol: a blind audit first, then a cross-examination of the other judges' findings. That cross-examination is what the workflows' consensus step consumes, and it is the design's quiet thesis — the verdict emerges from the three-way interaction of mutually independent audits, held by no single judge alone. That is why the suite runs three forbidden-to-overlap roles instead of one thorough auditor: independence, not thoroughness, is what makes the audit worth trusting.

## The two workflows

### sfl-docs-debate: a document is born

`workflows/sfl-docs-debate.yaml` (version 0.1.0) takes two required inputs — `target_path`, the document to produce, and `genre_template`, the document type — plus three optional register inputs: `register_field`, `register_tenor`, `register_mode` (SFL's Field, Tenor, and Mode: what the document is about, who it is talking to and in what voice, and what form it takes). Then ten steps:

1. **codebase-scout** gathers evidence under an explicit budget: 4 tool calls over 2 files.
2. **qmd-scout** searches the QMD knowledge base.
3. **sfl-docs-drafter** drafts the document from the SFL genre template and the scouts' evidence.
4–6. **The three judges audit the draft** — ideational, interpersonal, textual — each running its blind audit and then its cross-examination of the other two.
7. **consensus-synthesis** resolves the judges' findings, with an instruction that deserves quoting: "Resolve inter-judge deadlocks strictly using cited code/spec evidence."
8. **A Plannotator gate**, with `require_approval: true`, presents the consensus result for human approval.
9. **sfl-docs-editor** applies only what that gate approved — the edit step runs only when the gate's `review_decision` is "approved".
10. **validate** runs the sfl-technical-writing five-point gate over the edited result.

Read as a graph rather than a list, the sequence carries one back-edge: if validation fails, step 10 re-enters step 9, and the edit–validate pair repeats until the five-point gate passes. Failure does not exit the system; it re-enters one step earlier. A failure anywhere outside that loop escalates to the supervisor.

It's worth pausing on what the debate is auditing *for*, because the standard is the most practical idea in the suite. When an agent writes documentation, nothing in the setup stops it from inventing plausible-sounding claims — sounding right is precisely the skill a language model has. So the suite requires every factual claim a drafted document makes to carry a check the reader can actually run: a citation, a command, a measurement, or an honest "we don't know" naming the exact step that would find out. A claim the evidence cannot verify must say so openly. Each judge audits that bar in its own dimension — the ideational judge checks whether the draft's assertions (material, mental, relational processes — doing, thinking, being) are grounded; the interpersonal judge checks whether the draft's confidence is calibrated to its evidence; the textual judge checks whether the flow and genre staging carry a reader through it.

### collaborative-edit: pairing and review, compressed

`workflows/collaborative-edit.yaml` is the four-step version, for the session where a person and the agent edit a document together. The collaborative session applies mechanical fixes directly; everything beyond them is annotated as a proposal, each one shaped `claim -> problem class -> evidence needed -> proposed rewrite`. The proposal batch passes the Plannotator gate, and the editor applies only the approved proposals — one edit call per fix, gated on the decision being "approved". The four steps drop the debate stages, but not the gate: that is the one stage both workflows share.

### What a run looks like

The formats read faster than they describe. Everything below is illustrative — invented content in the repo's real formats — not repository output. A one-shot invocation composing the documented run entry point with the debate workflow's required inputs (a target path and one of the three genre templates):

```
opengap run -d . -p "Run the sfl-docs-debate workflow on docs/example.md with the system-overview genre template"
```

One proposal, in the shape the collaborative workflow defines:

```
claim: "The gate script wraps a single command."
  -> problem class: verifiable by direct inspection
  -> evidence needed: read tools/plannotator-gate.sh
  -> proposed rewrite: keep the claim, and name the file the reader can check
```

And the decision a human answers at the Plannotator prompt (the debate workflow names it `review_decision`; collaborative-edit calls the same decision `gate_decision`):

```
review_decision: "approved"
```

Only an approved decision like that lets the edit step run.

## The review gate: the one decision the suite cannot make

Both workflows converge on the same control point, and it deserves the most explanation, because it is the heart of the design. The gate's definition has two parts: `tools/plannotator.yaml` declares three inputs — `file` (required), `result_file`, and `require_approval` — and the gate script implements it by wrapping exactly one command:

```
plannotator annotate "$FILE" --gate --json --require-approval
```

The rule is a single invariant descending a stack, stated in a different formalism at each level:

- **Manifest.** plannotator is ruth's sole declared tool.
- **Tool.** `require_approval: true` makes the human approval prompt mandatory.
- **Workflow.** Both workflows carry the gate step, and their edit steps run only on approval.
- **Hook.** A pre_tool_use hook passes every shell call through the allowlist check.
- **Shell.** That allowlist permits ruth `plannotator annotate` — nothing else.

Writes require approval at the manifest level too; no route the manifest declares bypasses the gate.

The gate's semantics are mandatory, not advisory. A human decision is required; an agent never self-certifies; and a denial is not an error condition — it means fold the feedback back into the work and run the gate again. A usage error means fix the command, not retry it blindly. The script's two failure modes are explicit: if the plannotator CLI is missing, it writes decision "escalate" and exits 1 — the human review the annotate call would have prompted silently never happens; if the file argument is missing, it exits 2.

The script is thin on purpose. Every mechanical branch in its thirty-odd lines is pinned down, so that nothing remains mechanical at the decision point — the one condition the script cannot compute is the human's yes or no. Its authority comes entirely from the person answering the prompt that `require_approval: true` makes mandatory. Here, and only here, can the loop the suite forbids everywhere else — no agent auditing its own draft, no agent certifying past a denial — close: outside the system, at a level above it. That level is you.

## Shell discipline

The shell restrictions are enforced, not requested. `hooks/hooks.yaml` registers three hooks — `on_session_start`, `pre_tool_use`, `on_error` — and `hooks/scripts/check-allowlist.sh` enforces a per-agent shell for every agent that gets one:

- **codebase-scout**: git read subcommands plus non-mutating file inspection (`ls`, `fd`, `wc`, `head`, `tail`, `cat`, `stat`, `file`) — no command that writes.
- **qmd-scout**: the qmd CLI, and nothing else.
- **ruth**: `plannotator annotate`, and nothing else.
- **sfl-docs-workflow**: one further carve-out — the commands the orchestrator works with (`qmd`, `git`, `ls`, `cat`, `head`, `tail`, plus the `env -u CI qmd` form), and nothing else.
- Every agent outside the script's cases: no shell at all.

What falls outside those lists is the point of the lists. One environment quirk matters if you drive qmd-scout by hand: `CI=true` disables the LLM inside qmd, so the scout runs `env -u CI qmd query` to strip it.

The root manifest bounds the rest of the runtime: sessions run under max_turns 100 and a timeout of 600 (the unit is not declared), and every shell call passes a 5-second pre_tool_use hook check before it runs.

## Repository layout

```
agents/                   one directory per subagent: agent.yaml + SOUL.md
workflows/                sfl-docs-debate.yaml; collaborative-edit.yaml
tools/                    plannotator.yaml; plannotator-gate.sh
hooks/                    hooks.yaml; scripts/check-allowlist.sh
scripts/                  tracked shell scripts; contents not documented in this README
skills/                   doc-style, qmd, ruth-voice, sfl-technical-writing,
                          sift-graph, update-docs
  skills/sfl-technical-writing/templates/    3 genre templates
goals/                    ruth-opengap-port/
memory/                   MEMORY.md, memory.yaml
compliance/, config/, knowledge/    tracked directories; contents not
                          documented in this README
examples/, examples/scenarios/, memory/archive/    empty; purpose undocumented
top level                 AGENTS.md, PROMPT.md, README.md, agent.yaml, SOUL.md,
                          RULES.md, DUTIES.md, .gitignore
```

The root manifest also carries the runtime contract. It declares two shell dependencies — qmd and plannotator — and one MCP server, codebase-memory-mcp, started through the environment variable `CODEBASE_MEMORY_MCP_CMD`. That variable's definition appears in none of the tracked files; Known Unknown 3 records the gap. The manifest further declares that compliance output is retained 6 years, logged as structured_json, and immutable — recorded here as a declaration, because no component in this repository can be named that enforces that retention on disk. The escape hatch for that one is to identify the enforcement mechanism — or to confirm there is none.

Of the six skills the manifest mounts, sfl-technical-writing carries the genre templates: three exist, under `skills/sfl-technical-writing/templates/`. The workflow instructions name API reference, troubleshooting, and security docs as genres to adapt staging for — but no template files for those genres exist yet (Known Unknown 6).

## What the suite deliberately does not do

Part of the design is what it refuses, stated as plainly as what it does:

- The orchestrator, sfl-docs-workflow, owns the register and the validation gate but does not draft prose.
- No judge writes; all three are read-only leaf agents.
- The drafter may create files but cannot edit existing ones.
- The editor applies fixes but never runs git.
- Memory carries a declared bound, not an enforced one: MEMORY.md states "Max 200 lines", and no enforcement mechanism is documented anywhere in this repository.
- No draft or proposal batch finalizes without a human-approved gate, and no agent self-certifies past a denial — feedback is folded back in and the gate re-run.
- There is no package.json, Makefile, justfile, or Taskfile. Installation runs through the OpenGAP and qmd CLIs documented above, plus plannotator.

## Known unknowns

Nine unknowns remain, and the section is the suite's name made procedural: R.U.T.H. records uncertainty and traces history. Each unknown below is a rationed uncertainty — not a verified fact — and each names its **Escape Hatch**: the exact act that would resolve it. They are listed as part of the design, not as an apology for it.

1. **Validation not re-run.** This README has not run `opengap validate -d .` against this repository, so the port goal's clean exit is a goal, not a verified fact. *Escape Hatch:* run the command with the 0.3.1 CLI on a fresh clone and record the exit code.
2. **plannotator install undocumented.** No file in this repository documents how to install the gate CLI, and when it is missing the gate escalates and exits 1 with the human review silently skipped. *Escape Hatch:* document the upstream install.
3. **CODEBASE_MEMORY_MCP_CMD undefined.** The variable is referenced in the root manifest and defined in none of the tracked files. *Escape Hatch:* grep the tree for it, then document the MCP launch command.
4. **sift-graph scripts unverified.** The Python scripts in skills/sift-graph — sift_graph.py, sift_graph_crewai.py, sift_graph_mcp.py — have no dependency manifest, and this README could not verify that they run. *Escape Hatch:* execute them against a target repo with dependencies pinned.
5. **Model values not reconstructed.** The model configuration that commit a488530 replaced is not reproduced here. *Escape Hatch:* `git show a488530^:agent.yaml`.
6. **Missing genre templates.** The workflow instructions mention adapting staging for API reference, troubleshooting, and security docs, but only 3 genre templates exist. *Escape Hatch:* author the missing template files.
7. **MIT declared, no LICENSE file.** The root manifest declares an MIT license and no LICENSE file is tracked; the declaration and the contents do not match. *Escape Hatch:* add a LICENSE file.
8. **Empty, undocumented directories.** `examples/`, `examples/scenarios/`, and `memory/archive/` are tracked but empty, and their intended use is undocumented. *Escape Hatch:* document them or remove them.
9. **Payload counts not audited.** The goal statement quotes its payload counts — "the 15 accepted, testable outcomes" and "the approved 11-step execution plan" — but facts.md and plan.md have not been audited line-by-line. *Escape Hatch:* audit facts.md and plan.md.

## Where to go from here

Clone it, install the prerequisites in order, and validate — a clean `opengap validate -d .` exit is the port goal, and this README has not re-run it, so your first run is also the suite's first chance to close Known Unknown 1. For a short first drive that still reaches the human gate, start with collaborative-edit (four steps). Move to sfl-docs-debate when you want full ten-step document creation. To adapt the suite: `agent.yaml` is the root manifest, `DUTIES.md` holds the segregation rules, and a new document type starts as a genre template under `skills/sfl-technical-writing/templates/`. The nine known unknowns above are part of the design, not a deficit — each names the exact act that closes it.

## License

The root manifest declares `license: MIT`. No LICENSE file is tracked in this repository; the declaration and the contents do not currently match. Known Unknown 7 records the fix: add the file.
