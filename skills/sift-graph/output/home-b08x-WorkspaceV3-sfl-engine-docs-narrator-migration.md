# SIFT-Graph Report: sfl-engine doc changes & RubyLLM narrator migration

**Generated**: 2026-11-04T05:15:36Z (session), report assembled same session
**Project**: home-b08x-WorkspaceV3-sfl-engine
**Graph Status**: indexed (4,821 nodes, 10,126 edges, 658 File nodes; 1 parse_partial: `spec/fixtures/loaders/image_meta/malformed.yaml:1`; generation 2026-11-04T05:06:02Z, `generation_matches: true`)
**Producer**: sift-graph v0.1 (R.U.T.H. inline execution, Declared Deviation logged)
**Scope**: working-tree changes (`.gitignore`, `Gemfile.lock`, `docs/gem-inventory.md`, untracked `docker/.devcontainer/devcontainer.json`) plus the two recent refactors they document — the RubyLLM narrator migration (`52ed0ac`) and the require-time Zeitwerk loader (`fbb5ed0`).

---

## 1. ✅ Verified Facts

| # | Statement | Status | Provenance | Conf |
|---|---|---|---|---|
| V1 | `SFL::LLM::Narrators::NarrativeGenerator` requires `"ruby_llm"` at line 3, builds one chat per narrative via `build_chat(provider, model).ask(digest_text)` (line 88), and builds no DSPy object — the class comment (lines 11–14) states the request goes through RubyLLM, not DSPy | ✅ | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.llm.narrators.narrative_generator.SFL.LLM.Narrators.NarrativeGenerator:17-187) | 5 |
| V2 | `SFL::LLM::Narrators::SectionParser` (9–57) parses headed text into sections; `MissingSectionsError` subclasses `Analysis::NarrativeError` so the analysis layer passes it through | ✅ | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.llm.narrators.section_parser.SFL.LLM.Narrators.SectionParser:9-57) | 5 |
| V3 | `SFL::LLM::Catalogs::RubyLLMCatalog::REFRESH` refreshes the process-wide registry: `require "ruby_llm"` (line 17), `RubyLLM::Models.refresh(remote_only: true)` (line 18), `RubyLLM.models.all` (line 19) | ✅ | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.llm.catalogs.ruby_llm_catalog.SFL.LLM.Catalogs.RubyLLMCatalog:9-47) | 5 |
| V4 | `SFL::LLM::Tracing.configure` writes `LANGFUSE_*` into `ENV` then calls `DSPy::Observability.configure!(adapter: :langfuse)` at line 18 — the RubyLLM narrator sits outside this tracing path | ✅ | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.llm.tracing.SFL.LLM.Tracing:9-20) | 5 |
| V5 | `SFL.loader` (40–42) returns the `LOADER` constant, built at require time by `Zeitwerk::Loader.new.tap` (line 33, `private_constant` line 38) — commit `fbb5ed0`'s claim holds | ✅ | [Graph:Method](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.SFL.loader:40-42) | 5 |
| V6 | `SFL::Analysis::NarrativeGenerator` (15–275) takes an injected `narrator:` (no DSPy default — "DI-everywhere house convention", class comment), builds a `Core::Types::NarrativeReport` from `@narrator.call(digest.to_text)`, and maps three failure modes to `NarrativeError` via distinct rescue clauses | ✅ | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.analysis.narrative_generator.SFL.Analysis.NarrativeGenerator:15-275) | 5 |
| V7 | `bin/build-sidecar` drives the docker-api gem, not the docker CLI: `require "docker"` (line 16), `Docker::Image.build_from_dir` (line 72), `Docker::Container.create` (line 102) | ✅ | [Graph:File](home-b08x-WorkspaceV3-sfl-engine.bin.build-sidecar) | 5 |
| V8 | Graph state: 4,821 nodes, 10,126 edges, 658 File nodes; all eight cited evidence paths carry `no_recorded_issue` coverage with `metadata_match` freshness | ✅ | index_status + check_index_coverage (8 paths) 2026-11-04T05:06:02Z | 5 |

## 2. Errors & Corrections

