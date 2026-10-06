from pathlib import Path

from .graphplan import solve_graphplan
from .pddl import ground, load_domain, load_problem
from .search import bfs


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    domain = load_domain(root / "pddl/blocksworld/domain.pddl")
    problem = load_problem(root / "pddl/blocksworld/baseline3.pddl")
    actions = ground(domain, problem)
    print(f"Loaded {problem.name} with {len(actions)} grounded actions")
    print("BFS:", [a.label for a in bfs(problem, actions).plan])
    gp = solve_graphplan(problem, actions)
    print("GraphPlan:")
    for t, step in enumerate(gp.plan):
        print(f"  t{t}: " + " | ".join(a.label for a in step))


if __name__ == "__main__":
    main()
