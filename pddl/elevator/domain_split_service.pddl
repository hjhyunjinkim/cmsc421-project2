; TODO-STUDENT: UNFINISHED
; Add exactly this static movement predicate:
;   (link ?e - elevator ?from - floor ?to - floor)
; move must require both (lift-at ?e ?from) and (link ?e ?from ?to).
; board and leave retain their baseline meaning.
; Delete the TODO-STUDENT line only when the file is complete.

(define (domain elevator-split-service)
  (:requirements :strips :typing)
  (:types elevator passenger floor)

  (:predicates
    (lift-at ?e - elevator ?f - floor)
    (passenger-at ?p - passenger ?f - floor)
    (boarded ?p - passenger ?e - elevator)

    ; TODO: add link
  )

  ; TODO: implement move, board, and leave.
)