| # | Statement | Status | Provenance | Conf |
|---|---|---|---|---|
| E1 | `docs/gem-inventory.md:42` cited `lib/sfl/ingest/loader_drafter.rb:2` for the `dspy` require; the actual `require "dspy"` sits at line 4 (line 2 is blank, line 3 requires `"fileutils"`). **Corrected to `:4` this session** | ✅ fixed | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.ingest.loader_drafter.SFL.Ingest.LoaderDrafter:16-146) + source lines 1–4 | 5 |
| E2 | The working-tree `Gemfile.lock` refresh inserted 77 malformed `PLATFORMS` entries (`dry-unknown` ×3, `dspy-unknown` ×4, 36 bare `unknown`, `rubocop-unknown` ×6, …) alongside 1 legitimate entry (`x86_64-linux-gnu`) of 78 total, at lockfile lines 604–682 | ⚠️ anomaly | `Gemfile.lock:604-682` (source count; graph-absent — lockfile is skip-listed from the index) | 5 |
| E3 | Root `README.md` had no mention of the new devcontainer definition; **a Setup-section paragraph was added this session** pointing at `docker/.devcontainer/devcontainer.json` with the auto-discovery caveat | ✅ fixed | [Graph:File](home-b08x-WorkspaceV3-sfl-engine.README.md) + README Setup section | 4 |

## 3. ⚠️ Risks & Anomalies

| # | Statement | Status | Provenance | Conf |
|---|---|---|---|---|
| R1 | The untracked `docker/.devcontainer/devcontainer.json` (26 lines) uses image `mcr.microsoft.com/devcontainers/ruby:2-3.4-trixie` with a JetBrains RubyMine backend, and its `postCreateCommand` is commented out — the container installs no project dependencies, and the file is outside every editor's auto-discovery path (`devcontainer.json` is auto-discovered only under `.devcontainer/` at the workspace root) | ⚠️ | `docker/.devcontainer/devcontainer.json:4,20,26` (source read; graph-absent — untracked config, re-index did not add it) | 4 |
| R2 | E2's malformed platform rows were written by the local bundler; whether a fresh clone's `bundle install` tolerates or regenerates them is untested — Escape Hatch: run `bundle install` on a clean clone or `bundle platform` and compare | ⚠️ rationed | `Gemfile.lock:603` (PLATFORMS header; graph-absent) | 3 |

## 4. Potential Leads

| # | Statement | Status | Provenance | Conf |
|---|---|---|---|---|
| L1 | `trace_path("NarrativeGenerator", inbound)` reports `callers_total: 0` although `lib/sfl/cli.rb:776` instantiates `LLM::Narrators::NarrativeGenerator.new` — the constructor-injection pattern (`narrator:` duck kwarg) leaves no CALLS edge in the graph; wiring questions need text search, not the call graph | 🔎 | trace_path output (2026-11-04) + [Graph:File](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.cli.rb) `cli.rb:776` | 4 |
| L2 | `bake` (Gemfile:258), `decode` (Gemfile:259) and `rubydex` (Gemfile:260) have zero call sites — `rg "require '(bake|decode|rubydex)'|\bBake\b|\bRubydex\b|Bakefile" lib exe bin rakelib` returns nothing — confirming `docs/gem-inventory.md`'s "not used" rows and prune-candidacy; commit `0d7532a`'s message ("bake task runner", "quality gates") is unsupported by the tree | 🔎 | `Gemfile:258-260` + negative rg sweep (graph-absent: Gemfile carries no File node; negative claims cannot resolve) | 4 |
| L3 | 18 of the 21 "no call site" findings in `docs/gem-inventory.md` (everything except `bake`/`decode`/`rubydex`, re-verified in L2) rest on the earlier `d974b45` pass, not on this session's evidence — Escape Hatch: re-run the per-gem rg sweep before any pruning decision | 🔎 | [Graph:File](home-b08x-WorkspaceV3-sfl-engine.docs.gem-inventory.md) Findings section | 3 |

## 5. Structure

