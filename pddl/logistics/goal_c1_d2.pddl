; Provided baseline L0. Do not modify.
(define (problem logistics-l0-c1-d2)
  (:domain logistics)
  (:objects
    r1 - robot
    c1 c2 c3 - container
    d1 d2 d3 - location)
  (:init
    (onboard c1 r1)
    (container-at c2 d1)
    (container-at c3 d2)
    (robot-at r1 d1)
    (connected d1 d2)
    (connected d2 d1)
    (connected d1 d3)
    (connected d3 d1)
    (connected d2 d3)
    (connected d3 d2))
  (:goal (and
    (container-at c1 d2)))
)
