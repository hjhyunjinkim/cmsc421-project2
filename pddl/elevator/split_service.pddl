; TODO-STUDENT: UNFINISHED
; Exact service links:
; even: f0<->f2<->f4<->f6
; odd:  f0<->f1<->f3<->f5
; Required passengers: p1 f2->f3, p2 f5->f4
; Initial elevators: even at f2, odd at f5
; Delete the TODO-STUDENT line only when the file is complete.

(define (problem elevator-split-service-problem)
  (:domain elevator-split-service)
  (:objects
    even odd - elevator
    p1 p2 - passenger
    f0 f1 f2 f3 f4 f5 f6 - floor)

  (:init
    ; TODO: elevator positions and passenger positions
    ; TODO: add exactly the 12 directed link facts specified above
  )

  (:goal (and
    ; TODO: p1 at f3 and p2 at f4
  ))
)
