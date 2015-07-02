#Based on http://www.math.rwth-aachen.de/~Gerhard.Hiss/Students/DiplomarbeitPfeiffer.pdf
#algorithm 3, 4
import itertools

#def dprint(*args, **kwargs):    pass

dprint = print

def showValue(s, valueRepr=str):
    """printable representation of elements"""
    if len(s) == 0:
        return "e"
    
    def escape(s):
        return s if len(s)==1 else "["+s+"]"
    
    return "".join(escape(valueRepr(x)) for x in s)

class RewriteRuleset:
    def __init__(self, rules):
        self.rules = rules

    def pprint(self):
        print ("{")
        for v, w in self._sortedItems():
            print ("  {sv} -> {sw}".format(sv = showValue(v), sw = showValue(w)))
        print ("}")
    def copy(self): return RewriteRuleset(self.rules.copy())
    def _sortedItems(self):
        shortKey = LessKey(shortLex)
        return sorted(self.rules.items(),
                      key=lambda vw: shortKey(vw[0]))
    def suffices(self): return self.rules.keys()
    def __str__(self):
        return "{"+", ".join( "{sv}->{sw}".format(sv = showValue(v), sw = showValue(w))
                              for v, w in self._sortedItems()) +"}"

    def size(self): return len(self.rules)    
    def items(self): return self.rules.items()
    def __eq__(self, other): return self.rules == other.rules
    def __hash__(self): return hash(self.rules)
    def add(self, v, w):
        self.rules[v] = w
    def remove(self, v):
        del self.rules[v]
        
    def normalize( self, lessOrEq ):
        SS  = dict()
        for v, w in self.rules.items():
            v, w = sortPairReverse(v, w, lessOrEq)
            #v is biggest now
            if v not in SS:
                SS[v] = w
            else:
                #resolve conflict by chosing the lowest of 2.
                SS[v] = sortPairReverse(w, SS[v], lessOrEq)[1]
        return RewriteRuleset(SS)

    def __ruleLengths(self):
        return sorted(set( len(key) for key in self.rules.keys()))
    
    def appendRewrite(self, s, xs_):
        """Append elements of the string xs_ (reversed) to the string s, running all rewrite rules"""
        rules = self.rules
        
        s = list(s)
        xs = list(reversed(xs_))
        
        lengths = self.__ruleLengths()

        while len(xs) > 0:
            s.append(xs.pop())
            for suffixLen in lengths:
                suffix = tuple(s[-suffixLen:])
                rewriteAs = rules.get(suffix)
                if rewriteAs is not None:
                    #Rewrite found!
                    dprint("Rewrite", suffix, "as", rewriteAs)
                    del s[-suffixLen:]
                    xs.extend( reversed(rewriteAs) )
                    continue
        return tuple(s)

    def rewrite( self, s ): return self.appendRewrite( (), s )
    def __call__(self, s ): return self.rewrite(s)
    
    @staticmethod
    def parse(srules):
        def parseVal(s):
            return tuple(s.replace("e", "").strip())

        rules = dict()
        for r in srules.split(","):
            l, r = map(parseVal, r.split("->"))
            rules[l] = r
        return RewriteRuleset(rules)

def LessKey(lessOrEq):
    """COnvert comparator to a sorting key"""
    class Key:
        def __init__(self, x):
            self.value = x
        def __lt__(self, other):
            return not lessOrEq(other.value, self.value)
        def __eq__(self, other):
            return self.value == other.value
    return Key

def shortLex(s1, s2):
    """Shortlex less or equal comparator"""
    if len(s1) > len(s2):
        return False
    if len(s1) < len(s2):
        return True
    return s1 <= s2

