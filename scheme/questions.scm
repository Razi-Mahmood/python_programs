(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cdar x) (cdr (car x)))
(define (cddr x) (cdr (cdr x)))

; Some utility functions that you may find useful to implement.

;; Problem 17
;; Returns a list of two-element lists
(define (enumerate s)

        (define (helper s index)
            (cond ((null? s) nil)
              (else (cons (list index (car s))
                      (helper (cdr s) (+ index 1))))
            ))
    (helper s 0)
)

  ; END PROBLEM 17

;; Problem 18
;; List all ways to make change for TOTAL with DENOMS

(define (cons-all first rests)
    (map (lambda (var) (cons first var)) rests) ; map has a built-in base case
)

  (define (list-change total denoms)
    ; BEGIN PROBLEM 18

    (cond ((null? denoms) nil)

          ((= total 0) (list nil))

          ((> (car denoms) total)
              (list-change total (cdr denoms)))

          (else (append (cons-all (car denoms) (list-change (- total (car denoms)) denoms)) ;
                        (list-change total (cdr denoms)))) ;only need without-total because we don't need to add the denom element to our desired list
    )
  )
  ; END PROBLEM 18

;; Problem 19
;; Returns a function that checks if an expression is the special form FORM
(define (check-special form)
  (lambda (expr) (equal? form (car expr))))

(define lambda? (check-special 'lambda))
(define define? (check-special 'define))
(define quoted? (check-special 'quote))
(define let?    (check-special 'let))

;; Converts all let special forms in EXPR into equivalent forms using lambda

(define (zip pairs)

    (list (map car pairs) (map cadr pairs)) ;extract the car of each pair and combine with subsequent cars
)


(define (let-to-lambda expr)
  (cond ((atom? expr)
         ; BEGIN PROBLEM 19
         expr
         ; END PROBLEM 19
         )
        ((quoted? expr)
         ; BEGIN PROBLEM 19
         expr
         ; END PROBLEM 19
         )
        ((or (lambda? expr)
             (define? expr))
         (let ((form   (car expr))
               (params (cadr expr))
               (body   (cddr expr)))
           ; BEGIN PROBLEM 19
        ;   (cond
                ;((let? body) (let-to-lambda body)) ;if there is a nested let, convert to a lambda
                (cons form (cons (map let-to-lambda params) (map let-to-lambda body)))

           ; END PROBLEM 19
           ))
        ((let? expr)
         (let ((values (cadr expr))
               (body   (cddr expr)))
           ; BEGIN PROBLEM 19
           (begin (cons (cons 'lambda (cons (map let-to-lambda (car (zip values))) (map let-to-lambda body))) ;the map accounts for any nested let statements
              (map let-to-lambda (cadr (zip values))))
           ; END PROBLEM 19
           )))
        (else
         ; BEGIN PROBLEM 19
            (cond ((list? expr) (map let-to-lambda expr))
                  (else expr)
            )

         ; END PROBLEM 19
         )))
