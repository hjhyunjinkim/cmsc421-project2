# CMSC 421 - Project 2
## Breaking and Extending Classical Planning Worlds

This repository is the **starter code** for Project 2.

The project is about **PDDL modeling and planning experiments**, not implementing planning algorithms. The repository already contains working implementations of:

- a small STRIPS-style PDDL parser and grounder;
- forward state-space search using breadth-first search (BFS);
- GraphPlan;
- sequential and parallel plan validation;
- an experiment runner; and
- plotting code for the required report figures.

Your job is to complete the prescribed PDDL changes, run the supplied planners, and analyze the resulting behavior in your **PDF report**.

> **START -> BREAK -> EXTEND -> COMPARE**

The assignment handout names the eleven experimental configurations as follows:

| ID | Configuration |
| --- | --- |
| B0 | Blocks World baseline, 3 blocks (provided) |
| B1 | Blocks World Sussman anomaly, 3 blocks |
| B2 | Blocks World scaled to 6 blocks |
| B3 | B1 with two independent grippers |
| E0 | Elevator baseline (provided) |
| E1 | Split-service even/odd elevators |
| L0 | Logistics: deliver carried `c1` to `d2` (provided) |
| L1 | Logistics: `c1` at `d1`; robot at `d2` |
| L2 | L1 plus `c3` onboard the robot |
| L3 | Logistics: `c1` at `d2`; `c3` at `d3` |
| L4 | Logistics: all containers at `d3` |

Use these IDs when reading the handout and discussing results in your PDF report.

The required modifications are fixed. Do **not** invent a different world modification.

---
Submit:

1. the ten completed PDDL TODO files listed below; and
2. one **PDF report** following the analysis requirements in the project handout. The PDF filename is up to you unless the submission system specifies one.

The detailed report questions are in the assignment PDF/LaTeX handout, not in this README. This README is primarily a guide to the codebase and the implementation tasks.

---

# Repository layout

```text
cmsc421-project2/
|-- README.md
|-- requirements.txt
|-- pytest.ini
|-- run_experiments.py
|-- make_plots.py
|-- visualize_plan.py
|-- main.tex
|-- planner/
|   |-- __init__.py
|   |-- __main__.py
|   |-- model.py
|   |-- pddl.py
|   |-- search.py
|   |-- graphplan.py
|   `-- validate.py
|-- pddl/
|   |-- blocksworld/
|   |   |-- domain.pddl                      PROVIDED
|   |   |-- baseline3.pddl                   PROVIDED
|   |   |-- sussman3.pddl                    TODO
|   |   |-- sussman6.pddl                    TODO
|   |   |-- domain_two_grippers.pddl         TODO
|   |   `-- sussman3_two_grippers.pddl       TODO
|   |-- elevator/
|   |   |-- domain.pddl                      PROVIDED
|   |   |-- baseline.pddl                    PROVIDED
|   |   |-- domain_split_service.pddl        TODO
|   |   `-- split_service.pddl               TODO
|   `-- logistics/
|       |-- domain.pddl                                      PROVIDED
|       |-- goal_c1_d2.pddl                                  PROVIDED
|       |-- goal_c1_d1_robot_d2.pddl                         TODO
|       |-- goal_c1_d1_c3_onboard_robot_d2.pddl              TODO
|       |-- goal_c1_d2_c3_d3.pddl                            TODO
|       `-- goal_all_d3.pddl                                 TODO
|-- tests/
|   |-- conftest.py
|   |-- test_baseline.py
|   |-- test_student_models.py
|   `-- test_visualize_plan.py
`-- results/
    `-- .gitkeep
```

Every student file initially contains:

```text
TODO-STUDENT: UNFINISHED
```

The public tests and experiment runner skip that task while the marker is present. **Remove the marker only after the file is complete.**

---

# Setup

Use Python 3.10 or newer. If you have not cloned the repository yet, run:

```bash
git clone https://github.com/hjhyunjinkim/cmsc421-project2.git
cd cmsc421-project2
```

