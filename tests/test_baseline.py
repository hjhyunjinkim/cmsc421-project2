from pathlib import Path

from planner import (
    bfs,
    ground,
    load_domain,
    load_problem,
    solve_graphplan,
    validate_parallel,
    validate_sequential,
)

ROOT = Path(__file__).resolve().parents[1]


def solve(domain_rel: str, problem_rel: str):
    domain = load_domain(ROOT / domain_rel)
    problem = load_problem(ROOT / problem_rel)
    actions = ground(domain, problem)
    bfs_result = bfs(problem, actions)
    gp_result = solve_graphplan(problem, actions)
    return problem, actions, bfs_result, gp_result


def test_blocks_baseline_solved_by_both_planners():
    problem, actions, bfs_result, gp_result = solve(
        "pddl/blocksworld/domain.pddl",
        "pddl/blocksworld/baseline3.pddl",
    )
    assert actions
    assert bfs_result.success
    assert gp_result.success
    assert validate_sequential(problem, bfs_result.plan)[0]
    assert validate_parallel(problem, gp_result.plan)[0]


def test_elevator_baseline_solved_by_both_planners():
    problem, actions, bfs_result, gp_result = solve(
        "pddl/elevator/domain.pddl",
        "pddl/elevator/baseline.pddl",
    )
    assert actions
    assert bfs_result.success
    assert gp_result.success
    assert validate_sequential(problem, bfs_result.plan)[0]
    assert validate_parallel(problem, gp_result.plan)[0]


def test_ferry_baseline_solved_by_both_planners():
    problem, actions, bfs_result, gp_result = solve(
        "pddl/ferry/domain.pddl",
        "pddl/ferry/baseline.pddl",
    )
    assert actions
    assert bfs_result.success
    assert gp_result.success
    assert validate_sequential(problem, bfs_result.plan)[0]
    assert validate_parallel(problem, gp_result.plan)[0]
