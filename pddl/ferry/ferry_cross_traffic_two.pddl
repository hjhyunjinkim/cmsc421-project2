; TODO-STUDENT: UNFINISHED
; Same four-car cross-traffic task as ferry_cross_traffic.pddl.
; ferry1 starts at left-bank; ferry2 starts at right-bank; both start empty.
; Include both sailing routes.
; Delete the TODO-STUDENT line only when the file is complete.

(define (problem ferry-cross-traffic-two)
  (:domain ferry-two)
  (:objects
    c1 c2 c3 c4 - car
    ferry1 ferry2 - ferry
    left-bank right-bank - location)

  (:init
    ; TODO: exact car, ferry, empty, and route facts
  )

  (:goal (and
    ; TODO: same four car goals as the one-ferry problem
  ))
)
