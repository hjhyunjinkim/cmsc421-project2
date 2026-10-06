from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from time import perf_counter
from typing import Iterable

from .model import Fact, GroundAction, Problem


@dataclass
class GraphPlanResult:
    success: bool
    plan: list[list[GroundAction]]
    elapsed_s: float
    levels: int
    fact_nodes: int
    action_nodes: int
    action_mutexes: int
    fact_mutexes: int
    extraction_calls: int
    reason: str = ""


def _noop(fact: Fact) -> GroundAction:
    return GroundAction(
        name="__noop__",
        args=fact,
        pos_pre=frozenset({fact}),
        neg_pre=frozenset(),
        add_eff=frozenset({fact}),
        del_eff=frozenset(),
        noop=True,
    )


def _pair(a, b):
    return frozenset((a, b))


def actions_mutex(
    a: GroundAction,
    b: GroundAction,
    prev_fact_mutex: set[frozenset[Fact]] | None = None,
) -> bool:
    """GraphPlan-style action mutex test for the supported STRIPS subset."""
    prev_fact_mutex = prev_fact_mutex or set()
    if a == b:
        return False

    # Inconsistent effects.
    if (a.add_eff & b.del_eff) or (b.add_eff & a.del_eff):
        return True

    # Interference with positive/negative preconditions.
    if (a.del_eff & b.pos_pre) or (b.del_eff & a.pos_pre):
        return True
    if (a.add_eff & b.neg_pre) or (b.add_eff & a.neg_pre):
        return True
    if (a.pos_pre & b.neg_pre) or (b.pos_pre & a.neg_pre):
        return True

    # Competing needs.
    for p in a.pos_pre:
        for q in b.pos_pre:
            if _pair(p, q) in prev_fact_mutex:
                return True
    return False


def _goals_nonmutex(
    goals: frozenset[Fact],
    fact_mutex: set[frozenset[Fact]],
) -> bool:
    return all(_pair(a, b) not in fact_mutex for a, b in combinations(goals, 2))


def solve_graphplan(
    problem: Problem,
    grounded_actions: Iterable[GroundAction],
    max_levels: int = 30,
) -> GraphPlanResult:
    """Small educational GraphPlan implementation.

    The assignment domains use positive action preconditions. Negative goals are
    intentionally unsupported to keep the implementation compact.
    """
    real_actions = tuple(grounded_actions)
    t0 = perf_counter()

    if any(a.neg_pre for a in real_actions):
        return GraphPlanResult(
            False, [], perf_counter() - t0, 0, 0, 0, 0, 0, 0,
            "negative-action-preconditions-not-supported",
        )
    if problem.goal_neg:
        return GraphPlanResult(
            False, [], perf_counter() - t0, 0, 0, 0, 0, 0, 0,
            "negative-goals-not-supported",
        )

    fact_layers: list[frozenset[Fact]] = [problem.init]
    fact_mutex_layers: list[set[frozenset[Fact]]] = [set()]
    action_layers: list[tuple[GroundAction, ...]] = []
    action_mutex_layers: list[set[frozenset[GroundAction]]] = []
    achievers_layers: list[dict[Fact, tuple[GroundAction, ...]]] = []
    failed: set[tuple[int, frozenset[Fact]]] = set()
    extraction_calls = 0

    def extract(level: int, goals: frozenset[Fact]):
        nonlocal extraction_calls
        extraction_calls += 1
        key = (level, goals)
        if key in failed:
            return None
        if level == 0:
            return [] if goals.issubset(fact_layers[0]) else None
        if not goals.issubset(fact_layers[level]):
            failed.add(key)
            return None
        if not _goals_nonmutex(goals, fact_mutex_layers[level]):
            failed.add(key)
            return None

        amutex = action_mutex_layers[level - 1]
        achievers = achievers_layers[level - 1]

        def choose(remaining: frozenset[Fact], chosen: tuple[GroundAction, ...]):
            if not remaining:
                subgoals = (
                    frozenset().union(*(a.pos_pre for a in chosen))
                    if chosen
                    else frozenset()
                )
                prefix = extract(level - 1, subgoals)
                if prefix is not None:
                    real = [a for a in chosen if not a.noop]
                    return prefix + [real]
                return None

            goal = min(remaining, key=lambda g: len(achievers.get(g, ())))
            for action in achievers.get(goal, ()):
                if any(_pair(action, other) in amutex for other in chosen if action != other):
                    continue
                covered = frozenset().union(
                    *(a.add_eff for a in (*chosen, action))
                )
                new_remaining = remaining - covered
                new_chosen = chosen if action in chosen else (*chosen, action)
                answer = choose(new_remaining, new_chosen)
                if answer is not None:
                    return answer
            return None

        answer = choose(goals, ())
        if answer is None:
            failed.add(key)
        return answer

    for _ in range(max_levels):
        level = len(fact_layers) - 1
        goals = problem.goal_pos

        if goals.issubset(fact_layers[level]) and _goals_nonmutex(
            goals, fact_mutex_layers[level]
        ):
            plan = extract(level, goals)
            if plan is not None:
                return GraphPlanResult(
                    True,
                    plan,
                    perf_counter() - t0,
                    level,
                    sum(len(layer) for layer in fact_layers),
                    sum(len(layer) for layer in action_layers),
                    sum(len(layer) for layer in action_mutex_layers),
                    sum(len(layer) for layer in fact_mutex_layers),
                    extraction_calls,
                )

        facts = fact_layers[-1]
        prev_fmutex = fact_mutex_layers[-1]

        applicable: list[GroundAction] = []
        for action in real_actions:
            if action.pos_pre.issubset(facts) and _goals_nonmutex(
                action.pos_pre, prev_fmutex
            ):
                applicable.append(action)
        applicable.extend(_noop(f) for f in facts)
        applicable_t = tuple(applicable)

        amutex: set[frozenset[GroundAction]] = set()
        for a, b in combinations(applicable_t, 2):
            if actions_mutex(a, b, prev_fmutex):
                amutex.add(_pair(a, b))

        next_facts = (
            frozenset().union(*(a.add_eff for a in applicable_t))
            if applicable_t
            else frozenset()
        )

        achievers: dict[Fact, list[GroundAction]] = {f: [] for f in next_facts}
        for action in applicable_t:
            for fact in action.add_eff:
                achievers[fact].append(action)
        achievers_t = {fact: tuple(items) for fact, items in achievers.items()}

        fmutex: set[frozenset[Fact]] = set()
        for f, g in combinations(next_facts, 2):
            all_mutex = True
            for a in achievers_t[f]:
                for b in achievers_t[g]:
                    if a == b or _pair(a, b) not in amutex:
                        all_mutex = False
                        break
                if not all_mutex:
                    break
            if all_mutex:
                fmutex.add(_pair(f, g))

        action_layers.append(applicable_t)
        action_mutex_layers.append(amutex)
        achievers_layers.append(achievers_t)
        fact_layers.append(next_facts)
        fact_mutex_layers.append(fmutex)

    level = len(fact_layers) - 1
    return GraphPlanResult(
        False,
        [],
        perf_counter() - t0,
        level,
        sum(len(layer) for layer in fact_layers),
        sum(len(layer) for layer in action_layers),
        sum(len(layer) for layer in action_mutex_layers),
        sum(len(layer) for layer in fact_mutex_layers),
        extraction_calls,
        "max-levels",
    )
