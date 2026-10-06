from pathlib import Path

import pytest

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


def assert_action_names(domain, expected: set[str]) -> None:
    actual = {a.name for a in domain.actions}
    assert actual == expected, f"expected action schemas {sorted(expected)}, got {sorted(actual)}"


def assert_ground_action(
    actions,
    name: str,
    *,
    pos_pre: set[tuple[str, ...]],
    add_eff: set[tuple[str, ...]],
    del_eff: set[tuple[str, ...]],
) -> None:
    """Require a grounded action with exactly the specified STRIPS semantics.

    Matching on grounded facts rather than parameter names lets students choose
    harmless variable names/order while still enforcing the required world model.
    """
    matches = [
        a
        for a in actions
        if a.name == name
        and a.pos_pre == frozenset(pos_pre)
        and not a.neg_pre
        and a.add_eff == frozenset(add_eff)
        and a.del_eff == frozenset(del_eff)
    ]
    assert matches, f"no grounded {name} action had the required preconditions/effects"


def assert_solved(problem, actions):
    bfs_result = bfs(problem, actions)
    gp_result = solve_graphplan(problem, actions)
    assert bfs_result.success, bfs_result.reason
    assert gp_result.success, gp_result.reason

    bfs_valid, bfs_message = validate_sequential(problem, bfs_result.plan)
    gp_valid, gp_message = validate_parallel(problem, gp_result.plan)
    assert bfs_valid, bfs_message
    assert gp_valid, gp_message
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
    assert not problem.goal_neg
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
    assert not problem.goal_neg
    assert len(actions) == 72
    assert_solved(problem, actions)


def test_two_gripper_domain_and_problem_are_exact_and_parallelize():
    d = "pddl/blocksworld/domain_two_grippers.pddl"
    p = "pddl/blocksworld/sussman3_two_grippers.pddl"
    require_finished(d, p)
    domain, problem, actions = load(d, p)

    assert domain.name == "blocks-two-grippers"
    assert_action_names(domain, {"pickup", "putdown", "stack", "unstack"})
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
    assert not problem.goal_neg

    # Exact representative grounded semantics. This catches models that merely
    # mention a gripper but fail to make free/holding a true capacity-one resource.
    assert_ground_action(
        actions,
        "pickup",
        pos_pre={("ontable", "a"), ("clear", "a"), ("free", "left")},
        add_eff={("holding", "left", "a")},
        del_eff={("ontable", "a"), ("clear", "a"), ("free", "left")},
    )
    assert_ground_action(
        actions,
        "putdown",
        pos_pre={("holding", "left", "a")},
        add_eff={("ontable", "a"), ("clear", "a"), ("free", "left")},
        del_eff={("holding", "left", "a")},
    )
    assert_ground_action(
        actions,
        "stack",
        pos_pre={("holding", "left", "a"), ("clear", "b")},
        add_eff={("on", "a", "b"), ("clear", "a"), ("free", "left")},
        del_eff={("holding", "left", "a"), ("clear", "b")},
    )
    assert_ground_action(
        actions,
        "unstack",
        pos_pre={("on", "a", "b"), ("clear", "a"), ("free", "left")},
        add_eff={("holding", "left", "a"), ("clear", "b")},
        del_eff={("on", "a", "b"), ("clear", "a"), ("free", "left")},
    )

    assert len(actions) == 36
    _, gp = assert_solved(problem, actions)
    assert any(len(step) > 1 for step in gp.plan), "expected at least one parallel step"


def test_split_service_elevator_exact_links_transfer_and_solvable():
    d = "pddl/elevator/domain_split_service.pddl"
    p = "pddl/elevator/split_service.pddl"
    require_finished(d, p)
    domain, problem, actions = load(d, p)

    assert domain.name == "elevator-split-service"
    assert_action_names(domain, {"move", "board", "leave"})
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
    assert not problem.goal_neg

    assert_ground_action(
        actions,
        "move",
        pos_pre={("lift-at", "even", "f0"), ("link", "even", "f0", "f2")},
        add_eff={("lift-at", "even", "f2")},
        del_eff={("lift-at", "even", "f0")},
    )
    assert_ground_action(
        actions,
        "board",
        pos_pre={("passenger-at", "p1", "f2"), ("lift-at", "even", "f2")},
        add_eff={("boarded", "p1", "even")},
        del_eff={("passenger-at", "p1", "f2")},
    )
    assert_ground_action(
        actions,
        "leave",
        pos_pre={("boarded", "p1", "even"), ("lift-at", "even", "f2")},
        add_eff={("passenger-at", "p1", "f2")},
        del_eff={("boarded", "p1", "even")},
    )

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
    assert not problem.goal_neg
    assert len(actions) == 18
    assert_solved(problem, actions)


def test_two_ferries_exact_instance_and_parallelize():
    d = "pddl/ferry/domain_two_ferries.pddl"
    p = "pddl/ferry/ferry_cross_traffic_two.pddl"
    require_finished(d, p)
    domain, problem, actions = load(d, p)

    assert domain.name == "ferry-two"
    assert_action_names(domain, {"board", "debark", "sail"})
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
    assert not problem.goal_neg

    assert_ground_action(
        actions,
        "board",
        pos_pre={
            ("car-at", "c1", "left-bank"),
            ("ferry-at", "ferry1", "left-bank"),
            ("empty", "ferry1"),
        },
        add_eff={("onboard", "c1", "ferry1")},
        del_eff={("car-at", "c1", "left-bank"), ("empty", "ferry1")},
    )
    assert_ground_action(
        actions,
        "debark",
        pos_pre={("onboard", "c1", "ferry1"), ("ferry-at", "ferry1", "left-bank")},
        add_eff={("car-at", "c1", "left-bank"), ("empty", "ferry1")},
        del_eff={("onboard", "c1", "ferry1")},
    )
    assert_ground_action(
        actions,
        "sail",
        pos_pre={("ferry-at", "ferry1", "left-bank"), ("route", "left-bank", "right-bank")},
        add_eff={("ferry-at", "ferry1", "right-bank")},
        del_eff={("ferry-at", "ferry1", "left-bank")},
    )

    assert len(actions) == 36
    _, gp = assert_solved(problem, actions)
    assert any(len(step) > 1 for step in gp.plan), "expected two-ferry parallelism"
