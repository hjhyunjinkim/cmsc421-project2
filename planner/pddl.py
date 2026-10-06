from __future__ import annotations

import itertools
import re
from pathlib import Path
from typing import Iterable

from .model import ActionSchema, Domain, Fact, GroundAction, Problem


def _tokenize(text: str) -> list[str]:
    """Tokenize the small STRIPS + typing subset used in this assignment."""
    text = re.sub(r";[^\n]*", "", text)
    return re.findall(r"\(|\)|[^\s()]+", text.lower())


def _parse_tokens(tokens: list[str]):
    stack: list[list] = []
    root = None
    for tok in tokens:
        if tok == "(":
            node: list = []
            if stack:
                stack[-1].append(node)
            stack.append(node)
        elif tok == ")":
            if not stack:
                raise ValueError("Unbalanced ')' in PDDL")
            node = stack.pop()
            if not stack:
                root = node
        else:
            if not stack:
                raise ValueError(f"Token outside list: {tok}")
            stack[-1].append(tok)
    if stack:
        raise ValueError("Unbalanced '(' in PDDL")
    return root


def parse_sexpr(text: str):
    return _parse_tokens(_tokenize(text))


def _typed_items(items: Iterable[str], default_type: str = "object") -> list[tuple[str, str]]:
    items = list(items)
    out: list[tuple[str, str]] = []
    pending: list[str] = []
    i = 0
    while i < len(items):
        tok = items[i]
        if tok == "-":
            if i + 1 >= len(items):
                raise ValueError("Dangling '-' in typed list")
            typ = items[i + 1]
            out.extend((x, typ) for x in pending)
            pending.clear()
            i += 2
        else:
            pending.append(tok)
            i += 1
    out.extend((x, default_type) for x in pending)
    return out


def _literal(expr) -> Fact:
    if not isinstance(expr, list) or not expr:
        raise ValueError(f"Expected literal, got {expr!r}")
    return tuple(str(x) for x in expr)


def _split_literals(expr) -> tuple[frozenset[Fact], frozenset[Fact]]:
    if expr is None:
        return frozenset(), frozenset()
    parts = expr[1:] if isinstance(expr, list) and expr and expr[0] == "and" else [expr]
    pos: set[Fact] = set()
    neg: set[Fact] = set()
    for part in parts:
        if isinstance(part, list) and part and part[0] == "not":
            if len(part) != 2:
                raise ValueError(f"Bad negated literal: {part}")
            neg.add(_literal(part[1]))
        else:
            pos.add(_literal(part))
    return frozenset(pos), frozenset(neg)


def _kw_value(form: list, key: str):
    try:
        i = form.index(key)
    except ValueError:
        return None
    return form[i + 1] if i + 1 < len(form) else None


def load_domain(path: str | Path) -> Domain:
    tree = parse_sexpr(Path(path).read_text())
    if not tree or tree[0] != "define":
        raise ValueError("Expected (define ...) domain")

    name = None
    actions: list[ActionSchema] = []
    for form in tree[1:]:
        if not isinstance(form, list) or not form:
            continue
        if form[0] == "domain":
            name = form[1]
        elif form[0] == ":action":
            aname = form[1]
            params_expr = _kw_value(form, ":parameters") or []
            params = tuple(_typed_items(params_expr))
            pos_pre, neg_pre = _split_literals(_kw_value(form, ":precondition"))
            add_eff, del_eff = _split_literals(_kw_value(form, ":effect"))
            actions.append(
                ActionSchema(
                    name=aname,
                    parameters=params,
                    pos_pre=pos_pre,
                    neg_pre=neg_pre,
                    add_eff=add_eff,
                    del_eff=del_eff,
                )
            )

    if name is None:
        raise ValueError("Domain name not found")
    return Domain(name=name, actions=tuple(actions))


def load_problem(path: str | Path) -> Problem:
    tree = parse_sexpr(Path(path).read_text())
    if not tree or tree[0] != "define":
        raise ValueError("Expected (define ...) problem")

    name = None
    domain_name = None
    objects: dict[str, str] = {}
    init: set[Fact] = set()
    goal_pos: frozenset[Fact] = frozenset()
    goal_neg: frozenset[Fact] = frozenset()

    for form in tree[1:]:
        if not isinstance(form, list) or not form:
            continue
        if form[0] == "problem":
            name = form[1]
        elif form[0] == ":domain":
            domain_name = form[1]
        elif form[0] == ":objects":
            objects.update(_typed_items(form[1:]))
        elif form[0] == ":init":
            for lit in form[1:]:
                if isinstance(lit, list) and lit and lit[0] == "not":
                    continue
                init.add(_literal(lit))
        elif form[0] == ":goal":
            goal_pos, goal_neg = _split_literals(form[1])

    if name is None or domain_name is None:
        raise ValueError("Problem/domain name missing")

    return Problem(
        name=name,
        domain_name=domain_name,
        objects=objects,
        init=frozenset(init),
        goal_pos=goal_pos,
        goal_neg=goal_neg,
    )


def _substitute_fact(fact: Fact, env: dict[str, str]) -> Fact:
    return tuple(env.get(token, token) for token in fact)


def ground(domain: Domain, problem: Problem) -> list[GroundAction]:
    """Ground all action schemas for the supplied problem.

    Predicates that never occur in an effect are static.  We prune grounded
    actions requiring static facts absent from the initial state.  This keeps
    the small educational domains compact without needing a sophisticated
    grounding engine.
    """
    if problem.domain_name != domain.name:
        raise ValueError(f"Problem uses domain {problem.domain_name}, loaded {domain.name}")

    all_objects = sorted(problem.objects)
    by_type: dict[str, list[str]] = {"object": list(all_objects)}
    for obj, typ in problem.objects.items():
        by_type.setdefault(typ, []).append(obj)
    for values in by_type.values():
        values.sort()

    dynamic_predicates = {
        fact[0]
        for schema in domain.actions
        for fact in (schema.add_eff | schema.del_eff)
    }

    grounded: list[GroundAction] = []
    for schema in domain.actions:
        choices: list[list[str]] = []
        for _, typ in schema.parameters:
            choices.append(by_type.get(typ, []))
        if any(not choice for choice in choices):
            continue

        assignments = itertools.product(*choices) if choices else [()]
        for args in assignments:
            env = {param: arg for (param, _), arg in zip(schema.parameters, args)}
            action = GroundAction(
                name=schema.name,
                args=tuple(args),
                pos_pre=frozenset(_substitute_fact(f, env) for f in schema.pos_pre),
                neg_pre=frozenset(_substitute_fact(f, env) for f in schema.neg_pre),
                add_eff=frozenset(_substitute_fact(f, env) for f in schema.add_eff),
                del_eff=frozenset(_substitute_fact(f, env) for f in schema.del_eff),
            )

            # Conventional Blocks World never needs (on x x).
            if any(
                len(f) == 3 and f[0] == "on" and f[1] == f[2]
                for f in (action.add_eff | action.pos_pre)
            ):
                continue

            impossible_static = any(
                f[0] not in dynamic_predicates and f not in problem.init
                for f in action.pos_pre
            )
            if impossible_static:
                continue

            grounded.append(action)

    grounded.sort(key=lambda a: (a.name, a.args))
    return grounded
