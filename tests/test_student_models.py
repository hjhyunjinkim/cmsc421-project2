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


LOGISTICS_DOMAIN = "pddl/logistics/domain.pddl"
LOGISTICS_OBJECTS = {
    "r1": "robot",
    "c1": "container", "c2": "container", "c3": "container",
    "d1": "location", "d2": "location", "d3": "location",
}
LOGISTICS_INIT = frozenset({
    ("onboard", "c1", "r1"),
    ("container-at", "c2", "d1"),
    ("container-at", "c3", "d2"),
    ("robot-at", "r1", "d1"),
    ("connected", "d1", "d2"), ("connected", "d2", "d1"),
    ("connected", "d1", "d3"), ("connected", "d3", "d1"),
    ("connected", "d2", "d3"), ("connected", "d3", "d2"),
})


def assert_logistics_domain_and_instance(problem_rel: str, goal: set[tuple[str, ...]]):
    require_finished(problem_rel)
    domain, problem, actions = load(LOGISTICS_DOMAIN, problem_rel)
    assert domain.name == "logistics"
    assert_action_names(domain, {"pickup", "putdown", "move"})
    assert problem.objects == LOGISTICS_OBJECTS
    assert problem.init == LOGISTICS_INIT
    assert problem.goal_pos == frozenset(goal)
    assert not problem.goal_neg
    assert len(actions) == 24

    # Capacity-one is represented positively with (empty r1), which keeps the
    # supplied GraphPlan within its positive-precondition STRIPS subset.
    assert_ground_action(
        actions,
        "pickup",
        pos_pre={
            ("robot-at", "r1", "d1"),
            ("container-at", "c2", "d1"),
            ("empty", "r1"),
        },
        add_eff={("onboard", "c2", "r1")},
        del_eff={("container-at", "c2", "d1"), ("empty", "r1")},
    )
    assert_ground_action(
        actions,
        "putdown",
        pos_pre={("robot-at", "r1", "d1"), ("onboard", "c1", "r1")},
        add_eff={("container-at", "c1", "d1"), ("empty", "r1")},
        del_eff={("onboard", "c1", "r1")},
    )
    assert_ground_action(
        actions,
        "move",
        pos_pre={("robot-at", "r1", "d1"), ("connected", "d1", "d3")},
        add_eff={("robot-at", "r1", "d3")},
        del_eff={("robot-at", "r1", "d1")},
    )
    return problem, actions, assert_solved(problem, actions)


def test_logistics_l1_c1_d1_robot_d2():
    assert_logistics_domain_and_instance(
        "pddl/logistics/goal_c1_d1_robot_d2.pddl",
        {("container-at", "c1", "d1"), ("robot-at", "r1", "d2")},
    )


def test_logistics_l2_nested_goal():
    problem, actions, (bfs_result, gp_result) = assert_logistics_domain_and_instance(
        "pddl/logistics/goal_c1_d1_c3_onboard_robot_d2.pddl",
        {
            ("container-at", "c1", "d1"),
            ("robot-at", "r1", "d2"),
            ("onboard", "c3", "r1"),
        },
    )
    assert len(bfs_result.plan) == 3
    assert len(gp_result.plan) == 3


def test_logistics_l3_two_deliveries():
    problem, actions, (bfs_result, gp_result) = assert_logistics_domain_and_instance(
        "pddl/logistics/goal_c1_d2_c3_d3.pddl",
        {("container-at", "c1", "d2"), ("container-at", "c3", "d3")},
    )
    assert len(bfs_result.plan) == 5
    assert len(gp_result.plan) == 5


def test_logistics_l4_all_to_d3():
    problem, actions, (bfs_result, gp_result) = assert_logistics_domain_and_instance(
        "pddl/logistics/goal_all_d3.pddl",
        {
            ("container-at", "c1", "d3"),
            ("container-at", "c2", "d3"),
            ("container-at", "c3", "d3"),
        },
    )
    assert len(bfs_result.plan) == 10
    assert len(gp_result.plan) == 10
    # This is the historically pathological goal set. The repaired planner must
    # solve it; students analyze the observed extraction effort in the report.
