from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results/results.csv"


def read_rows() -> list[dict[str, str]]:
    if not RESULTS.exists():
        raise SystemExit("results/results.csv not found. Run python run_experiments.py first.")
    with RESULTS.open(newline="") as handle:
        return list(csv.DictReader(handle))


def plot_search_effort(rows: list[dict[str, str]]) -> None:
    bfs = [
        row
        for row in rows
        if row["planner"] == "forward-strips-bfs" and row["states_expanded"]
    ]
    if not bfs:
        return

    names = [row["case"] for row in bfs]
    values = [int(row["states_expanded"]) for row in bfs]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(names, values)
    ax.set_ylabel("States expanded")
    ax.set_title("Forward STRIPS search effort")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(ROOT / "results/search_effort.png", dpi=180)
    plt.close(fig)


def plot_plan_structure(rows: list[dict[str, str]]) -> None:
    graphplan = [
        row
        for row in rows
        if row["planner"] == "graphplan" and row["success"] == "True"
    ]
    if not graphplan:
        return

    names = [row["case"] for row in graphplan]
    actions = [int(row["plan_actions"]) for row in graphplan]
    makespan = [int(row["makespan"]) for row in graphplan]
    x = list(range(len(names)))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([v - width / 2 for v in x], actions, width=width, label="Plan actions")
    ax.bar([v + width / 2 for v in x], makespan, width=width, label="Parallel makespan")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=35, ha="right")
    ax.set_ylabel("Count")
    ax.set_title("GraphPlan plan actions vs. parallel makespan")
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT / "results/plan_structure.png", dpi=180)
    plt.close(fig)


def main() -> None:
    rows = read_rows()
    plot_search_effort(rows)
    plot_plan_structure(rows)
    print("Wrote results/search_effort.png")
    print("Wrote results/plan_structure.png")


if __name__ == "__main__":
    main()
