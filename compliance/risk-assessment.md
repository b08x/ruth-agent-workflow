# Risk Assessment

## Agent: ruth
## Risk Tier: standard
## Assessment Date: 2026-11-08
## Assessor: b08x

## Risk Tier Justification
R.U.T.H. is classified under the **standard** risk tier. The agent orchestrates technical documentation authoring and editing (READMEs, API references, changelogs, postmortems, and architecture notes). It does not hold production deployment permissions, execute financial transactions, or mutate customer data. Its blast radius is bounded to repository documentation.

## Applicable Regulatory Frameworks
None directly mandated for general internal documentation; operates under standard organizational change control, provenance tracking, and segregation of duties.

## Risk Categories
1. **Unverified Claims / Hallucination:** Documenting incorrect operational characteristics or unverified behaviors.
   - *Mitigation:* Target Intensity 9/10 grammar requires that at least 9 of every 10 declaratives carry verifiable proof (`path:line`, `#docid`, exact measure, or Escape Hatch).
2. **Unauthorized File Mutation:** Overwriting repository documents without consent.
   - *Mitigation:* `write_file` and `edit` tools require explicit human approval (`permission: "ask"`). Pre-tool hooks block unauthorized shell invocations.
3. **Unreviewed Document Release:** Finalizing documentation without human validation.
   - *Mitigation:* Mandatory human-in-the-loop Plannotator review gate (`plannotator annotate --gate --require-approval`) enforced by workflow and policy before any draft or proposal batch is finalized or applied.

## Mitigation Controls
- **Segregation of Duties:** Drafter (maker), Judges (checkers), Editor (executor), and Ruth (orchestrator) roles strictly partitioned.
- **Human-in-the-Loop Supervision:** Conditional supervision with automated escalation when confidence is below 0.7 or when errors are detected.
- **Audit Logging:** Structured JSON audit logging of all prompts, responses, tool calls, and decision pathways.

## Approval
- [x] Risk team approval
- [x] Systems engineering approval
- [x] Supervisor approval
