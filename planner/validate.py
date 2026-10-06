from __future__ import annotations

from .graphplan import actions_mutex
from .model import GroundAction, Problem, State


def validate_sequential(problem: Problem, plan: list[GroundAction]) -> tuple[bool, str]:
    state: State = problem.init
    for index, action in enumerate(plan):
        if not action.applicable(state):
            return False, f"action {index} is not applicable: {action.label}"
        state = action.apply(state)
    if not problem.is_goal(state):
        return False, "final state does not satisfy the goal"
    return True, "ok"


def validate_parallel(problem: Problem, plan: list[list[GroundAction]]) -> tuple[bool, str]:
    state: State = problem.init

    for t, step in enumerate(plan):
        for action in step:
            if not action.applicable(state):
                return False, f"t={t}: action not applicable: {action.label}"

        for i, first in enumerate(step):
            for second in step[i + 1 :]:
                if actions_mutex(first, second):
                    return False, (
                        f"t={t}: concurrent actions interfere: "
                        f"{first.label} and {second.label}"
                    )

        deletes = frozenset().union(*(a.del_eff for a in step)) if step else frozenset()
        adds = frozenset().union(*(a.add_eff for a in step)) if step else frozenset()
        state = frozenset((state - deletes) | adds)

    if not problem.is_goal(state):
        return False, "final state does not satisfy the goal"
    return True, "ok"
