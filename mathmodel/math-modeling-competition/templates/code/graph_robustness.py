"""Network robustness under random and targeted node failures."""

from __future__ import annotations

from typing import Any

import networkx as nx
import numpy as np


def graph_metrics(graph: nx.Graph, original_nodes: int | None = None) -> dict[str, float]:
    denominator = original_nodes if original_nodes is not None else graph.number_of_nodes()
    if graph.number_of_nodes() == 0 or denominator == 0:
        return {"largest_component_fraction": 0.0, "global_efficiency": 0.0}
    largest = max((len(component) for component in nx.connected_components(graph)), default=0)
    return {
        "largest_component_fraction": float(largest / denominator),
        "global_efficiency": float(nx.global_efficiency(graph)),
    }


def removal_trajectory(
    graph: nx.Graph,
    *,
    mode: str,
    fractions: list[float],
    seed: int = 0,
) -> dict[str, Any]:
    if graph.is_directed():
        raise ValueError("use an undirected graph")
    if any(fraction < 0 or fraction > 1 for fraction in fractions):
        raise ValueError("fractions must lie in [0, 1]")
    nodes = list(graph.nodes())
    rng = np.random.default_rng(seed)
    if mode == "random":
        order = list(rng.permutation(nodes))
    elif mode == "targeted":
        order = [node for node, _ in sorted(graph.degree, key=lambda pair: (-pair[1], str(pair[0])))]
    else:
        raise ValueError("mode must be random or targeted")
    trajectory = []
    for fraction in fractions:
        remove_count = int(round(fraction * len(nodes)))
        damaged = graph.copy()
        damaged.remove_nodes_from(order[:remove_count])
        trajectory.append({"removed_fraction": fraction, **graph_metrics(damaged, len(nodes))})
    return {"status": "ok", "mode": mode, "seed": seed, "trajectory": trajectory}


def compare_failure_modes(graph: nx.Graph, fractions: list[float], seed: int = 0) -> dict[str, Any]:
    return {
        "random": removal_trajectory(graph, mode="random", fractions=fractions, seed=seed),
        "targeted": removal_trajectory(graph, mode="targeted", fractions=fractions, seed=seed),
    }
