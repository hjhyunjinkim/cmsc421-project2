from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from planner import (
    bfs,
    ground,
    load_domain,
    load_problem,
    reachable_states,
    solve_graphplan,
    validate_parallel,
    validate_sequential,
)

ROOT = Path(__file__).resolve().parent
TODO_MARKER = "TODO-STUDENT: UNFINISHED"


@dataclass(frozen=True)
class Case:
    experiment_id: str
    name: str
    domain: str
    problem: str


CASES = [
    Case("B0", "blocks-baseline-3", "pddl/blocksworld/domain.pddl", "pddl/blocksworld/baseline3.pddl"),
    Case("B1", "blocks-sussman-3", "pddl/blocksworld/domain.pddl", "pddl/blocksworld/sussman3.pddl"),
    Case("B2", "blocks-sussman-6", "pddl/blocksworld/domain.pddl", "pddl/blocksworld/sussman6.pddl"),
    Case("B3", "blocks-two-grippers", "pddl/blocksworld/domain_two_grippers.pddl", "pddl/blocksworld/sussman3_two_grippers.pddl"),
    Case("E0", "elevator-baseline", "pddl/elevator/domain.pddl", "pddl/elevator/baseline.pddl"),
    Case("E1", "elevator-split-service", "pddl/elevator/domain_split_service.pddl", "pddl/elevator/split_service.pddl"),
    Case("F0", "ferry-baseline", "pddl/ferry/domain.pddl", "pddl/ferry/baseline.pddl"),
    Case("F1", "ferry-cross-traffic", "pddl/ferry/domain.pddl", "pddl/ferry/ferry_cross_traffic.pddl"),
    Case("F2", "ferry-two-ferries", "pddl/ferry/domain_two_ferries.pddl", "pddl/ferry/ferry_cross_traffic_two.pddl"),
]


def unfinished(path: Path) -> bool:
    return TODO_MARKER in path.read_text()


def sequential_plan_text(plan) -> list[str]:
    return [f"{i:02d}. {action.label}" for i, action in enumerate(plan, start=1)]


def parallel_plan_text(plan) -> list[str]:
    lines = []
    for t, step in enumerate(plan):
        body = " | ".join(action.label for action in step) if step else "<noop>"
        lines.append(f"t{t:02d}: {body}")
    return lines


def run_case(case: Case, args) -> tuple[list[dict], list[str]]:
    domain_path = ROOT / case.domain
    problem_path = ROOT / case.problem

    if unfinished(domain_path) or unfinished(problem_path):
        print(f"SKIP  {case.experiment_id} ({case.name}): unfinished TODO file")
        return [], [f"## {case.experiment_id} — {case.name}", "SKIPPED: unfinished TODO file", ""]

    domain = load_domain(domain_path)
    problem = load_problem(problem_path)
    actions = ground(domain, problem)

    reachable_count = ""
    reachable_exact = ""
    enumeration_s = ""
    if args.enumerate_reachable:
        count, exact, elapsed = reachable_states(problem.init, actions, cap=args.node_limit)
        reachable_count = count
        reachable_exact = exact
        enumeration_s = f"{elapsed:.6f}"

    rows: list[dict] = []
    plan_lines: list[str] = [
        f"## {case.experiment_id} — {case.name}",
        f"Domain: {case.domain}",
        f"Problem: {case.problem}",
        f"Ground actions: {len(actions)}",
        "",
    ]

    bfs_result = bfs(problem, actions, max_nodes=args.node_limit)
    bfs_valid, bfs_message = (
        validate_sequential(problem, bfs_result.plan)
        if bfs_result.success
        else (False, bfs_result.reason)
    )
    rows.append(
        {
            "experiment_id": case.experiment_id,
            "case": case.name,
            "planner": "forward-strips-bfs",
            "success": bfs_result.success,
            "plan_valid": bfs_valid,
            "ground_actions": len(actions),
            "states_generated": bfs_result.generated,
            "states_expanded": bfs_result.expanded,
            "visited_states": bfs_result.visited,
            "max_frontier": bfs_result.max_frontier,
            "reachable_states": reachable_count,
            "reachable_exact": reachable_exact,
            "enumeration_s": enumeration_s,
            "plan_actions": len(bfs_result.plan),
            "makespan": len(bfs_result.plan),
            "graph_levels": "",
            "fact_nodes": "",
            "action_nodes": "",
            "action_mutexes": "",
            "fact_mutexes": "",
            "runtime_s": f"{bfs_result.elapsed_s:.6f}",
            "reason": bfs_result.reason,
        }
    )
    plan_lines += ["Forward STRIPS / BFS:"]
    if bfs_result.success:
        plan_lines += sequential_plan_text(bfs_result.plan)
        plan_lines.append(f"Validation: {bfs_message}")
    else:
        plan_lines.append(f"FAILED: {bfs_result.reason}")
    plan_lines.append("")

    gp_result = solve_graphplan(problem, actions, max_levels=args.max_levels)
    gp_valid, gp_message = (
        validate_parallel(problem, gp_result.plan)
        if gp_result.success
        else (False, gp_result.reason)
    )
    rows.append(
        {
            "experiment_id": case.experiment_id,
            "case": case.name,
            "planner": "graphplan",
            "success": gp_result.success,
            "plan_valid": gp_valid,
            "ground_actions": len(actions),
            "states_generated": "",
            "states_expanded": "",
            "visited_states": "",
            "max_frontier": "",
            "reachable_states": reachable_count,
            "reachable_exact": reachable_exact,
            "enumeration_s": enumeration_s,
            "plan_actions": sum(len(step) for step in gp_result.plan),
            "makespan": len(gp_result.plan),
            "graph_levels": gp_result.levels,
            "fact_nodes": gp_result.fact_nodes,
            "action_nodes": gp_result.action_nodes,
            "action_mutexes": gp_result.action_mutexes,
            "fact_mutexes": gp_result.fact_mutexes,
            "runtime_s": f"{gp_result.elapsed_s:.6f}",
            "reason": gp_result.reason,
        }
    )
    plan_lines += ["GraphPlan:"]
    if gp_result.success:
        plan_lines += parallel_plan_text(gp_result.plan)
        plan_lines.append(f"Validation: {gp_message}")
    else:
        plan_lines.append(f"FAILED: {gp_result.reason}")
    plan_lines.append("")

    print(
        f"DONE  {case.experiment_id} ({case.name}): actions={len(actions)}, "
        f"BFS={'ok' if bfs_result.success else bfs_result.reason}, "
        f"GraphPlan={'ok' if gp_result.success else gp_result.reason}"
    )
    return rows, plan_lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CMSC 421 Project 2 experiments")
    parser.add_argument("--node-limit", type=int, default=250_000)
    parser.add_argument("--max-levels", type=int, default=30)
    parser.add_argument(
        "--enumerate-reachable",
        action="store_true",
        help="also enumerate reachable states up to --node-limit",
    )
    parser.add_argument("--out", default="results/results.csv")
    args = parser.parse_args()

    rows: list[dict] = []
    plans: list[str] = []

    for case in CASES:
        case_rows, case_plans = run_case(case, args)
        rows.extend(case_rows)
        plans.extend(case_plans)

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if rows:
        with out_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {out_path.relative_to(ROOT)}")
    else:
        print("No completed cases were available to write.")

    plans_path = out_path.parent / "plans.txt"
    plans_path.write_text("\n".join(plans) + "\n")
    print(f"Wrote {plans_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
