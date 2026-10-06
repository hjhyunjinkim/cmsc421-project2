"""Visualize solved plans without changing the project planners.

The visualizer loads the same cases as ``run_experiments.py``, solves one case,
and renders the resulting state sequence with a small domain-specific scene.
It supports the Blocks World, Elevator, and Logistics domains used by this
assignment.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle
from matplotlib.widgets import Button

from planner import bfs, ground, load_domain, load_problem, solve_graphplan
from planner.model import GroundAction, Problem, State
from run_experiments import CASES, TODO_MARKER

ROOT = Path(__file__).resolve().parent

COLORS = (
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#E45756",
    "#72B7B2",
    "#B279A2",
    "#FF9DA6",
    "#9D755D",
    "#BAB0AC",
)
GOAL_COLOR = "#159447"
INK = "#24323D"
MUTED = "#6B7780"
SURFACE = "#F7F9FB"


@dataclass(frozen=True)
class PlanFrame:
    """One world state and the action(s) that produced it."""

    state: State
    actions: tuple[str, ...]


def natural_key(value: str) -> tuple[object, ...]:
    """Sort names such as f2 before f10."""

    return tuple(
        int(part) if part.isdigit() else part
        for part in re.split(r"(\d+)", value)
    )


def objects_of_type(problem: Problem, object_type: str) -> list[str]:
    return sorted(
        (name for name, kind in problem.objects.items() if kind == object_type),
        key=natural_key,
    )


def object_colors(names: Iterable[str]) -> dict[str, str]:
    return {
        name: COLORS[index % len(COLORS)]
        for index, name in enumerate(sorted(names, key=natural_key))
    }


def goal_progress(problem: Problem, state: State) -> tuple[int, int]:
    positive = sum(fact in state for fact in problem.goal_pos)
    negative = sum(fact not in state for fact in problem.goal_neg)
    return positive + negative, len(problem.goal_pos) + len(problem.goal_neg)


def build_frames(
    problem: Problem,
    steps: Sequence[Sequence[GroundAction]],
) -> list[PlanFrame]:
    """Apply sequential or parallel plan steps and retain every resulting state."""

    state = problem.init
    frames = [PlanFrame(state=state, actions=())]
    for step_number, step in enumerate(steps, start=1):
        step = tuple(step)
        for action in step:
            if not action.applicable(state):
                raise ValueError(
                    f"action {action.label} is not applicable before step {step_number}"
                )
        deletes = (
            frozenset().union(*(action.del_eff for action in step))
            if step
            else frozenset()
        )
        adds = (
            frozenset().union(*(action.add_eff for action in step))
            if step
            else frozenset()
        )
        state = frozenset((state - deletes) | adds)
        frames.append(
            PlanFrame(
                state=state,
                actions=tuple(action.label for action in step),
            )
        )
    return frames


def solve_case(
    case_id: str,
    planner_name: str,
    *,
    node_limit: int = 250_000,
    max_levels: int = 30,
) -> tuple[Problem, list[PlanFrame], float]:
    """Solve a configured assignment case and return visualization-ready frames."""

    case_id = case_id.upper()
    case = next((item for item in CASES if item.experiment_id == case_id), None)
    if case is None:
        choices = ", ".join(item.experiment_id for item in CASES)
        raise ValueError(f"unknown case {case_id!r}; choose one of: {choices}")

    domain_path = ROOT / case.domain
    problem_path = ROOT / case.problem
    unfinished = [
        path.relative_to(ROOT)
        for path in (domain_path, problem_path)
        if TODO_MARKER in path.read_text()
    ]
    if unfinished:
        names = ", ".join(str(path) for path in unfinished)
        raise ValueError(f"{case_id} is unfinished: {names}")

    domain = load_domain(domain_path)
    problem = load_problem(problem_path)
    actions = ground(domain, problem)

    if planner_name == "bfs":
        result = bfs(problem, actions, max_nodes=node_limit)
        steps = [(action,) for action in result.plan]
    elif planner_name == "graphplan":
        result = solve_graphplan(problem, actions, max_levels=max_levels)
        steps = result.plan
    else:
        raise ValueError(f"unknown planner {planner_name!r}")

    if not result.success:
        raise RuntimeError(f"{planner_name} could not solve {case_id}: {result.reason}")
    return problem, build_frames(problem, steps), result.elapsed_s


def _draw_blocksworld(ax, problem: Problem, state: State) -> None:
    blocks = objects_of_type(problem, "block")
    colors = object_colors(blocks)
    held: dict[str, str] = {}
    for fact in state:
        if fact[0] != "holding":
            continue
        if len(fact) == 2:
            held["hand"] = fact[1]
        elif len(fact) == 3:
            held[fact[1]] = fact[2]

    above = {fact[2]: fact[1] for fact in state if fact[0] == "on"}
    roots = sorted(
        (fact[1] for fact in state if fact[0] == "ontable"),
        key=natural_key,
    )
    towers: list[list[str]] = []
    placed: set[str] = set()
    for root in roots:
        tower = [root]
        while tower[-1] in above and above[tower[-1]] not in tower:
            tower.append(above[tower[-1]])
        towers.append(tower)
        placed.update(tower)

    # Keep malformed or intermediate unattached blocks visible instead of
    # silently dropping them from the scene.
    for block in blocks:
        if block not in placed and block not in held.values():
            towers.append([block])

    grippers = objects_of_type(problem, "gripper") or ["hand"]
    column_count = max(len(towers), len(grippers), 1)
    block_width = 0.9
    block_height = 0.62
    max_height = max((len(tower) for tower in towers), default=1)
    ax.set_xlim(-0.8, column_count + 0.8)
    ax.set_ylim(-0.35, max(max_height + 2.0, 4.1))
    ax.axhline(0, color=INK, linewidth=3)
    ax.text(-0.65, -0.18, "TABLE", color=MUTED, fontsize=9, va="top")

    satisfied_goal_blocks = {
        fact[1]
        for fact in problem.goal_pos
        if fact and fact[0] == "on" and fact in state
    }
    for column, tower in enumerate(towers, start=1):
        x = column - block_width / 2
        for level, block in enumerate(tower):
            y = 0.05 + level * (block_height + 0.05)
            goal_met = block in satisfied_goal_blocks
            patch = FancyBboxPatch(
                (x, y),
                block_width,
                block_height,
                boxstyle="round,pad=0.02,rounding_size=0.06",
                facecolor=colors[block],
                edgecolor=GOAL_COLOR if goal_met else INK,
                linewidth=3 if goal_met else 1.5,
            )
            ax.add_patch(patch)
            ax.text(
                column,
                y + block_height / 2,
                block.upper(),
                ha="center",
                va="center",
                color="white",
                weight="bold",
                fontsize=13,
            )

    gripper_xs = [
        0.7 + index * max(1.1, (column_count - 0.4) / max(len(grippers), 1))
        for index in range(len(grippers))
    ]
    hand_y = max(max_height + 0.85, 2.65)
    for gripper, x in zip(grippers, gripper_xs):
        is_free = ("free", gripper) in state or (
            gripper == "hand" and ("handempty",) in state
        )
        ax.plot(
            [x - 0.28, x - 0.28, x + 0.28, x + 0.28],
            [hand_y, hand_y - 0.25, hand_y - 0.25, hand_y],
            color=INK,
            linewidth=3,
        )
        ax.text(
            x,
            hand_y + 0.12,
            gripper,
            ha="center",
            va="bottom",
            fontsize=9,
            color=MUTED,
        )
        block = held.get(gripper)
        if block:
            y = hand_y - 0.93
            patch = FancyBboxPatch(
                (x - block_width / 2, y),
                block_width,
                block_height,
                boxstyle="round,pad=0.02,rounding_size=0.06",
                facecolor=colors[block],
                edgecolor=INK,
                linewidth=1.5,
            )
            ax.add_patch(patch)
            ax.text(
                x,
                y + block_height / 2,
                block.upper(),
                ha="center",
                va="center",
                color="white",
                weight="bold",
                fontsize=13,
            )
        elif is_free:
            ax.text(x, hand_y - 0.48, "free", ha="center", color=GOAL_COLOR, fontsize=9)


def _draw_elevator(ax, problem: Problem, state: State) -> None:
    floors = objects_of_type(problem, "floor")
    elevators = objects_of_type(problem, "elevator")
    passengers = objects_of_type(problem, "passenger")
    elevator_colors = object_colors(elevators)
    passenger_colors = object_colors(passengers)
    floor_y = {floor: index for index, floor in enumerate(floors)}
    elevator_x = {name: index + 1.0 for index, name in enumerate(elevators)}

    ax.set_xlim(0.0, max(len(elevators) + 2.2, 3.8))
    ax.set_ylim(-0.7, max(len(floors) - 0.25, 1.5))
    for floor, y in floor_y.items():
        ax.hlines(y, 0.45, len(elevators) + 1.05, color="#CAD2D9", linewidth=1.3)
        ax.text(0.32, y, floor.upper(), ha="right", va="center", color=MUTED, weight="bold")

    # Split-service link predicates make each car's reachable floors visible.
    for elevator in elevators:
        x = elevator_x[elevator]
        links = {
            tuple(sorted((floor_y[fact[2]], floor_y[fact[3]])))
            for fact in state
            if fact[0] == "link" and fact[1] == elevator
        }
        for low, high in links:
            ax.plot(
                [x, x],
                [low, high],
                color=elevator_colors[elevator],
                alpha=0.2,
                linewidth=6,
                solid_capstyle="round",
            )

    lift_positions = {
        fact[1]: fact[2] for fact in state if fact[0] == "lift-at"
    }
    boarded = {
        fact[1]: fact[2] for fact in state if fact[0] == "boarded"
    }
    passenger_positions: dict[str, str] = {
        fact[1]: fact[2] for fact in state if fact[0] == "passenger-at"
    }
    passenger_goals = {
        fact[1]: fact[2]
        for fact in problem.goal_pos
        if fact and fact[0] == "passenger-at"
    }

    for elevator in elevators:
        x = elevator_x[elevator]
        floor = lift_positions.get(elevator)
        ax.text(
            x,
            len(floors) - 0.45,
            elevator,
            ha="center",
            va="bottom",
            color=elevator_colors[elevator],
            weight="bold",
        )
        if floor not in floor_y:
            continue
        y = floor_y[floor]
        car = FancyBboxPatch(
            (x - 0.34, y - 0.28),
            0.68,
            0.56,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor=elevator_colors[elevator],
            edgecolor=INK,
            linewidth=1.4,
            zorder=3,
        )
        ax.add_patch(car)
        riders = sorted((p for p, e in boarded.items() if e == elevator), key=natural_key)
        for index, passenger in enumerate(riders):
            px = x + (index - (len(riders) - 1) / 2) * 0.22
            ax.add_patch(
                Circle(
                    (px, y),
                    0.105,
                    facecolor=passenger_colors[passenger],
                    edgecolor="white",
                    linewidth=1.2,
                    zorder=4,
                )
            )
            ax.text(
                px,
                y,
                passenger.removeprefix("p"),
                ha="center",
                va="center",
                color="white",
                fontsize=7,
                weight="bold",
                zorder=5,
            )

    waiting_by_floor: dict[str, list[str]] = {floor: [] for floor in floors}
    for passenger, floor in passenger_positions.items():
        if floor in waiting_by_floor:
            waiting_by_floor[floor].append(passenger)
    waiting_x = len(elevators) + 1.45
    for floor, waiting in waiting_by_floor.items():
        y = floor_y[floor]
        for index, passenger in enumerate(sorted(waiting, key=natural_key)):
            x = waiting_x + index * 0.38
            goal_met = passenger_goals.get(passenger) == floor
            ax.add_patch(
                Circle(
                    (x, y),
                    0.16,
                    facecolor=passenger_colors[passenger],
                    edgecolor=GOAL_COLOR if goal_met else INK,
                    linewidth=3 if goal_met else 1.2,
                    zorder=4,
                )
            )
            ax.text(
                x,
                y,
                passenger.removeprefix("p"),
                ha="center",
                va="center",
                color="white",
                fontsize=8,
                weight="bold",
                zorder=5,
            )


def _draw_logistics(ax, problem: Problem, state: State) -> None:
    locations = objects_of_type(problem, "location")
    robots = objects_of_type(problem, "robot")
    containers = objects_of_type(problem, "container")
    robot_colors = object_colors(robots)
    container_colors = object_colors(containers)

    # A compact triangular layout for three depots, and a circle for any other
    # number of locations.
    if len(locations) == 3:
        positions = {
            locations[0]: (0.0, 1.8),
            locations[1]: (-2.25, -1.1),
            locations[2]: (2.25, -1.1),
        }
    else:
        import math

        positions = {
            location: (
                2.5
                * math.cos(
                    math.pi / 2
                    + 2 * math.pi * index / max(len(locations), 1)
                ),
                2.1
                * math.sin(
                    math.pi / 2
                    + 2 * math.pi * index / max(len(locations), 1)
                ),
            )
            for index, location in enumerate(locations)
        }

    connections = {
        frozenset((fact[1], fact[2]))
        for fact in state
        if fact[0] == "connected" and fact[1] in positions and fact[2] in positions
    }
    for connection in connections:
        if len(connection) != 2:
            continue
        start, end = tuple(connection)
        x1, y1 = positions[start]
        x2, y2 = positions[end]
        ax.plot([x1, x2], [y1, y2], color="#C8D0D7", linewidth=4, zorder=0)

    robot_positions = {
        fact[1]: fact[2] for fact in state if fact[0] == "robot-at"
    }
    container_positions = {
        fact[1]: fact[2] for fact in state if fact[0] == "container-at"
    }
    onboard = {fact[1]: fact[2] for fact in state if fact[0] == "onboard"}
    goal_container_at = {
        (fact[1], fact[2])
        for fact in problem.goal_pos
        if fact and fact[0] == "container-at"
    }
    goal_robot_at = {
        (fact[1], fact[2])
        for fact in problem.goal_pos
        if fact and fact[0] == "robot-at"
    }
    goal_onboard = {
        (fact[1], fact[2])
        for fact in problem.goal_pos
        if fact and fact[0] == "onboard"
    }

    for location, (x, y) in positions.items():
        ax.add_patch(
            Circle(
                (x, y),
                0.58,
                facecolor="#EDF1F4",
                edgecolor=INK,
                linewidth=2,
                zorder=1,
            )
        )
        ax.text(
            x,
            y + 0.08,
            location.upper(),
            ha="center",
            va="center",
            color=INK,
            fontsize=13,
            weight="bold",
            zorder=2,
        )

        local_containers = sorted(
            (
                container
                for container, place in container_positions.items()
                if place == location
            ),
            key=natural_key,
        )
        for index, container in enumerate(local_containers):
            cx = x + (index - (len(local_containers) - 1) / 2) * 0.42
            cy = y - 0.82
            goal_met = (container, location) in goal_container_at
            ax.add_patch(
                Rectangle(
                    (cx - 0.17, cy - 0.17),
                    0.34,
                    0.34,
                    facecolor=container_colors[container],
                    edgecolor=GOAL_COLOR if goal_met else INK,
                    linewidth=3 if goal_met else 1.2,
                    zorder=4,
                )
            )
            ax.text(
                cx,
                cy,
                container.removeprefix("c"),
                ha="center",
                va="center",
                color="white",
                fontsize=8,
                weight="bold",
                zorder=5,
            )

        local_robots = sorted(
            (
                robot
                for robot, place in robot_positions.items()
                if place == location
            ),
            key=natural_key,
        )
        for index, robot in enumerate(local_robots):
            rx = x + (index - (len(local_robots) - 1) / 2) * 0.72
            ry = y + 0.82
            goal_met = (robot, location) in goal_robot_at
            ax.add_patch(
                FancyBboxPatch(
                    (rx - 0.31, ry - 0.22),
                    0.62,
                    0.44,
                    boxstyle="round,pad=0.02,rounding_size=0.12",
                    facecolor=robot_colors[robot],
                    edgecolor=GOAL_COLOR if goal_met else INK,
                    linewidth=3 if goal_met else 1.2,
                    zorder=4,
                )
            )
            ax.text(
                rx,
                ry,
                robot.upper(),
                ha="center",
                va="center",
                color="white",
                fontsize=8,
                weight="bold",
                zorder=5,
            )
            cargo = sorted(
                (container for container, carrier in onboard.items() if carrier == robot),
                key=natural_key,
            )
            for cargo_index, container in enumerate(cargo):
                cx = rx + (cargo_index - (len(cargo) - 1) / 2) * 0.27
                cy = ry + 0.38
                cargo_goal_met = (container, robot) in goal_onboard
                ax.add_patch(
                    Rectangle(
                        (cx - 0.13, cy - 0.13),
                        0.26,
                        0.26,
                        facecolor=container_colors[container],
                        edgecolor=GOAL_COLOR if cargo_goal_met else INK,
                        linewidth=3 if cargo_goal_met else 1.0,
                        zorder=6,
                    )
                )
                ax.text(
                    cx,
                    cy,
                    container.removeprefix("c"),
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=7,
                    weight="bold",
                    zorder=7,
                )

    ax.set_xlim(-3.35, 3.35)
    ax.set_ylim(-2.25, 3.4)
    ax.set_aspect("equal", adjustable="box")


def draw_frame(
    ax,
    problem: Problem,
    frames: Sequence[PlanFrame],
    index: int,
    planner_name: str,
) -> None:
    """Draw one frame; exposed separately to keep rendering easy to test."""

    frame = frames[index]
    ax.clear()
    ax.set_facecolor(SURFACE)
    domain = problem.domain_name
    if domain.startswith("blocks"):
        _draw_blocksworld(ax, problem, frame.state)
    elif domain.startswith("elevator"):
        _draw_elevator(ax, problem, frame.state)
    elif domain == "logistics":
        _draw_logistics(ax, problem, frame.state)
    else:
        raise ValueError(f"no visual renderer for domain {domain!r}")

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    action_text = "Initial state" if not frame.actions else "  |  ".join(frame.actions)
    satisfied, total = goal_progress(problem, frame.state)
    ax.set_title(action_text, fontsize=12, color=INK, pad=12)
    ax.text(
        0.01,
        1.03,
        f"Step {index}/{len(frames) - 1}",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=10,
        color=MUTED,
    )
    ax.text(
        0.99,
        1.03,
        f"Goals {satisfied}/{total}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=10,
        color=GOAL_COLOR if satisfied == total else MUTED,
        weight="bold" if satisfied == total else "normal",
    )
    ax.figure.suptitle(
        f"{problem.name}  ·  {planner_name}",
        fontsize=15,
        weight="bold",
        color=INK,
        y=0.97,
    )


def create_figure():
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    fig.patch.set_facecolor("white")
    return fig, ax


class InteractiveViewer:
    """Manual previous/next controller for a Matplotlib window."""

    def __init__(
        self,
        problem: Problem,
        frames: Sequence[PlanFrame],
        planner_name: str,
    ) -> None:
        self.problem = problem
        self.frames = frames
        self.planner_name = planner_name
        self.index = 0
        self.fig, self.ax = create_figure()
        self.fig.subplots_adjust(bottom=0.16, top=0.86, left=0.05, right=0.95)

        previous_ax = self.fig.add_axes((0.365, 0.035, 0.12, 0.055))
        next_ax = self.fig.add_axes((0.515, 0.035, 0.12, 0.055))
        self.previous_button = Button(previous_ax, "Previous")
        self.next_button = Button(next_ax, "Next")
        self.previous_button.on_clicked(self.previous)
        self.next_button.on_clicked(self.next)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)

        self.render()

    def render(self) -> None:
        draw_frame(self.ax, self.problem, self.frames, self.index, self.planner_name)
        self.fig.canvas.draw_idle()

    def previous(self, _event=None) -> None:
        self.index = max(0, self.index - 1)
        self.render()

    def next(self, _event=None) -> None:
        self.index = min(len(self.frames) - 1, self.index + 1)
        self.render()

    def on_key(self, event) -> None:
        if event.key == "left":
            self.previous()
        elif event.key == "right":
            self.next()


def print_cases() -> None:
    print("CASE  STATUS       DESCRIPTION")
    for case in CASES:
        paths = (ROOT / case.domain, ROOT / case.problem)
        status = "unfinished" if any(TODO_MARKER in path.read_text() for path in paths) else "ready"
        print(f"{case.experiment_id:<5} {status:<12} {case.name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Visualize Blocks World, Elevator, and Logistics plans"
    )
    parser.add_argument("--case", help="experiment ID, for example B0, E0, or L0")
    parser.add_argument(
        "--planner",
        choices=("bfs", "graphplan"),
        default="graphplan",
        help="planner whose plan should be visualized (default: graphplan)",
    )
    parser.add_argument("--node-limit", type=int, default=250_000)
    parser.add_argument("--max-levels", type=int, default=30)
    parser.add_argument(
        "--list",
        action="store_true",
        help="list assignment cases and their completion status",
    )
    args = parser.parse_args()

    if args.list:
        print_cases()
        return
    if not args.case:
        parser.error("--case is required unless --list is used")
    try:
        problem, frames, elapsed = solve_case(
            args.case,
            args.planner,
            node_limit=args.node_limit,
            max_levels=args.max_levels,
        )
        print(
            f"Solved {args.case.upper()} with {args.planner}: "
            f"{len(frames) - 1} step(s) in {elapsed:.4f}s"
        )
        InteractiveViewer(problem, frames, args.planner)
        plt.show()
    except (RuntimeError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