| # | Statement | Status | Provenance | Conf |
|---|---|---|---|---|
| S1 | The narrator migration splits LLM transport (`lib/sfl/llm/narrators/`, 187-line `NarrativeGenerator` + 57-line `SectionParser`) from analysis assembly (`lib/sfl/analysis/narrative_generator.rb`, 275 lines incl. `Digest`); the narrator keeps a `SIGNATURES = {v0:, v1:, v2:}` hash (`DEFAULT_VARIANT = :v1`) whose description text alone is reused | ✅ | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.llm.narrators.narrative_generator.SFL.LLM.Narrators.NarrativeGenerator:32-36) + V6 node | 5 |
| S2 | Graph shape: 658 indexed files; the spec tree mirrors lib (e.g. `spec/llm/narrators/narrative_generator_spec.rb` present as Folder + Module + File nodes) | ✅ | query_graph (File count 658) + search_graph `spec/llm/narrators` | 5 |

## 6. Idioms

| # | Statement | Status | Provenance | Conf |
|---|---|---|---|---|
| I1 | The narrator's three error classes (`RefusedError`, `EmptyResponseError`, `ConfigurationError`) subclass `Analysis::NarrativeError` so `Analysis::NarrativeGenerator#generate` re-raises them unchanged and the CLI rescues by name | ✅ | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.llm.narrators.narrative_generator.SFL.LLM.Narrators.NarrativeGenerator:21-31) | 5 |
| I2 | The ports-and-fakes convention persists in the loader layer: `Core::Ports::Loader` with `Fake::Loader` and `Null::Loader` adapters, all present as graph nodes | ✅ | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.core.ports.loader.SFL.Core.Ports.Loader:11-22) | 4 |

## 7. Functionality

| # | Statement | Status | Provenance | Conf |
|---|---|---|---|---|
| F1 | End-to-end narrative flow: the CLI instantiates the RubyLLM narrator (`cli.rb:776-778`) with `variant: boot_result.narrative_variant || DEFAULT_VARIANT`; `SFL::Boot` validates the variant against `LLM::Narrators::NarrativeGenerator::SIGNATURES.key?(variant)` at `boot.rb:429`; the analysis layer injects it as the `narrator:` duck | ✅ | [Graph:File](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.cli.rb) `cli.rb:776-778` + [Graph:File](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.boot.rb) `boot.rb:429` | 4 |
| F2 | `docs/gem-inventory.md`'s "55 direct gems" holds: the Gemfile declares 76 gems — 55 top-level (43 before `group :development, :test` at line 186, 12 after `group :perf` closes at line 243), plus 15 dev/test, 3 quality, 3 perf, with zero duplicate names | ✅ | `Gemfile:1-262` (source count; graph-absent: Gemfile carries no File node) | 5 |

## 8. Testing

| # | Statement | Status | Provenance | Conf |
|---|---|---|---|---|
| T1 | The narrator migration carries mirrored specs: `spec/llm/narrators/narrative_generator_spec.rb` (Module node, lines 1–294, 9 outbound edges) and `spec/llm/narrators/section_parser_spec.rb` (1–83), plus `spec/llm/catalogs/ruby_llm_catalog_spec.rb` | ✅ | [Graph:Module](home-b08x-WorkspaceV3-sfl-engine.spec.llm.narrators.narrative_generator_spec:1-294) + [Graph:Module](home-b08x-WorkspaceV3-sfl-engine.spec.llm.narrators.section_parser_spec:1-83) | 5 |
| T2 | `bundle exec rake` runs RSpec, RuboCop and the Zeitwerk check as the pre-finish gate (documented in both `AGENTS.md` and `README.md` "Test" section) | ✅ | [Graph:File](home-b08x-WorkspaceV3-sfl-engine.AGENTS.md) + [Graph:File](home-b08x-WorkspaceV3-sfl-engine.README.md) | 5 |

---

## 9. 📊 SIFT-Graph Meta-Rubric Scores