def overlap(s1, s2):
    """Two strings: s1, s2.
    Reutnrs x,y,z such as:
    s1 = xy
    s2 = yz
    """

    if len(s2) == 0:
        return s1, (), s2
    
    i1, i2 = 0, 0
    #i1, i2: indices in s1, s2
    s2_0 = s2[0]
    istart = max( 0, len(s1) - len(s2) )
    for i in range(istart, len(s1)):
        s1_i = s1[i]
        if s1_i == s2_0:
            if s1[i+1:] == s2[1:len(s1)-i]:
                return s1[:i], s1[i:], s2[len(s1)-i:]
    return s1, (), s2

def splitBy(s1, s2):
    """Split sequence s1 by sequence s2.
    Returns True and prefix + postfix, or just False and None None
    """
    if len(s2) == 0:
        return True, s1, ()
    
    for i in range(len(s1) - len(s2)+1):
        if s1[i:i+len(s2)] == s2:
            return True, s1[:i], s1[i+len(s2):]
    return False, None, None

def sortPairReverse( a, b, lessOrEq ):
    """return a1, b1 such that a1 >= b1"""
    return (b, a) if lessOrEq(a,b) else (a,b)

def findOverlap( v1, w1, v2, w2 ):
    """Find a sequence that is can be rewritten in 2 ways using given rules"""
    # if v1=xy and v2=yz
    x, y, z = overlap(v1, v2)
    if y: #if there is nonempty overlap
        return True, x+w2, w1+z
    
    hasSplit, x, z = splitBy(v1, v2)
    if hasSplit:# and len(x)>0 and len(z)>0
        return True, w1, x+w2+z

    return False, None, None

def knuthBendixCompletion(S, lessOrEqual):
    """S :: dict of rewrite rules: (original, rewrite)
    lessorequal :: (x, y) -> boolean
    """
    assert isinstance( S, RewriteRuleset )

    SS = S.copy()
    #
    for (v1, w1) in S.items():
        for (v2, w2) in S.items():
            # if v1=xy and v2=yz
            x, y, z = overlap(v1, v2)
            hasOverlap, s1, s2 = findOverlap(v1,w1, v2,w2)
            if hasOverlap:
                t1, t2 = map(S, (s1,s2))
                if t1 != t2:
                    dprint ("Conflict found", v1, w1, v2, w2)
                    t1, t2 = sortPairReverse(t1, t2, lessOrEqual)
                    #dprint("    add rule:", (t1,t2) )
                    SS.add(t1, t2)
    return SS

def simplifyRules(S_, lessOrEqual):
    S = S_.copy()
    Slist = list(S_.items()) #used to iterate
    
    while Slist:
        v,w = vw = Slist.pop()
        S.remove(v)

        vv, ww = map(S, vw)
        
        addBack = True
        if vv == ww:
            #dprint("Redundant rewrite", v, w)
            addBack = False
        else:
            vw1 = sortPairReverse(vv,ww, lessOrEqual)
            if vw1 != vw:
                #dprint ("Simplify rule:", vw, "->", vw1 )
                S.add( *vw1 )
                Slist.append(vw1)
                addBack = False
        if addBack:
            S.add(v,w)
    return S

def knuthBendix(S0, lessOrEqual=shortLex, maxIters = 1000, maxRulesetSize = 1000, onIteration=None):
    """Main funciton of the Knuth-Bendix completion algorithm.
    arguments:
    S - original rewrite table
    lessOrEqual - comparator for strings. shortLex is the default one.
    maxIters - maximal number of iterations. If reached, exception is raised.
    maxRulesetSize - maximal number of ruleset. If reached, exception is raised.
    onIteration - callback, called each iteration of the method. It receives iteration number and current table.
    """
    S = S0.normalize(lessOrEqual)
    for i in range(maxIters):
        if S.size() > maxRulesetSize:
            raise ValueError("Ruleset grew too big")
        SS = simplifyRules(S, lessOrEqual)
        SSS = knuthBendixCompletion(SS, lessOrEqual)
        if SSS == S:
            #Convergence achieved!
            return SSS
        if onIteration: onIteration( i, S )
        S = SSS
    raise ValueError("Iterations exceeded")
    
