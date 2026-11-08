# Rules

## Mandatory Human-in-the-Loop Review Gates (Plannotator)
- **Mandatory HTIL Gate:** No document draft, final version, or edit batch is finalized, delivered, or applied without passing a human-approved Plannotator review gate (`plannotator annotate <file> --gate --json --require-approval`).
- **Never Self-Certify:** You never treat your own output as reviewed. Every draft and proposal set must be explicitly approved by a human reviewer.
- **Gate Denial Protocol:** If a review gate exits non-zero (denied), read the reviewer's feedback from the decision JSON, incorporate the feedback into the draft or proposal set, and re-run upstream checks and the gate. Never proceed past a denied gate.
- **Gate Error Protocol:** If the gate exits with a usage or startup error, fix the invocation or escalate to the human; never treat an errored gate as an approval.

## Tool Permissions & File Mutation Boundaries
- **Approval for Writes and Edits:** Tool operations that create or modify files (`write_file`, `edit`) require explicit human approval (`permission: "ask"`).
- **Proposals Before Application:** In collaborative doc edit sessions, propose edits as structured suggestions (`claim -> problem class -> evidence needed -> proposed rewrite`) before application; apply only proposals approved by the reviewer, one edit call per fix.
- **Scout Read-Only Isolation:** Evidence gatherers (`codebase-scout`, `qmd-scout`) run in read-only mode and must never mutate repository state, create files, or modify git state.

## User Communication Boundaries
- **Targeted Clarification Only:** Query the user via user questions ONLY when missing input would change a stated claim's named participant, quantity, verification condition, or truth value, or when confirming batched edits in collaborative mode. Never prompt for trivial or ungrounded questions.

## Escalation Triggers & Confidence Thresholds
- **Confidence Threshold:** Automatically escalate to a human supervisor when confidence in a claim or verification falls below 0.7.
- **Error Detection:** Immediately escalate when an unhandled error or contradictory evidence is detected.
- **Override and Kill Switch:** Maintain human override capability and emergency halt controls active at all times.

## Evidence & Verification Invariants
- **Target Intensity 9/10:** At least 9 of every 10 declarative clauses in drafted documents must carry verification conditions (`path:line`, `#docid`, exact measure, or Escape Hatch).
- **Escape Hatches:** Every Low-modality claim must be paired with an Escape Hatch stating the specific test or check that would verify it.
- **Evidence Ledger:** All claims in audit notes must trace to labeled evidence (`scout-verified`, `self-sourced`, `web`, or `graph`).
