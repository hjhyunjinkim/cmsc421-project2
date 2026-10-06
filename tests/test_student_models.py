from pathlib import Path

import pytest

from planner import bfs, ground, load_domain, load_problem, solve_graphplan

ROOT = Path(__file__).resolve().parents[1]
TODO = "TODO-STUDENT: UNFINISHED"


def require_finished(*paths: str) -> None:
    unfinished = [p for p in paths if TODO in (ROOT / p).read_text()]
    if unfinished:
        pytest.skip("unfinished student template(s): " + ", ".join(unfinished))


def load(domain_rel: str, problem_rel: str):
    domain = load_domain(ROOT / domain_rel)
    problem = load_problem(ROOT / problem_rel)
    return domain, problem, ground(domain, problem)


def schema(domain, name: str):
    matches = [a for a in domain.actions if a.name == name]
    assert len(matches) == 1, f"expected exactly one action schema named {name}"
    return matches[0]


def assert_solved(problem, actions):
    bfs_result = bfs(problem, actions)
    gp_result = solve_graphplan(problem, actions)
    assert bfs_result.success, bfs_result.reason
    assert gp_result.success, gp_result.reason
    return bfs_result, gp_result


def test_sussman3_exact_instance_and_solvable():
    d = "pddl/blocksworld/domain.pddl"
    p = "pddl/blocksworld/sussman3.pddl"
    require_finished(p)
    _, problem, actions = load(d, p)

    assert problem.objects == {"a": "block", "b": "block", "c": "block"}
    assert problem.init == frozenset({
        ("on", "c", "a"),
        ("ontable", "a"),
        ("ontable", "b"),
        ("clear", "b"),
        ("clear", "c"),
        ("handempty",),
    })
    assert problem.goal_pos == frozenset({("on", "a", "b"), ("on", "b", "c")})
    assert len(actions) == 18
    assert_solved(problem, actions)


def test_sussman6_exact_instance_and_solvable():
    d = "pddl/blocksworld/domain.pddl"
    p = "pddl/blocksworld/sussman6.pddl"
    require_finished(p)
    _, problem, actions = load(d, p)

    assert problem.objects == {x: "block" for x in "abcdef"}
    assert problem.init == frozenset({
        ("on", "c", "a"),
        ("ontable", "a"),
        ("ontable", "b"),
        ("ontable", "d"),
        ("ontable", "e"),
        ("ontable", "f"),
        ("clear", "b"),
        ("clear", "c"),
        ("clear", "d"),
        ("clear", "e"),
        ("clear", "f"),
        ("handempty",),
    })
    assert problem.goal_pos == frozenset({
        ("on", "a", "b"),
        ("on", "b", "c"),
        ("on", "c", "d"),
        ("on", "d", "e"),
        ("on", "e", "f"),
    })
    assert len(actions) == 72
    assert_solved(problem, actions)


def test_two_gripper_domain_and_problem_are_exact_and_parallelize():
    d = "pddl/blocksworld/domain_two_grippers.pddl"
    p = "pddl/blocksworld/sussman3_two_grippers.pddl"
    require_finished(d, p)
    domain, problem, actions = load(d, p)

    assert domain.name == "blocks-two-grippers"
    assert problem.objects == {
        "a": "block", "b": "block", "c": "block",
        "left": "gripper", "right": "gripper",
    }
    assert problem.init == frozenset({
        ("on", "c", "a"),
        ("ontable", "a"),
        ("ontable", "b"),
        ("clear", "b"),
        ("clear", "c"),
        ("free", "left"),
        ("free", "right"),
    })
    assert problem.goal_pos == frozenset({("on", "a", "b"), ("on", "b", "c")})

    for name in ("pickup", "putdown", "stack", "unstack"):
        action = schema(domain, name)
        assert any(param_type == "gripper" for _, param_type in action.parameters)
        referenced = action.pos_pre | action.neg_pre | action.add_eff | action.del_eff
        assert any(f[0] in {"free", "holding"} for f in referenced)

    assert len(actions) == 36
    _, gp = assert_solved(problem, actions)
    assert any(len(step) > 1 for step in gp.plan), "expected at least one parallel step"


