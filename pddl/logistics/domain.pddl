; Provided baseline. Do not modify.
(define (domain logistics)
  (:requirements :strips :typing)
  (:types robot container location)

  (:predicates
    (robot-at ?r - robot ?l - location)
    (container-at ?c - container ?l - location)
    (onboard ?c - container ?r - robot)
    (empty ?r - robot)
    (connected ?from - location ?to - location))

  (:action pickup
    :parameters (?r - robot ?c - container ?l - location)
    :precondition (and
      (robot-at ?r ?l)
      (container-at ?c ?l)
      (empty ?r))
    :effect (and
      (onboard ?c ?r)
      (not (container-at ?c ?l))
      (not (empty ?r))))

  (:action putdown
    :parameters (?r - robot ?c - container ?l - location)
    :precondition (and
      (robot-at ?r ?l)
      (onboard ?c ?r))
    :effect (and
      (container-at ?c ?l)
      (empty ?r)
      (not (onboard ?c ?r))))

  (:action move
    :parameters (?r - robot ?from - location ?to - location)
    :precondition (and
      (robot-at ?r ?from)
      (connected ?from ?to))
    :effect (and
      (robot-at ?r ?to)
      (not (robot-at ?r ?from))))
)