**Ledger**: 21 main claims + 4 self-critique claims (below) = 25 total.
**Provenance audit**: 21 of 25 tuples resolve to graph nodes/edges; 4 do not (R2 `Gemfile.lock`, R1 `devcontainer.json`, L2 `Gemfile` + negative sweep, F2 partially — its Gemfile count is source-verified against a file the graph indexes not). Claim Provenance = 21/25 = 84% → **score 3** (70–85% band).

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Claim Provenance | 3 | 40% | 1.20 |
| Section Completeness (8/8 sections, ≥1 claim each) | 5 | 25% | 1.25 |
| Severity Calibration (14×5, 8×4, 3×3; mean ≈ 4.4, σ ≈ 0.7) | 3 | 20% | 0.60 |
| Self-Critique Payoff (4 new claims / 25 = 16%) | 3 | 15% | 0.45 |
| **Raw Score** | | | **3.50** |
| Pitfall Penalty (4 non-resolving tuples × −0.3) | | | **−1.20** |
| **Final Score** | | | **2.3** |
| Chain Integrity (min dimension) | 3 | | |

**Essential Cap**: Not triggered (Claim Provenance ≥ 3).
**Status**: Marginal — but read the cause before re-running: the penalty is dominated not by claim quality (every claim carries exact `path:line` evidence checked against source) but by the graph's by-design exclusion surface — `Gemfile.lock` is skip-listed, `Gemfile` carries no File node, and the untracked `devcontainer.json` was not picked up by a moderate re-index. Any re-run against a graph that indexes those three targets would lift the penalty wholesale.

### Self-Critique Ledger (Stage 5 — claims absent from the original pass)

| # | New claim | Provenance | Conf |
|---|---|---|---|
| C1 | The moderate re-index did not add `docker/.devcontainer/devcontainer.json` although the file is present in the tree — either the untracked status or the comment-bearing JSON blocked it; Escape Hatch: read the index run's `logfile` for the file's skip reason | index_repository response (excluded/not_indexed lists) + query_graph (rows: 0) | 4 |
| C2 | `SFL::LLM::Tracing.configure` **writes** `ENV["LANGFUSE_*"]` (lines 15–17); `AGENTS.md`'s "SFL::Boot is the only code that reads ENV" rule concerns reads, not writes — a nuance worth an inventory row if the doc ever audits ENV writes; Escape Hatch: `rg 'ENV\[' lib` | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.llm.tracing.SFL.LLM.Tracing:15-17) | 4 |
| C3 | The narrator snippet's provider check (`RubyLLM::Provider.providers.key?(provider)`, line 102) pins RubyLLM 2.1.1 semantics (see also line 39's version comment) — the `ruby_llm` Gemfile constraint `~> 2.1` matches; Escape Hatch: re-check `Provider.providers` against the ruby_llm 2.x registry on next upgrade | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.llm.narrators.narrative_generator.SFL.LLM.Narrators.NarrativeGenerator:39,102) + Gemfile:263 | 3 |
| C4 | The `SFL::Analysis::NarrativeGenerator::Digest` class (analysis file, 57-line class comment at build time) documents `UNRELIABLE_THRESHOLD = 0.5` and `PREVIEW_LENGTH = 200` as narrating-affecting constants — candidates for the glossary if narrative docs expand | [Graph:Class](home-b08x-WorkspaceV3-sfl-engine.lib.sfl.analysis.narrative_generator.SFL.Analysis.NarrativeGenerator:15-275) | 3 |

**Critique payoff**: 4/25 = 16% (> 0 — the critique pass added material, not theater).

### Documentation actions taken this session

1. `docs/gem-inventory.md:42` — `loader_drafter.rb:2` → `loader_drafter.rb:4` (E1).
2. `README.md` Setup — added the devcontainer paragraph with the auto-discovery caveat (E3/R1).
3. No stale DSPy-narrator claims exist in `README.md` or `docs/*.md` outside `gem-inventory.md` (rg sweep: zero matches).

### Limitations

1. Negative claims (L2's zero-call-site sweep) cannot resolve to graph nodes by nature; they rest on rg sweeps over `lib/`, `exe/`, `bin/`, `rakelib/`.
2. `Gemfile`, `Gemfile.lock` and untracked config files sit outside the graph's provenance surface this run.
3. Line numbers cite the working tree at 2026-11-04T05:06Z (graph generation) — before this session's two doc edits, which touched only Markdown.