Run the remaining commands from the repository root.

A virtual environment is recommended:

```bash
conda create -n project2 python=3.10
conda activate project2
```

Activate it, then install the dependencies:

```bash
pip install -r requirements.txt
```

The planning code itself uses only the Python standard library. `matplotlib` is
used for the required figures, and `pytest` is used only to verify the PDDL and
planner outputs.

Run the baseline smoke test to confirm the installation and see both supplied
planners solve the provided B0 problem:

```bash
python -m planner
```

This smoke test prints one sequential BFS plan and one parallel GraphPlan plan.
It is only a quick demonstration; the experiment runner described below is what
you will use to generate results for the report.

---

# Files you may modify

Modify only these files:

```text
pddl/blocksworld/sussman3.pddl
pddl/blocksworld/sussman6.pddl
pddl/blocksworld/domain_two_grippers.pddl
pddl/blocksworld/sussman3_two_grippers.pddl

pddl/elevator/domain_split_service.pddl
pddl/elevator/split_service.pddl

pddl/logistics/goal_c1_d1_robot_d2.pddl
pddl/logistics/goal_c1_d1_c3_onboard_robot_d2.pddl
pddl/logistics/goal_c1_d2_c3_d3.pddl
pddl/logistics/goal_all_d3.pddl
```

Do **not** modify:

```text
planner/
run_experiments.py
make_plots.py
tests/

pddl/blocksworld/domain.pddl
pddl/blocksworld/baseline3.pddl
pddl/elevator/domain.pddl
pddl/elevator/baseline.pddl
pddl/logistics/domain.pddl
pddl/logistics/goal_c1_d2.pddl
```

The supplied planners are experimental infrastructure. Changing them would make comparisons inconsistent.

---

# Part 1 - Blocks World

The baseline files are already complete:

```text
pddl/blocksworld/domain.pddl
pddl/blocksworld/baseline3.pddl
```

Run them before changing anything so that you have a control case.

## 1. Sussman anomaly

Complete:

```text
pddl/blocksworld/sussman3.pddl
```

Use exactly the objects:

```text
a b c - block
```

Required initial facts:

```text
(on c a)
(ontable a)
(ontable b)
(clear b)
(clear c)
(handempty)
```

Required goals:

```text
(on a b)
(on b c)
```

This is a **problem-instance change**. Do not modify the standard Blocks World domain.

## 2. Six-block scaling instance

Complete:

```text
pddl/blocksworld/sussman6.pddl
```

Use exactly:

```text
a b c d e f - block
```

Required initial facts:

```text
(on c a)
(ontable a)
(ontable b)
(ontable d)
(ontable e)
(ontable f)
(clear b)
(clear c)
(clear d)
(clear e)
(clear f)
(handempty)
```

Required goals:

```text
(on a b)
(on b c)
(on c d)
(on d e)
(on e f)
```

This is also a **problem-instance change**. The domain remains the standard one-gripper Blocks World domain.

## 3. Two-gripper extension

Complete both:

```text
pddl/blocksworld/domain_two_grippers.pddl
pddl/blocksworld/sussman3_two_grippers.pddl
```

The extended domain must use exactly the domain name:

```text
blocks-two-grippers
```

and the types:

```text
block gripper
```

Use these dynamic predicates in place of the single-gripper `handempty` / `holding` representation:

```text
(free ?g - gripper)
(holding ?g - gripper ?x - block)
```

Keep the standard block predicates:

```text
(on ?x - block ?y - block)
(ontable ?x - block)
(clear ?x - block)
```

Implement all four actions:

```text
pickup
putdown
stack
unstack
```

Each action must have an explicit `?g - gripper` parameter and must update the state of that gripper correctly.

The problem file must contain exactly two gripper objects:

```text
left right - gripper
```

Both start free. Use the same block configuration and goals as `sussman3.pddl`.

This is a **domain-model change**: the set of available resources and grounded actions changes.

---

# Part 2 - Elevator World

