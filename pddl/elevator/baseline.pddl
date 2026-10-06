; Provided baseline. Do not modify.
(define (problem elevator-baseline)
  (:domain elevator)
  (:objects
    e0 - elevator
    p1 p2 - passenger
    f0 f1 f2 f3 - floor)
  (:init
    (lift-at e0 f0)
    (passenger-at p1 f0)
    (passenger-at p2 f3)

    (adjacent f0 f1) (adjacent f1 f0)
    (adjacent f1 f2) (adjacent f2 f1)
    (adjacent f2 f3) (adjacent f3 f2))
  (:goal (and
    (passenger-at p1 f3)
    (passenger-at p2 f1)))
)
