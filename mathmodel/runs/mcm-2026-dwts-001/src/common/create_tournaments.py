#!/usr/bin/env python3
"""Generate the four pre-execution candidate tournaments for human review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PASS_GATES = {
    "assumption_gate": "pass",
    "data_gate": "pass",
    "complexity_gate": "pass",
    "identifiability_gate": "pass",
    "engineering_gate": "pass",
    "validation_gate": "pass",
}


def candidate(
    name: str,
    formulation: str,
    assumptions: list[str],
    parameter_sources: list[str],
    validation_plan: list[str],
    refutation_evidence: list[str],
    failure_modes: list[str],
    decision: str,
    reason: str,
    *,
    failed_gates: list[str] | None = None,
    rejection_evidence: list[str] | None = None,
) -> dict:
    value = {
        "name": name,
        "formulation": formulation,
        "assumptions": assumptions,
        "parameter_sources": parameter_sources,
        **PASS_GATES,
        "validation_plan": validation_plan,
        "refutation_evidence": refutation_evidence,
        "expected_failure_modes": failure_modes,
        "rejection_evidence": rejection_evidence or [],
        "decision": decision,
        "decision_reason": reason,
    }
    for gate in failed_gates or []:
        value[gate] = "fail"
    return value


def approval() -> dict:
    return {"approved": False, "approver": "", "approved_at": "", "plan_hash": ""}


def plans() -> dict[str, dict]:
    q1 = {
        "problem_id": "2026-MCM-C",
        "subquestion": "Q1",
        "target_claim": "Latent weekly fan-share distributions reproduce reported eliminations with quantified, nonuniform uncertainty.",
        "data_audit": {
            "unit_table_complete": True,
            "temporal_order_preserved": True,
            "leakage_risks": ["results and placement only define validation constraints", "future weeks excluded"],
            "missingness_notes": "Judge-4 and late-season missingness are structural; zero scores after elimination are inactive."
        },
        "baseline": {
            "name": "uniform minimum-adjustment",
            "reason": "transparent least-information reference that can expose infeasible weeks",
            "implementation": "src/baseline/q1_uniform_adjustment.py",
            "validation": "weekly elimination compatibility and simplex violation"
        },
        "candidates": [
            candidate(
                "maximum-entropy constrained votes",
                "For each week maximize -sum_i v_i log(v_i) subject to v on the simplex and the reported eliminated contestant having a non-greater combined score than every survivor.",
                ["reported elimination label is correct", "one weekly vote share vector applies to all rule comparisons", "ties use a fixed epsilon"],
                ["judge scores and elimination labels from DATA-PROCESSED-C", "epsilon from numerical tolerance study"],
                ["compatibility by week and season", "constraint residuals", "bootstrap/feasible perturbation interval width", "hold out seasons 29-34 for stress reporting"],
                ["less than 90% of evaluable weeks feasible", "median interval width exceeds 0.50 share", "constraint residual exceeds 1e-7"],
                ["ambiguous no-/multi-elimination week", "rank-rule ties", "non-identification produces wide intervals"],
                "primary",
                "Uses the least additional information while satisfying observed outcomes and exposes uncertainty rather than inventing labels."
            ),
            candidate(
                "quadratic minimum-deviation votes",
                "Minimize sum_i (v_i-1/n)^2 under the same weekly simplex and elimination constraints.",
                ["uniform support is a defensible neutral center", "reported elimination label is correct"],
                ["DATA-PROCESSED-C", "numerical tolerance study"],
                ["compatibility", "distance from uniform", "compare with maximum entropy"],
                ["infeasible in any week feasible for primary", "counterfactual conclusions reverse materially"],
                ["arbitrary uniform center", "boundary solutions"],
                "fallback",
                "Convex, interpretable, and executable if entropy optimization has numerical issues."
            ),
            candidate(
                "supervised fan-vote neural network",
                "Fit a nonlinear predictor of observed fan-vote share from contestant attributes and scores.",
                ["true fan-vote labels exist"],
                ["no source available"],
                ["would require labeled out-of-sample fan votes"],
                ["no target labels", "validation cannot be performed"],
                ["fabricated proxy target", "overfit small data"],
                "rejected",
                "The official data do not contain fan votes, so supervised training would manufacture the target.",
                failed_gates=["data_gate", "identifiability_gate", "validation_gate"],
                rejection_evidence=["EDA field fan_vote_target_available=false", "official PDF describes fan votes as unknown and secret"]
            )
        ],
        "primary_model": "maximum-entropy constrained votes",
        "fallback_model": "quadratic minimum-deviation votes",
        "stop_conditions": ["human approval absent or stale", "less than 90% of evaluable weeks reconstructable", "unresolved constraint convention changes headline results"],
        "team_approval": approval()
    }

    q2 = {
        "problem_id": "2026-MCM-C",
        "subquestion": "Q2",
        "target_claim": "Rank and percentage rules produce measurably different eliminations and fan influence under the same plausible votes.",
        "data_audit": {
            "unit_table_complete": True,
            "temporal_order_preserved": True,
            "leakage_risks": ["final placement cannot determine weekly counterfactuals"],
            "missingness_notes": "Only Q1-current active rosters and supported elimination weeks enter comparison."
        },
        "baseline": {
            "name": "deterministic point replay",
            "reason": "directly implements both published combination formulas",
            "implementation": "src/baseline/q2_point_replay.py",
            "validation": "replay consistency and hand-checked official appendix examples"
        },
        "candidates": [
            candidate(
                "uncertainty-integrated counterfactual replay",
                "Apply rank and percentage rules to every feasible/bootstrap Q1 vote draw and summarize disagreement and fan-favor metrics with intervals.",
                ["fan response is fixed under a counterfactual weekly rule", "tie handling is common across rules"],
                ["RESULT-Q1-VOTES", "official problem appendix formulas"],
                ["official appendix hand checks", "replay historical method", "multi-draw stability", "named controversy cases"],
                ["rule recommendation reverses in more than 25% of feasible draws", "appendix examples are not reproduced"],
                ["tie sensitivity", "uncertain bottom-two save proxy", "behavioral response omitted"],
                "primary",
                "Propagates the central Q1 uncertainty into every comparison instead of treating one latent vector as truth."
            ),
            candidate(
                "deterministic maximum-entropy replay",
                "Apply both rules once to Q1 maximum-entropy point estimates.",
                ["point estimate is adequate for directional comparison"],
                ["RESULT-Q1-VOTES"],
                ["formula unit tests", "named controversy cases"],
                ["direction differs from uncertainty-integrated result", "more than 10% tie-sensitive weeks"],
                ["understates partial-identification uncertainty"],
                "fallback",
                "Simple and reproducible when vote sampling fails, but conclusions must be weakened."
            ),
            candidate(
                "final-placement-only rule comparison",
                "Infer weekly rule quality from final season placement.",
                ["final placement is an unbiased weekly outcome label"],
                ["placement field"],
                ["not valid without weekly outcomes"],
                ["uses future outcome to evaluate prior weeks"],
                ["post-outcome leakage"],
                "rejected",
                "Final placement occurs after the weekly decisions and leaks the future.",
                failed_gates=["assumption_gate", "validation_gate"],
                rejection_evidence=["EDA leakage_fields_forbidden_in_weekly_prediction includes placement"]
            )
        ],
        "primary_model": "uncertainty-integrated counterfactual replay",
        "fallback_model": "deterministic maximum-entropy replay",
        "stop_conditions": ["Q1 evidence stale", "human approval absent or stale", "official combination formula unit test fails"],
        "team_approval": approval()
    }

    q3 = {
        "problem_id": "2026-MCM-C",
        "subquestion": "Q3",
        "target_claim": "Partner and celebrity characteristics have stable predictive associations with judge scores and estimated fan support after season/week adjustment.",
        "data_audit": {
            "unit_table_complete": True,
            "temporal_order_preserved": True,
            "leakage_risks": ["placement/results/future scores forbidden", "repeat contestants and partners require grouped validation"],
            "missingness_notes": "Missing home state is encoded explicitly; rare categories are pooled inside training folds."
        },
        "baseline": {
            "name": "season-week adjusted mean",
            "reason": "transparent no-characteristic reference",
            "implementation": "src/baseline/q3_adjusted_mean.py",
            "validation": "leave-seasons-out RMSE for judge mean and Q1 fan share"
        },
        "candidates": [
            candidate(
                "grouped cross-fitted ridge",
                "One-hot encode categorical characteristics and standardize numeric features inside a pipeline; fit ridge models with entire seasons held out.",
                ["reported associations are predictive, not causal", "Q1 estimates are uncertainty-weighted outcomes"],
                ["DATA-PROCESSED-C", "RESULT-Q1-VOTES", "regularization selected inside training seasons"],
                ["leave-seasons-out RMSE", "bootstrap coefficient stability", "partner-feature ablation", "Q1 draw propagation"],
                ["does not beat adjusted mean", "coefficient sign stable in fewer than 70% bootstraps", "partner benefit vanishes on held-out seasons"],
                ["rare category instability", "repeat contestant dependence", "latent-vote measurement error"],
                "primary",
                "Preprocessing stays inside grouped folds and regularization matches the sample size and interpretability requirement."
            ),
            candidate(
                "hierarchical shrinkage approximation",
                "Estimate season/week fixed effects and partially pooled partner/industry deviations using ridge penalties.",
                ["partial pooling approximates exchangeable group effects", "associations are not causal"],
                ["DATA-PROCESSED-C", "RESULT-Q1-VOTES"],
                ["leave-season-out RMSE", "group-effect bootstrap", "compare with grouped ridge"],
                ["optimizer fails", "effect ranking unstable", "no holdout improvement"],
                ["small partner groups", "approximation to full mixed model"],
                "fallback",
                "Retains group shrinkage with a simpler deterministic implementation."
            ),
            candidate(
                "deep embedding network",
                "Learn partner, industry, and contestant embeddings with a multilayer network.",
                ["large labeled sample supports nonlinear embeddings"],
                ["2,777 active rows but only 421 contestants and latent fan labels"],
                ["grouped holdout"],
                ["expected variance exceeds simpler model", "weak interpretability"],
                ["overfit categories", "unstable effects"],
                "rejected",
                "Complexity is not justified by the grouped sample size or claim need.",
                failed_gates=["complexity_gate", "engineering_gate"],
                rejection_evidence=["421 contestants and no observed fan-vote labels", "interpretability is required by the question"]
            )
        ],
        "primary_model": "grouped cross-fitted ridge",
        "fallback_model": "hierarchical shrinkage approximation",
        "stop_conditions": ["Q1 evidence stale", "human approval absent or stale", "preprocessing leakage detected", "no candidate beats adjusted mean"],
        "team_approval": approval()
    }

    q4 = {
        "problem_id": "2026-MCM-C",
        "subquestion": "Q4",
        "target_claim": "A transparent weekly rule improves a documented judge-quality/fan-influence/stability trade-off across plausible vote distributions.",
        "data_audit": {
            "unit_table_complete": True,
            "temporal_order_preserved": True,
            "leakage_risks": ["no engagement label exists", "normative weights must not be fit to final placement"],
            "missingness_notes": "Only weeks supported by current Q1 evidence enter the rule grid."
        },
        "baseline": {
            "name": "50/50 percentage rule",
            "reason": "transparent current-style reference and exact official formula family",
            "implementation": "src/baseline/q4_equal_percent.py",
            "validation": "historical replay over Q1 uncertainty and controversy cases"
        },
        "candidates": [
            candidate(
                "robust weighted-percent rule with bottom-two safeguard",
                "Choose judge weight a on a fixed grid to minimize worst-case normalized judge-discordance, fan-disfranchisement, and rule-instability loss over Q1 vote draws; judges save the technically stronger of the bottom two.",
                ["three published criteria represent the recommendation goal", "weight preferences are reported as sensitivity ranges", "judge save uses observed score only"],
                ["RESULT-Q1-VOTES", "RESULT-Q2-COUNTERFACTUAL", "criterion weights declared in config"],
                ["multi-draw scenario grid", "alternative criterion weights", "rank-reversal test", "controversy cases", "failure boundary"],
                ["selected weight changes by more than 0.20 across reasonable criterion weights", "no Pareto improvement over baseline", "more than 25% of draws reverse recommendation"],
                ["normative trade-off", "fan behavioral response", "bottom-two judge-save concentrates judge power"],
                "primary",
                "Produces an explicit transparent rule and makes normative sensitivity visible rather than learning an unavailable engagement target."
            ),
            candidate(
                "trimmed rank aggregation",
                "Add judge and fan ranks after capping either side's maximum rank contribution, then apply a bottom-two safeguard.",
                ["rank robustness is preferable to cardinal differences", "cap is policy-chosen"],
                ["RESULT-Q1-VOTES", "official rank formula"],
                ["tie frequency", "counterfactual stability", "criterion-weight sensitivity"],
                ["excess ties", "no improvement over baseline", "controversy outcomes worsen"],
                ["information loss from ranks", "tie handling dominates"],
                "fallback",
                "Simple, communicable alternative if weighted-percent recommendation is fragile."
            ),
            candidate(
                "engagement-optimized learned rule",
                "Fit a policy to maximize viewer engagement and retention.",
                ["weekly engagement labels are available"],
                ["no engagement fields in official data"],
                ["would require held-out engagement outcome"],
                ["objective cannot be measured", "proxy would be fabricated"],
                ["Goodhart effects", "unverifiable black box"],
                "rejected",
                "The requested dataset contains no engagement target, so the objective is not identifiable.",
                failed_gates=["data_gate", "identifiability_gate", "validation_gate"],
                rejection_evidence=["official 53-column file contains no audience or engagement field"]
            )
        ],
        "primary_model": "robust weighted-percent rule with bottom-two safeguard",
        "fallback_model": "trimmed rank aggregation",
        "stop_conditions": ["upstream Q1/Q2 evidence stale", "human approval absent or stale", "recommendation reverses in more than 25% of plausible vote draws"],
        "team_approval": approval()
    }
    return {"Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for question, plan in plans().items():
        path = args.output / f"{question}.json"
        path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