The baseline files are provided:

```text
pddl/elevator/domain.pddl
pddl/elevator/baseline.pddl
```

Run them first as a control case.

## Split-service extension

Complete:

```text
pddl/elevator/domain_split_service.pddl
pddl/elevator/split_service.pddl
```

Use the domain name:

```text
elevator-split-service
```

Keep these predicates:

```text
(lift-at ?e - elevator ?f - floor)
(passenger-at ?p - passenger ?f - floor)
(boarded ?p - passenger ?e - elevator)
```

Add exactly this static movement predicate:

```text
(link ?e - elevator ?from - floor ?to - floor)
```

The `move` action must require both:

```text
(lift-at ?e ?from)
(link ?e ?from ?to)
```

The `board` and `leave` actions should retain their baseline meaning.

Use exactly these objects:

```text
even odd - elevator
p1 p2 - passenger
f0 f1 f2 f3 f4 f5 f6 - floor
```

Required dynamic initial facts:

```text
(lift-at even f2)
(lift-at odd f5)
(passenger-at p1 f2)
(passenger-at p2 f5)
```

This means `p1` is waiting at `f2` with the `even` elevator and `p2` is waiting at `f5` with the `odd` elevator. **Neither passenger is boarded initially.**

Required service links:

```text
(link even f0 f2)   (link even f2 f0)
(link even f2 f4)   (link even f4 f2)
(link even f4 f6)   (link even f6 f4)

(link odd f0 f1)    (link odd f1 f0)
(link odd f1 f3)    (link odd f3 f1)
(link odd f3 f5)    (link odd f5 f3)
```

No other `link` facts should be added. The floors served by both elevator networks intersect only at `f0`, so `f0` is the only possible transfer floor.

Required goals:

```text
(passenger-at p1 f3)
(passenger-at p2 f4)
```

Thus both passengers must use `f0` as the transfer floor between the two service networks.

---

# Part 3 - Logistics Goal-Interaction Study

The Logistics domain and baseline problem are provided:

```text
pddl/logistics/domain.pddl
pddl/logistics/goal_c1_d2.pddl
```

The domain provides `pickup`, `putdown`, and `move`. It has one robot with
capacity one, represented by the positive fluent `empty`. All five Logistics
experiments use the same objects, connectivity, and initial state; only the goal
conjunction changes.

Use exactly these objects in L1--L4:

```text
r1 - robot
c1 c2 c3 - container
d1 d2 d3 - location
```

Use exactly this common initial state:

```text
(onboard c1 r1)
(container-at c2 d1)
(container-at c3 d2)
(robot-at r1 d1)

(connected d1 d2) (connected d2 d1)
(connected d1 d3) (connected d3 d1)
(connected d2 d3) (connected d3 d2)
```

Container `c1` starts onboard, so the robot does **not** initially have an
`(empty r1)` fact. Do not change the provided Logistics domain or add initial
facts to make a goal easier.

## L0 - Baseline: deliver `c1` to `d2`

The provided baseline goal in `pddl/logistics/goal_c1_d2.pddl` is:

```text
(container-at c1 d2)
```

Run L0 first as a control case.

## L1 - Container and robot location goals

Complete `pddl/logistics/goal_c1_d1_robot_d2.pddl` with the common objects and
initial state, and exactly these goal facts:

```text
(container-at c1 d1)
(robot-at r1 d2)
```

## L2 - Container-onboard goal

Complete `pddl/logistics/goal_c1_d1_c3_onboard_robot_d2.pddl` with:

```text
(container-at c1 d1)
(robot-at r1 d2)
(onboard c3 r1)
```

All three facts must hold in the same final state.

## L3 - Two-container delivery goal

Complete `pddl/logistics/goal_c1_d2_c3_d3.pddl` with:

```text
(container-at c1 d2)
(container-at c3 d3)
```

The robot's final location and `c2`'s final location are not goal facts.

## L4 - Full delivery goal

