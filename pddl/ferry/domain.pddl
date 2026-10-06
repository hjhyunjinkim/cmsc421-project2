; Provided baseline. Do not modify.
(define (domain ferry)
  (:requirements :strips :typing)
  (:types car location)

  (:predicates
    (car-at ?c - car ?l - location)
    (ferry-at ?l - location)
    (empty)
    (onboard ?c - car)
    (route ?from - location ?to - location))

  (:action board
    :parameters (?c - car ?l - location)
    :precondition (and
      (car-at ?c ?l)
      (ferry-at ?l)
      (empty))
    :effect (and
      (onboard ?c)
      (not (car-at ?c ?l))
      (not (empty))))

  (:action debark
    :parameters (?c - car ?l - location)
    :precondition (and
      (onboard ?c)
      (ferry-at ?l))
    :effect (and
      (car-at ?c ?l)
      (empty)
      (not (onboard ?c))))

  (:action sail
    :parameters (?from - location ?to - location)
    :precondition (and
      (ferry-at ?from)
      (route ?from ?to))
    :effect (and
      (ferry-at ?to)
      (not (ferry-at ?from))))
)
