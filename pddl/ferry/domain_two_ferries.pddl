; TODO-STUDENT: UNFINISHED
; Required explicit-ferry predicates:
;   (ferry-at ?f - ferry ?l - location)
;   (empty ?f - ferry)
;   (onboard ?c - car ?f - ferry)
; Keep car-at and route.
; Implement board, debark, and sail with an explicit ?f - ferry parameter.
; Delete the TODO-STUDENT line only when the file is complete.

(define (domain ferry-two)
  (:requirements :strips :typing)
  (:types car ferry location)

  (:predicates
    (car-at ?c - car ?l - location)
    (route ?from - location ?to - location)

    ; TODO: add ferry-at, empty, and onboard
  )

  ; TODO: implement board, debark, and sail.
)
