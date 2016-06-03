from sympy.matrices import Matrix, eye, zeros
from sympy import sin, pi, cos, abc
from sympy.solvers import solve

class TriangleGroup:
    def __init__(self,p,q,r):
        [sp,sq,sr] = (cos(pi/n) for n in [p,q,r])
        self.pqr = [p,q,r]
        
        m = Matrix([[-1,sp,sr],
                 [sp,-1,sq],
                 [sr,sq,-1]])
        print (m)
        self.m = m
        im = m*2 + eye(3)
     
        def sigma(k):
            s = zeros(3)
            e = eye(3)
            for i in range(3):
                for j in range(3):
                    s[i, j] = (im if i == k else e)[i,j]
            return s
             
        self.m_pqr = [sigma(i) for i in range(3)]
     
    def __str__(self):
       return "Trg({pqr[0]},{pqr[1]},{pqr[2]})".format(pqr=self.pqr)

from functools import reduce
if __name__=="__main__":
    t = TriangleGroup(abc.p, abc.q, abc.r)
    #t = TriangleGroup(3,4,5)

    mp, mq, mr = t.m_pqr
    a = mp*mq
    b = mq*mr
    c = mp*mr

    print ("===============")
    for m, powr in zip((a,b,c),t.pqr):
        print ("Rotational matrix:", powr)
        print(m)
        if isinstance(powr, int):
            mp = (m**powr)
            mp.simplify()
            print("m^{powr}={mp}".format(**locals()) )

    av, ad = a.diagonalize()

    print ("A diag:")
    print(av)
    print (ad)
    
