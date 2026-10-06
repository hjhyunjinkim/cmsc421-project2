; Provided baseline. Do not modify.
(define (problem ferry-baseline)
  (:domain ferry)
  (:objects
    c1 - car
    left-bank right-bank - location)
  (:init
    (car-at c1 left-bank)
    (ferry-at left-bank)
    (empty)
    (route left-bank right-bank)
    (route right-bank left-bank))
  (:goal (and
    (car-at c1 right-bank)))
)
