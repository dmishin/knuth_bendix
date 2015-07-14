import numpy as np
def ss2tf(a,b,c):    
    den = np.poly(a)
    num = np.poly(a-np.dot(b,c)) - den

    return num, den


#from https://github.com/numpy/numpy/issues/4829
def polygcd(a,b, eps=1e-6):
    '''return monic GCD of polynomials a and b'''
    pa = a
    pb = b
    M = lambda x: x/x[0]
    # find gcd of a and b
    while len(pb) > 1 or pb[0] != 0:
        # Danger Will Robinson! requires numerical equality
        q,r = np.polydiv(pa,pb)
        pa = pb
        pb = r
    return M(pa)

def polylcm(a,b):
    '''return (Ka,Kb,c) such that c = LCM(a,b) = Ka*a = Kb*b'''        
    gcd = polygcd(a,b)
    Ka,_ = np.polydiv(b,gcd)
    Kb,_ = np.polydiv(a,gcd)
    return (Ka,Kb,np.polymul(Ka,a))
