from knuth_bendix import knuthBendix, RewriteRuleset, shortLex

def vdRule(n, m, k=2):
    """Create initial ruleset for von Dyck group with inverse elements
    https://en.wikipedia.org/wiki/Triangle_group#von_Dyck_groups
    """
    return RewriteRuleset({
        tuple('aA'): (),
        tuple('Aa'): (),
        tuple('bB'): (),
        tuple('Bb'): (),
        
        tuple('BA'*k): (),
        tuple('ab'*k): (),

        tuple( 'A'*n ): (),
        tuple( 'a'*n ): (),
             
        tuple( 'B'*m ): (),
        tuple( 'b'*m ): () })


def groupPowers(s):
    last = None
    lastPow = None
    for x in s:
        if last is None:
            last = x
            lastPow = 1
        else:
            if x == last:
                lastPow += 1
            else:
                yield last, lastPow
                last = x
                lastPow = 1
    if last is not None:
        yield last, lastPow

def groupPowersVd(s):
    for x, p in groupPowers(s):
        if x.upper() == x:
            yield x.lower(), -p
        else:
            yield x, p

def showGroupedPowers(s):
    if not s: return "e"
    return " ".join( (x if p == 1 else x+"^"+str(p))
                     for x, p in groupPowersVd(s))



import itertools

def powers(n):
    #powers from n // 2 to n//2-n, excluding 0
    for a,b in itertools.zip_longest( range(1, n-n//2+1),
                                       range(1, n//2+1)):
        if a is not None: yield a
        if b is not None: yield -b

def powerVondyck(n, m):
    """ each element of double VD group is some power of the original VD elements.
    powers are orderede from highest to lowest"""

    elements = []
    for p in reversed(list(powers(n))):
        elements.append(('a', p))
    for p in reversed(list(powers(m))):
        elements.append(('b', p))
        
    element2index = {e:i for i, e in enumerate(elements)}

    a = element2index[('a', 1)]
    ia = element2index[('a', -1)]
    b = element2index[('b', 1)]
    ib = element2index[('b', -1)]
    
    
    def showElement(i):
        a, p = elements[i]
        return "%s^%s"%(a,p)


    relations = {}
    #generate identities.
    # powers
    for i1,(c1, p1) in enumerate(elements):
        for i2, (c2, p2) in enumerate(elements):
            if c1 != c2: continue
            order = n if c1 == 'a' else m
            
            ps = (p1 + p2 + order//2)%order - order //2
            print ("#####", showElement(i1),"*",showElement(i2),"=",ps)
            if ps == 0:
                relations[(i1,i2)] = ()
            else:
                relations[(i1,i2)] = (element2index[(c1, ps)],)

    # special identities:
    # abab = e
    # BABA = e
    relations[(a,b,a,b)] = ()
    relations[(ib,ia,ib,ia)] = ()
    
    return RewriteRuleset(relations), showElement
    
if __name__=="__main__":

    #print (powerVondyck(4,5))
    
    
    #rules = RewriteRuleset.parse( "aA->e, bB->e")
    
    rules = vdRule( 5, 5)
    #rules, showElem = powerVondyck(4,5)

    def showProgress(i, s):
        print ("Iteration {i}, ruleset size: {n}".format(i=i,n=s.size()))
    rules1 = knuthBendix (rules, onIteration=showProgress, maxRulesetSize=10000)
    rules1.pprint()


    for v,w in rules1._sortedItems():
        print("   {sv}\t-> {sw}".format(sv = showGroupedPowers(v),
                                       sw = showGroupedPowers(w)))


    from automaton import *
    automaton, initial_state = build_accepting_automaton( 'abAB', list(rules1.suffices()) )

    print ("Number of states:", len(automaton.state_names))
    #print (automaton.transitions)
    with open("wd.dot","w") as dotfile:
        export_dot(automaton, dotfile)

    if True:
        #symbolic growth func
        print("growth func:")
        func = automaton_growth_func(automaton, initial_state)
        print("funciton calculated, simplifying...")
        import sympy
        func = sympy.cancel(func)
        print("done. Printing...")
        print(func)

    if False:
        #numeric growth func
        num, den = growth_function_numpy(automaton, initial_state)

        from ss2tf import *
        print (num, den)

        gcd = polygcd(num, den)
        num1,_ = np.polydiv(num,gcd)
        den1,_ = np.polydiv(den,gcd)

        print (num1, den1)
        