Complete `pddl/logistics/goal_all_d3.pddl` with:

```text
(container-at c1 d3)
(container-at c2 d3)
(container-at c3 d3)
```

The robot's final location and whether it is empty are not separately required.

---

# Running BFS and GraphPlan experiments

Run every currently completed case through **both** supplied planners with:

```bash
python run_experiments.py
```

This one command runs forward STRIPS/BFS and GraphPlan for each completed case.
There is no separate planner option for the experiment runner, and you do not
need to invoke the planners individually. Cases that still contain the
`TODO-STUDENT: UNFINISHED` marker are skipped.

The script writes:

```text
results/results.csv
results/plans.txt
```

`results/results.csv` contains both the handout experiment ID (for example `B1`) and a descriptive internal case name. It records, when applicable:

- `experiment_id`: the B0--B3 / E0--E1 / L0--L4 identifier used in the handout;
- `case`: a descriptive machine-readable case name;
- `ground_actions`: number of grounded actions for the problem;
- `states_generated`, `states_expanded`, `visited_states`, `max_frontier`: forward-BFS search measurements;
- `plan_actions`: number of non-persistence actions in the returned plan;
- `makespan`: number of sequential steps for BFS or parallel time steps for GraphPlan;
- `graph_levels`: GraphPlan planning horizon, i.e. the number of action layers built before successful extraction;
- `fact_nodes` and `action_nodes`: cumulative planning-graph nodes across built layers;
- `action_mutexes` and `fact_mutexes`: cumulative mutex pairs across built layers; and
- `runtime_s`: wall-clock runtime for that run.

`results/plans.txt` contains the actual sequential BFS plan and the parallel GraphPlan plan for every completed configuration.

For the final report, enable reachable-state enumeration so that the BFS table
can report reachable-state counts:

```bash
python run_experiments.py --enumerate-reachable
```

Reachable-state enumeration can be more expensive than solving alone. The
output indicates whether the count is exact or was capped by the node limit.

---

# Generating the required figures

After all TODO files are finished and `run_experiments.py` has been run, execute:

```bash
python make_plots.py
```

This creates:

```text
results/search_effort.png
results/plan_structure.png
```

- `search_effort.png` compares forward-BFS states expanded.
- `plan_structure.png` compares GraphPlan primitive action count with parallel makespan.

These figures are inputs to your **PDF report**. 

---

# Visualizing a plan (optional)

The standalone visualizer is the place to select one planner explicitly. It
solves one completed experiment and displays its world-state trace. It supports
Blocks World, Elevator, and Logistics without changing the supplied planner or
experiment code.

List the cases that are currently ready:

```bash
python visualize_plan.py --list
```

The visualizer supports both supplied planners. To inspect the sequential plan
returned by forward STRIPS BFS:

```bash
python visualize_plan.py --case B0 --planner bfs
```

To inspect the parallel plan returned by GraphPlan:

```bash
python visualize_plan.py --case B0 --planner graphplan
```

Use **Previous** and **Next** (or the left and right arrow keys) to inspect the
plan one step at a time. Satisfied goal facts are outlined in green. BFS frames
contain one action at a time, while a GraphPlan frame can contain multiple
independent actions executed in parallel. GraphPlan is the default if
`--planner` is omitted.

An unfinished student case reports which PDDL file must be completed instead of
trying to display a partial model.

---

# Verifying your work with the public tests

After generating and inspecting your experiment results, run:

```bash
python -m pytest
```

`pytest` is a verification command, not the experiment runner. The public tests
check the prescribed structure of the student PDDL files and verify that the
resulting problems are solvable by both supplied planners.
The final `PDDL checks` section reports every baseline and student case as
`PASS`, `FAIL`, or `INCOMPLETE`. An incomplete case still contains a
`TODO-STUDENT: UNFINISHED` marker. If a completed model fails, pytest also
prints the corresponding assertion details.

Passing the public tests does not replace inspecting the generated plans. Your report is graded on whether you understand and explain the observed behavior.

---
