; TODO-STUDENT: UNFINISHED
; Extend standard Blocks World to exactly two explicit grippers.
; Required predicates:
;   (free ?g - gripper)
;   (holding ?g - gripper ?x - block)
; Keep on / ontable / clear.
; Implement pickup, putdown, stack, and unstack with a ?g - gripper parameter.
; Delete the TODO-STUDENT line only when the file is complete.

(define (domain blocks-two-grippers)
  (:requirements :strips :typing)
  (:types block gripper)

  (:predicates
    (on ?x - block ?y - block)
    (ontable ?x - block)
    (clear ?x - block)

    ; TODO: add (free ...) and (holding ...)
  )

  ; TODO: implement pickup, putdown, stack, and unstack.
)
