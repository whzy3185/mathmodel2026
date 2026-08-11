# Human approval request — model execution gate

Selected problem: 2026 MCM Problem C — Data With The Stars.

The following SHA-256 values bind every field of each proposed tournament except the
`team_approval` object. A human team member must review the JSON and explicitly approve it.

| Question | Plan | Approval hash |
|---|---|---|
| Q1 | `Q1.json` | `535fdf4ec81955b9e1800ebe744308b70ce8ff1ff4bd6c8e5fd4b81bf4623cf0` |
| Q2 | `Q2.json` | `6b308ca6f5e80c5229352004436b6fc015d375552a0d1018e31735276a9d6560` |
| Q3 | `Q3.json` | `85b3022069b2657c64db4cca6d759bcba630b96b28588ea07a7bd25adcf748fd` |
| Q4 | `Q4.json` | `76383e02368b222b142765705d03b395465244cc170a37d429643080d4e62c3d` |

Approval must populate each file with a human identity, an ISO-8601 timestamp including a
timezone, and the matching hash. Any later plan edit changes the computed hash and invalidates
the approval. Codex/ChatGPT/OpenAI/AI/LLM are rejected as approver identities.

No baseline or candidate model for this run may execute until all four validators print `PASS`.
