import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from visualize_plan import (
    InteractiveViewer,
    create_figure,
    draw_frame,
    goal_progress,
    solve_case,
)


@pytest.mark.parametrize("case_id", ["B0", "E0", "L0"])
def test_baseline_visualizations_render(case_id):
    problem, frames, _elapsed = solve_case(case_id, "graphplan")
    assert len(frames) >= 2
    assert frames[0].state == problem.init
    assert problem.is_goal(frames[-1].state)
    assert goal_progress(problem, frames[-1].state)[0] == len(problem.goal_pos)

    fig, ax = create_figure()
    draw_frame(ax, problem, frames, 0, "graphplan")
    draw_frame(ax, problem, frames, len(frames) - 1, "graphplan")
    fig.canvas.draw()
    plt.close(fig)


def test_bfs_frames_are_sequential_actions():
    problem, frames, _elapsed = solve_case("L0", "bfs")
    assert all(len(frame.actions) == 1 for frame in frames[1:])
    assert problem.is_goal(frames[-1].state)


def test_interactive_viewer_steps_manually():
    problem, frames, _elapsed = solve_case("L0", "graphplan")
    viewer = InteractiveViewer(problem, frames, "graphplan")
    assert viewer.index == 0

    viewer.next()
    assert viewer.index == 1
    viewer.previous()
    assert viewer.index == 0
    plt.close(viewer.fig)


def test_unknown_case_has_helpful_error():
    with pytest.raises(ValueError, match="unknown case"):
        solve_case("not-a-case", "graphplan")
