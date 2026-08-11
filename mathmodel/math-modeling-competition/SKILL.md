---
name: math-modeling-competition
description: Evidence-first workflow for CUMCM, MCM/ICM, graduate and other mathematical modeling contests. Use when Codex must understand or select a contest problem, inspect data, compare and reject candidate models, formulate and execute a model, verify numerical and statistical results, run sensitivity or robustness analysis, design claim-bearing figures, write a Chinese or English contest paper, produce a memo or letter, audit contest compliance, or resume a multi-day modeling project from saved state.
---

# Mathematical Modeling Competition

## Operating contract

Treat modeling as a falsifiable workflow, not a keyword-to-algorithm lookup. Keep the team responsible for final choices, citations, formulas, code, data, compliance, and submission. Never claim an award probability.

Work in a project workspace, never inside this skill folder. On first use, run `python <skill>/scripts/init_workspace.py <workspace> --competition <name>`. If `state/decision_log.json` exists, read it before proposing new work and resume from the latest incomplete gate.

## Route by stage

1. **Rules and intake** — Verify the current official rules, AI disclosure requirements, language, anonymity, page limit, files, and deadline. Read `references/contest-compliance.md` and `references/problem-taxonomy.md`.
2. **Problem and data audit** — Restate each subquestion as decision variables, targets, constraints, outputs, evidence, and dependencies. Record units, missingness, provenance, temporal order, and leakage risks.
3. **Candidate tournament** — Read `references/model-selection.md`. Propose a transparent baseline and at least two plausible candidates. Apply assumption, data, complexity, identifiability, engineering, and validation gates. Record rejection evidence and a fallback.
4. **Formulation and execution** — Require a user-authorized, hash-current tournament before model execution. Load only the relevant domain reference. Write symbols, units, equations, constraints, parameter sources, solver status checks, and reproducible code. Start from the matching utility in `templates/code/` when applicable. Use exact optimization before heuristics when tractable.
5. **Validation** — Read `references/validation.md`, `references/sensitivity.md`, and `references/failure-patterns.md`. Compare with a baseline; inspect residuals or feasibility; test perturbations, scenarios, and failure boundaries.
6. **Evidence and figures** — Register dependencies with `templates/claim-evidence.json` and `templates/artifact-registry.json`. Run `scripts/check_evidence.py`; when upstream data, parameters, or models change, run `scripts/invalidate_artifacts.py` before regenerating descendants. Read `references/visualization.md`. Complete a Figure Contract before every final figure. A figure without a claim, units, expected pattern, and interpretation is not a deliverable.
7. **Paper** — Read `references/paper-writing.md`, `references/judges-commentary.md`, and `references/award-paper-patterns.md`. Write the summary last and report concrete results, uncertainty, weaknesses, and limits.
8. **Audit and handoff** — Run `python <skill>/scripts/audit_skill.py <skill>` for the skill itself and use the project checklist in `references/contest-compliance.md` for a submission. Update `state/decision_log.json` after each gate.

## Domain routing

- Forecasting: `references/forecasting.md`
- Evaluation/MCDM: `references/evaluation.md`
- Optimization and control: `references/optimization.md`
- Statistics and inference: `references/statistics.md`
- Graphs and networks: `references/graph-network.md`
- Spatial modeling: `references/spatial-modeling.md`
- Mechanism models: `references/mechanism-modeling.md`
- Simulation: `references/simulation.md`
- Machine learning: `references/machine-learning.md`

Load multiple domain references only when subquestions genuinely require different mechanisms. Do not stack models merely to decorate the paper.

## Mandatory gates

Do not advance when any applicable gate fails:

- **Traceability:** every non-given parameter, dataset, fact, and external figure has a source.
- **Dimensional validity:** equations, units, signs, bounds, and conservation relations are coherent.
- **Model justification:** the primary model beats or materially extends a simpler baseline.
- **Execution:** reported numbers come from executed code or a reproducible calculation, not prose generation.
- **Solver integrity:** feasibility, termination status, optimality gap, constraint violations, and stochastic seeds are checked.
- **Validation integrity:** temporal data use temporal splits; preprocessing is fitted inside folds; test data never informs selection.
- **Claim discipline:** conclusions do not exceed the model, data, scenarios, or uncertainty analysis.
- **Compliance:** current official rules override cached guidance and third-party templates.

## State and artifacts

Use `templates/candidate-model-tournament.json`, `templates/figure-contract.md`, and the paper outline matching the contest. Obtain the content hash with `python <skill>/scripts/check_plan.py <plan.json> --print-hash` and present or persist the exact hashes before requesting authorization. Accept either (a) a manual human signature or (b) an explicit repository-owner message such as `继续`, `approve`, `批准`, or `同意执行`. For an explicit user message, Codex may run `scripts/record_user_approval.py` to record the authorization text, user identity, timestamp, and current content hash; identify the user as approver and never identify Codex as approver. Treat that message as run-scoped authorization: if evidence forces an in-scope plan repair, record the reason, refresh the content hash with the same authorization, revalidate, and continue without asking the user again. A material change of problem, objective, data source, or external-action scope still requires fresh authorization. Store machine-readable results separately from prose so a model change can propagate to figures, tables, summary, and conclusions.

Read `references/state-and-collaboration.md` when several people or agents share work. Read `references/citation-license.md` before incorporating outside code, templates, or papers.

## Prohibitions

Never invent citations, results, solver success, statistical significance, data provenance, or award status. Never use random train/test splits for ordered time series. Never call a heuristic solution optimal without a bound or proof. Never copy papers or unlicensed repository content into a public deliverable. Never hide AI use when disclosure is required.
