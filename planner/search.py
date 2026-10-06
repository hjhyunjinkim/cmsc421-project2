from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from time import perf_counter
from typing import Iterable

from .model import GroundAction, Problem, State


@dataclass
class SearchResult:
    success: bool
    plan: list[GroundAction]
    elapsed_s: float
    expanded: int
    generated: int
    max_frontier: int
    visited: int
    reason: str = ""


def bfs(
    problem: Problem,
    actions: Iterable[GroundAction],
    max_nodes: int = 250_000,
) -> SearchResult:
    """Breadth-first forward state-space search over grounded STRIPS actions."""
    actions = tuple(actions)
    start = problem.init
    t0 = perf_counter()

    if problem.is_goal(start):
        return SearchResult(True, [], perf_counter() - t0, 0, 1, 1, 1)

    queue = deque([start])
    parent: dict[State, tuple[State | None, GroundAction | None]] = {
        start: (None, None)
    }
    expanded = 0
    generated = 1
    max_frontier = 1

    while queue:
        state = queue.popleft()
        expanded += 1
        if expanded > max_nodes:
            return SearchResult(
                False,
                [],
                perf_counter() - t0,
                expanded,
                generated,
                max_frontier,
                len(parent),
                "node-limit",
            )

        for action in actions:
            if not action.applicable(state):
                continue
            nxt = action.apply(state)
            if nxt in parent:
                continue

            parent[nxt] = (state, action)
            generated += 1

            if problem.is_goal(nxt):
                plan: list[GroundAction] = []
                cur = nxt
                while parent[cur][0] is not None:
                    prev, act = parent[cur]
                    assert prev is not None and act is not None
                    plan.append(act)
                    cur = prev
                plan.reverse()
                return SearchResult(
                    True,
                    plan,
                    perf_counter() - t0,
                    expanded,
                    generated,
                    max(max_frontier, len(queue) + 1),
                    len(parent),
                )

            queue.append(nxt)

        max_frontier = max(max_frontier, len(queue))

    return SearchResult(
        False,
        [],
        perf_counter() - t0,
        expanded,
        generated,
        max_frontier,
        len(parent),
        "exhausted",
    )


def reachable_states(
    init: State,
    actions: Iterable[GroundAction],
    cap: int = 250_000,
) -> tuple[int, bool, float]:
    """Enumerate the reachable state space up to cap.

    Returns (number_seen, exact, elapsed_seconds).  exact=False means the cap
    was reached and the actual reachable state space may be larger.
    """
    actions = tuple(actions)
    t0 = perf_counter()
    queue = deque([init])
    seen = {init}

    while queue:
        state = queue.popleft()
        for action in actions:
            if not action.applicable(state):
                continue
            nxt = action.apply(state)
            if nxt in seen:
                continue
            seen.add(nxt)
            if len(seen) >= cap:
                return len(seen), False, perf_counter() - t0
            queue.append(nxt)

    return len(seen), True, perf_counter() - t0
