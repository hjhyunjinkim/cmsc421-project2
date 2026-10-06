"""Keep the default test report focused on student-authored PDDL cases."""

from __future__ import annotations

from collections import OrderedDict


PDDL_CHECKS = OrderedDict(
    [
        ("test_blocks_baseline_solved_by_both_planners", "B0"),
        ("test_sussman3_exact_instance_and_solvable", "B1"),
        ("test_sussman6_exact_instance_and_solvable", "B2"),
        ("test_two_gripper_domain_and_problem_are_exact_and_parallelize", "B3"),
        ("test_elevator_baseline_solved_by_both_planners", "E0"),
        ("test_split_service_elevator_exact_links_transfer_and_solvable", "E1"),
        ("test_logistics_baseline_solved_by_both_planners", "L0"),
        ("test_logistics_l1_c1_d1_robot_d2", "L1"),
        ("test_logistics_l2_nested_goal", "L2"),
        ("test_logistics_l3_two_deliveries", "L3"),
        ("test_logistics_l4_all_to_d3", "L4"),
    ]
)

_results = {test_name: "NOT RUN" for test_name in PDDL_CHECKS}


def _test_name(nodeid: str) -> str:
    return nodeid.rsplit("::", 1)[-1].split("[", 1)[0]


def pytest_runtest_logreport(report) -> None:
    """Record the outcome of each public student-model check."""

    test_name = _test_name(report.nodeid)
    if test_name not in PDDL_CHECKS:
        return
    if report.failed:
        _results[test_name] = "FAIL"
    elif report.skipped:
        _results[test_name] = "INCOMPLETE"
    elif report.when == "call" and report.passed:
        _results[test_name] = "PASS"


def pytest_report_teststatus(report):
    """Suppress per-test progress symbols while preserving pytest statistics."""

    if report.when == "call" or report.failed or report.skipped:
        return report.outcome, "", ""
    return None


def pytest_terminal_summary(terminalreporter) -> None:
    """Print one concise status line for every experiment configuration."""

    terminalreporter.write_sep("=", "PDDL checks")
    for test_name, experiment_id in PDDL_CHECKS.items():
        status = _results[test_name]
        terminalreporter.write_line(f"{experiment_id:<3} {status}")
