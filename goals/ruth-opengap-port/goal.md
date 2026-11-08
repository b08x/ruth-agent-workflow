# Goal — Port R.U.T.H to OpenGAP

## Articulated goal

Port the R.U.T.H agent suite — ruth, its two scout sub-agents, the SFL debate leafs (drafter, three metafunction judges, editor, workflow), their system prompts, tool-permission/safety configuration, and six associated skills — from the Vibe-native `~/.vibe/{agents,prompts,skills}` format into OpenGAP, making this repository a valid, clone-and-run OpenGAP agent (`opengap validate -d .` clean) with the persona, delegation structure, and human-in-the-loop Plannotator review gates intact.

## Shared understanding

- `facts.md` — the 15 accepted, testable outcomes of the port.
- `plan.md` — the approved 11-step execution plan (validate after every step).
- `grilling-decisions.json` — provenance of the decisions this goal was scoped with.

## Done condition

`opengap validate -d .` exits zero with no errors on the ported repo, and every fact in `facts.md` with automated verification passes its check (facts 7 and 15 are confirmed manually).
