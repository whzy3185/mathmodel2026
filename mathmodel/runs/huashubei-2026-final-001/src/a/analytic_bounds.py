"""Rigorous direct-bridge bounds for the official periodic clipping rule."""

from __future__ import annotations

import math
from dataclasses import dataclass


BOX_SIDE = 10_000.0
GAP = 1.8
ROD_LENGTH = 5_000.0
ROD_RADIUS = 30.0
SPHERE_RADIUS = 200.0
CUBE_VOLUME = BOX_SIDE**3
A_VOLUME = math.pi * ROD_RADIUS**2 * ROD_LENGTH
B_VOLUME = 4 * math.pi * SPHERE_RADIUS**3 / 3
A_COST = 1.05 * A_VOLUME / 1e9
B_COST = 0.05 * B_VOLUME / 1e9


Q_A = ROD_LENGTH / (2 * BOX_SIDE) + 2 * ROD_RADIUS * (math.pi / 4) / BOX_SIDE
Q_B = 2 * SPHERE_RADIUS / BOX_SIDE


def direct_bridge_probability(a_count: int, b_count: int) -> float:
    return 1 - (1 - Q_A) ** a_count * (1 - Q_B) ** b_count


def non_direct_terminal_pair_upper_bound(a_count: int, b_count: int) -> float:
    """Upper-bound a non-direct path by opposite-electrode endpoint contacts.

    If no particle directly wraps from left to right, every conducting path must
    contain distinct particles touching the two electrode gap layers. A union
    bound over ordered particle pairs is independent of inter-particle geometry.
    """
    per_side = GAP / BOX_SIDE
    total = a_count + b_count
    return total * (total - 1) * per_side**2


def conduction_upper_bound(a_count: int, b_count: int) -> float:
    return min(
        1.0,
        direct_bridge_probability(a_count, b_count)
        + non_direct_terminal_pair_upper_bound(a_count, b_count),
    )


def material_cost(a_count: int, b_count: int) -> float:
    return a_count * A_COST + b_count * B_COST


@dataclass(frozen=True)
class IntegerCandidate:
    a_count: int
    b_count: int

    @property
    def cost(self) -> float:
        return material_cost(self.a_count, self.b_count)

    @property
    def lower(self) -> float:
        return direct_bridge_probability(self.a_count, self.b_count)

    @property
    def upper(self) -> float:
        return conduction_upper_bound(self.a_count, self.b_count)


def enumerate_cheaper_than(
    reference: IntegerCandidate, *, min_a: int = 0, min_b: int = 0
) -> list[IntegerCandidate]:
    candidates: list[IntegerCandidate] = []
    max_a = int(math.floor((reference.cost - 1e-15) / A_COST))
    for a_count in range(min_a, max_a + 1):
        remaining = reference.cost - a_count * A_COST
        max_b = int(math.floor((remaining - 1e-15) / B_COST))
        for b_count in range(min_b, max_b + 1):
            candidate = IntegerCandidate(a_count, b_count)
            if candidate.cost < reference.cost - 1e-15:
                candidates.append(candidate)
    return candidates


def cheaper_frontier(
    reference: IntegerCandidate, *, min_a: int = 0, min_b: int = 0
) -> list[IntegerCandidate]:
    candidates = enumerate_cheaper_than(reference, min_a=min_a, min_b=min_b)
    frontier: list[IntegerCandidate] = []
    for a_count in sorted({candidate.a_count for candidate in candidates}):
        options = [candidate for candidate in candidates if candidate.a_count == a_count]
        frontier.append(max(options, key=lambda candidate: candidate.b_count))
    return frontier


def prove_q3() -> dict:
    rows = []
    for count in range(1, 9):
        rows.append({
            "a_count": count,
            "direct_bridge_lower_bound": direct_bridge_probability(count, 0),
            "non_direct_path_upper_addition": non_direct_terminal_pair_upper_bound(count, 0),
            "conduction_upper_bound": conduction_upper_bound(count, 0),
        })
    return {
        "selected_a_count": 8,
        "selected_lower_bound": direct_bridge_probability(8, 0),
        "lower_neighbor_upper_bound": conduction_upper_bound(7, 0),
        "proof_rows": rows,
    }


def prove_q4() -> dict:
    selected = IntegerCandidate(0, 57)
    cheaper = enumerate_cheaper_than(selected)
    frontier = cheaper_frontier(selected)
    worst = max(cheaper, key=lambda candidate: candidate.upper)
    if selected.lower < 0.90 or worst.upper >= 0.90:
        raise AssertionError("analytic Q4 proof failed")
    positive_selected = IntegerCandidate(1, 50)
    positive_cheaper = enumerate_cheaper_than(positive_selected, min_a=1, min_b=1)
    positive_worst = max(positive_cheaper, key=lambda candidate: candidate.upper)
    if positive_selected.lower < 0.90 or positive_worst.upper >= 0.90:
        raise AssertionError("positive-mixture Q4 proof failed")
    return {
        "selected": {
            "a_count": selected.a_count,
            "b_count": selected.b_count,
            "cost_cny": selected.cost,
            "direct_bridge_lower_bound": selected.lower,
        },
        "cheaper_integer_candidate_count": len(cheaper),
        "maximum_upper_bound_among_cheaper": {
            "a_count": worst.a_count,
            "b_count": worst.b_count,
            "cost_cny": worst.cost,
            "conduction_upper_bound": worst.upper,
        },
        "cheaper_frontier": [
            {
                "a_count": candidate.a_count,
                "b_count": candidate.b_count,
                "cost_cny": candidate.cost,
                "direct_bridge_probability": candidate.lower,
                "conduction_upper_bound": candidate.upper,
            }
            for candidate in frontier
        ],
        "strictly_positive_mixture": {
            "selected": {
                "a_count": positive_selected.a_count,
                "b_count": positive_selected.b_count,
                "cost_cny": positive_selected.cost,
                "direct_bridge_lower_bound": positive_selected.lower,
            },
            "cheaper_integer_candidate_count": len(positive_cheaper),
            "maximum_upper_bound_among_cheaper": {
                "a_count": positive_worst.a_count,
                "b_count": positive_worst.b_count,
                "cost_cny": positive_worst.cost,
                "conduction_upper_bound": positive_worst.upper,
            },
        },
    }