def test_split_service_elevator_exact_links_transfer_and_solvable():
    d = "pddl/elevator/domain_split_service.pddl"
    p = "pddl/elevator/split_service.pddl"
    require_finished(d, p)
    domain, problem, actions = load(d, p)

    assert domain.name == "elevator-split-service"
    assert problem.objects == {
        "even": "elevator", "odd": "elevator",
        "p1": "passenger", "p2": "passenger",
        **{f"f{i}": "floor" for i in range(7)},
    }

    required_dynamic = {
        ("lift-at", "even", "f2"),
        ("lift-at", "odd", "f5"),
        ("passenger-at", "p1", "f2"),
        ("passenger-at", "p2", "f5"),
    }
    required_links = {
        ("link", "even", "f0", "f2"), ("link", "even", "f2", "f0"),
        ("link", "even", "f2", "f4"), ("link", "even", "f4", "f2"),
        ("link", "even", "f4", "f6"), ("link", "even", "f6", "f4"),
        ("link", "odd", "f0", "f1"), ("link", "odd", "f1", "f0"),
        ("link", "odd", "f1", "f3"), ("link", "odd", "f3", "f1"),
        ("link", "odd", "f3", "f5"), ("link", "odd", "f5", "f3"),
    }
    assert problem.init == frozenset(required_dynamic | required_links)
    assert problem.goal_pos == frozenset({
        ("passenger-at", "p1", "f3"),
        ("passenger-at", "p2", "f4"),
    })

    move = schema(domain, "move")
    assert ("link", "?e", "?from", "?to") in move.pos_pre
    assert ("lift-at", "?e", "?from") in move.pos_pre
    schema(domain, "board")
    schema(domain, "leave")

    assert len(actions) == 68
    assert_solved(problem, actions)


def test_ferry_cross_traffic_exact_instance_and_solvable():
    d = "pddl/ferry/domain.pddl"
    p = "pddl/ferry/ferry_cross_traffic.pddl"
    require_finished(p)
    _, problem, actions = load(d, p)

    assert problem.objects == {
        "c1": "car", "c2": "car", "c3": "car", "c4": "car",
        "left-bank": "location", "right-bank": "location",
    }
    assert problem.init == frozenset({
        ("car-at", "c1", "left-bank"),
        ("car-at", "c2", "left-bank"),
        ("car-at", "c3", "right-bank"),
        ("car-at", "c4", "right-bank"),
        ("ferry-at", "left-bank"),
        ("empty",),
        ("route", "left-bank", "right-bank"),
        ("route", "right-bank", "left-bank"),
    })
    assert problem.goal_pos == frozenset({
        ("car-at", "c1", "right-bank"),
        ("car-at", "c2", "right-bank"),
        ("car-at", "c3", "left-bank"),
        ("car-at", "c4", "left-bank"),
    })
    assert len(actions) == 18
    assert_solved(problem, actions)


def test_two_ferries_exact_instance_and_parallelize():
    d = "pddl/ferry/domain_two_ferries.pddl"
    p = "pddl/ferry/ferry_cross_traffic_two.pddl"
    require_finished(d, p)
    domain, problem, actions = load(d, p)

    assert domain.name == "ferry-two"
    assert problem.objects == {
        "c1": "car", "c2": "car", "c3": "car", "c4": "car",
        "ferry1": "ferry", "ferry2": "ferry",
        "left-bank": "location", "right-bank": "location",
    }
    assert problem.init == frozenset({
        ("car-at", "c1", "left-bank"),
        ("car-at", "c2", "left-bank"),
        ("car-at", "c3", "right-bank"),
        ("car-at", "c4", "right-bank"),
        ("ferry-at", "ferry1", "left-bank"),
        ("ferry-at", "ferry2", "right-bank"),
        ("empty", "ferry1"),
        ("empty", "ferry2"),
        ("route", "left-bank", "right-bank"),
        ("route", "right-bank", "left-bank"),
    })
    assert problem.goal_pos == frozenset({
        ("car-at", "c1", "right-bank"),
        ("car-at", "c2", "right-bank"),
        ("car-at", "c3", "left-bank"),
        ("car-at", "c4", "left-bank"),
    })

    for name in ("board", "debark", "sail"):
        action = schema(domain, name)
        assert any(param_type == "ferry" for _, param_type in action.parameters)

    board = schema(domain, "board")
    assert ("empty", "?f") in board.pos_pre
    assert ("empty", "?f") in board.del_eff
    assert ("onboard", "?c", "?f") in board.add_eff

    debark = schema(domain, "debark")
    assert ("onboard", "?c", "?f") in debark.pos_pre
    assert ("empty", "?f") in debark.add_eff

    sail = schema(domain, "sail")
    assert ("ferry-at", "?f", "?from") in sail.pos_pre

    assert len(actions) == 36
    _, gp = assert_solved(problem, actions)
    assert any(len(step) > 1 for step in gp.plan), "expected two-ferry parallelism"
