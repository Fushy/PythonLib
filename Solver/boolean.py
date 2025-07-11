def xor(a, b):
    return (a | b) & ~(a & b)

from sympy import symbols, simplify, And, Or, Not
A, B, C, D = symbols('A B C D')
# expr = ~(A & B)
expr = ~A & ~B
# expr = (~(A | B) & ~(A & B))
# expr = ~((X & Y) | (X & Z)) | (~(X) & ~(Y) & Z)
# expr = ~(A & ~(~(B & B) & ~(C & C)))
# expr = (A & B & C) | (A & B & ~C & D) | (A & B & ~C) | (A & ~B & D) | (A & ~D)

print(simplify(expr))
