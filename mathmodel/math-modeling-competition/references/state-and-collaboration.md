# State and Collaboration

Use `state/decision_log.json` as the project memory. Chat is discussion; files are the source of truth.

Record each decision with ID, timestamp, owner, subquestion, alternatives, evidence, chosen option, rejected reasons, affected artifacts, rollback/fallback, and approval. Give every result and figure a versioned artifact ID. When a model or parameter changes, invalidate downstream artifacts before recomputation.

Recommended states: rules-and-intake → problem-audit → candidate-tournament → formulation → execution → validation → paper → compliance-audit → submission-ready. A stage advances only when its named artifacts exist and gates pass. Partial repair returns to the first affected stage, not the beginning.

For team handoff, report: last accepted decision; commands run; current outputs; failed checks; unresolved risks; exact next action. Never rely on an agent's recollection of a result that is absent from the workspace.

