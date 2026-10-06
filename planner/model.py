from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Tuple

Fact = Tuple[str, ...]
State = FrozenSet[Fact]


def fact_str(fact: Fact) -> str:
    return "(" + " ".join(fact) + ")"


@dataclass(frozen=True)
class ActionSchema:
    name: str
    parameters: tuple[tuple[str, str], ...]
    pos_pre: frozenset[Fact]
    neg_pre: frozenset[Fact]
    add_eff: frozenset[Fact]
    del_eff: frozenset[Fact]


@dataclass(frozen=True)
class GroundAction:
    name: str
    args: tuple[str, ...]
    pos_pre: frozenset[Fact]
    neg_pre: frozenset[Fact]
    add_eff: frozenset[Fact]
    del_eff: frozenset[Fact]
    noop: bool = False

    @property
    def label(self) -> str:
        if self.noop:
            return f"noop {fact_str(self.args)}"
        return "(" + " ".join((self.name, *self.args)) + ")"

    def applicable(self, state: State) -> bool:
        return self.pos_pre.issubset(state) and self.neg_pre.isdisjoint(state)

    def apply(self, state: State) -> State:
        return frozenset((state - self.del_eff) | self.add_eff)


@dataclass(frozen=True)
class Domain:
    name: str
    actions: tuple[ActionSchema, ...]


@dataclass(frozen=True)
class Problem:
    name: str
    domain_name: str
    objects: dict[str, str]
    init: State
    goal_pos: frozenset[Fact]
    goal_neg: frozenset[Fact]

    def is_goal(self, state: State) -> bool:
        return self.goal_pos.issubset(state) and self.goal_neg.isdisjoint(state)
