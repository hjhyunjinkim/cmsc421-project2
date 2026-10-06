; Provided baseline. Do not modify.
(define (problem blocks-baseline-3)
  (:domain blocks)
  (:objects a b c - block)
  (:init
    (ontable a)
    (ontable b)
    (ontable c)
    (clear a)
    (clear b)
    (clear c)
    (handempty))
  (:goal (and
    (on a b)
    (on b c)))
)
