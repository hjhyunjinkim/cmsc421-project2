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

The assignment handout names the nine experimental configurations as follows:

| ID | Configuration |
| --- | --- |
| B0 | Blocks World baseline, 3 blocks (provided) |
| B1 | Blocks World Sussman anomaly, 3 blocks |
| B2 | Blocks World scaled to 6 blocks |
| B3 | B1 with two independent grippers |
| E0 | Elevator baseline (provided) |
| E1 | Split-service even/odd elevators |
| F0 | Ferry baseline (provided) |
| F1 | Four-car cross traffic with one ferry |
| F2 | F1 with two independent ferries |

Use these IDs when reading the handout and discussing results in your PDF report.

The required modifications are fixed. Do **not** invent a different world modification.

---
Submit:

1. the nine completed PDDL TODO files listed below; and
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
|   `-- ferry/
|       |-- domain.pddl                      PROVIDED
|       |-- baseline.pddl                    PROVIDED
|       |-- ferry_cross_traffic.pddl         TODO
|       |-- domain_two_ferries.pddl          TODO
|       `-- ferry_cross_traffic_two.pddl     TODO
|-- tests/
|   |-- test_baseline.py
|   `-- test_student_models.py
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
python -m venv .venv
```

Activate it, then install the dependencies:

```bash
pip install -r requirements.txt
```

The planning code itself uses only the Python standard library. `pytest` is used for the public tests and `matplotlib` is used for the required figures.

Run the baseline smoke test:

```bash
python -m planner
```

Run the public tests:

```bash
python -m pytest
```

A fresh starter repository should report the baseline tests as passing and the unfinished student-model tests as skipped.

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

pddl/ferry/ferry_cross_traffic.pddl
pddl/ferry/domain_two_ferries.pddl
pddl/ferry/ferry_cross_traffic_two.pddl
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
pddl/ferry/domain.pddl
pddl/ferry/baseline.pddl
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

# Part 3 - Ferry World

The baseline files are provided:

```text
pddl/ferry/domain.pddl
pddl/ferry/baseline.pddl
```

Run them first as a control case.

## 1. Cross traffic with one ferry

Complete:

```text
pddl/ferry/ferry_cross_traffic.pddl
```

Use exactly:

```text
c1 c2 c3 c4 - car
left-bank right-bank - location
```

Required initial facts:

```text
(car-at c1 left-bank)
(car-at c2 left-bank)
(car-at c3 right-bank)
(car-at c4 right-bank)
(ferry-at left-bank)
(empty)
(route left-bank right-bank)
(route right-bank left-bank)
```

Required goals:

```text
(car-at c1 right-bank)
(car-at c2 right-bank)
(car-at c3 left-bank)
(car-at c4 left-bank)
```

The provided ferry domain still has capacity one.

## 2. Two-ferry extension

Complete:

```text
pddl/ferry/domain_two_ferries.pddl
pddl/ferry/ferry_cross_traffic_two.pddl
```

Use the domain name:

```text
ferry-two
```

Use these types:

```text
car ferry location
```

Use these predicates:

```text
(car-at ?c - car ?l - location)
(ferry-at ?f - ferry ?l - location)
(empty ?f - ferry)
(onboard ?c - car ?f - ferry)
(route ?from - location ?to - location)
```

Implement:

```text
board
debark
sail
```

Each action must explicitly identify which ferry is being used. Each ferry has its own location and its own `empty` state, so each ferry independently has capacity one.

The problem must contain exactly:

```text
ferry1 ferry2 - ferry
```

Required ferry initial facts:

```text
(ferry-at ferry1 left-bank)
(ferry-at ferry2 right-bank)
(empty ferry1)
(empty ferry2)
```

Use the same four cars, car starting positions, routes, and car goals as the one-ferry cross-traffic problem.

Do not add extra locations or change capacity.

---

# Running the experiments

Run every currently completed case with:

```bash
python run_experiments.py
```

The script writes:

```text
results/results.csv
results/plans.txt
```

`results/results.csv` contains both the handout experiment ID (for example `B1`) and a descriptive internal case name. It records, when applicable:

- `experiment_id`: the B0--B3 / E0--E1 / F0--F2 identifier used in the handout;
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

Optional reachable-state enumeration:

```bash
python run_experiments.py --enumerate-reachable
```

This is optional because enumeration can become expensive. The output indicates whether the count is exact or was capped by the node limit.

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

# Public tests

Run:

```bash
python -m pytest
```

The public tests verify the prescribed structure of the student PDDL files and check that the resulting problems are solvable by the supplied planners.

Passing the public tests does not replace inspecting the generated plans. Your report is graded on whether you understand and explain the observed behavior.

---