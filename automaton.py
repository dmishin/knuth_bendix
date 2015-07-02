#moved to Prog/knuth_bendix

class Automaton:
    def __init__(self):
        self.name2state = dict()
        self.state_names = []
        self.transitions = []
    def num_states(self):
        return len(self.transitions)
    def add_state(self, name):
        if name in self.name2state: 
            raise ValueError("State {} already exists".format(name))
        state = len(self.transitions)
        self.name2state[name] = state 
        self.state_names.append(name)
        self.transitions.append(dict()) #empty state without transitions
        return state

    def add_transition(self, state, input, new_state ):
        self.transitions[state][input] = new_state

    def next(self, state, input):
        """returns next state, or raises KeyError, if input is not accepted"""
        return self.transitions[state][input]

    def accept_seq(self, initial_state, inputs):
        """Returns final state if the string is accepted or raises KeyError"""
        s = initial_state
        ts = self.transitions
        for inp in inputs:
            s = ts[s][inp]
        return s

def automaton_growth_func( automaton, initial_state ):
    """Returns Z-transform of the growth function of this automaton
    Uses SYmpy for calculations"""
    from sympy import Symbol, Matrix, eye
    z = Symbol('z')
    
    n  = automaton.num_states()
    a = Matrix( [[0]*n]*n )
    for state, state_transitions in enumerate(automaton.transitions ):
        for new_state in state_transitions.values():
            a[new_state, state] = 1
    b = Matrix( n,1,[0]*n )
    b[initial_state] = 1

    c = Matrix( 1, n, [1]*n)

    #a.print_nonzero()
    
    #(z*eye(n)-a).inv().print_nonzero()  
    q = z*eye(n)-a
    f = c * q.LUsolve(b) * z
    #f = (c * q.adjugate() * b * z)/q.det()
    assert f.shape == (1,1)
    return f[0,0]
    #f_num = c * q.adjugate() * b
    #f_den = q.det() / z
    #assert f_num.shape == (1,1)
    #return f_num[0,0] / f_den

def make_2step_automaton( automaton ):
    """Make an automaton that accepts pairs of the inputs, accepted by the original automaton"""
    a1 = Automaton()
    for state, name in enumerate(automaton.state_names):
        state_ = a1.add_state(name)
        assert state_ == state

    for state, state_transitions in enumerate(automaton.transitions):
        for input1, state1 in state_transitions.items():
            for input2, state2 in automaton.transitions[state1].items():
                a1.add_transition( state, (input1, input2), state2 )
    return a1


def export_dot( automaton, dotfile ):
    def escape(s):
        return '"' + s.replace('"', '\\"') + '"'
    w = dotfile.write
    w("digraph{\n")
    for statename in automaton.state_names:
        w('  {};\n'.format(escape(statename)))

    for state, state_transitions in enumerate(automaton.transitions):
        for input, new_state in state_transitions.items():
            w('  {a} -> {b} [label={lbl}];\n'.format(
                a=escape(automaton.state_names[state]),
                b=escape(automaton.state_names[new_state]),
                lbl=escape(str(input))))
    w('}\n')

def build_accepting_automaton( alphabet, forbidden_suffices, suffix2name=str ):
    """Builds a finite automaton that accepts strings without any forbidden ones
    """
    def initials(s):
        for l in range(len(s)):
            yield s[:l]

    forbidden_set = set( tuple(seq) for seq in forbidden_suffices )

    states = set( tuple(pref)
                  for suffix in forbidden_suffices 
                  for pref in initials(suffix) 
    )
                

    #print ("FOrbidden:", forbidden_set)
    #print ("States:", states)
    state2index = {}
    automaton = Automaton()
    for state in states:
        state_name = suffix2name(state)
        state_index = automaton.add_state(state_name)
        state2index[state] = state_index
    
    #now encode transitions
    for state in states:
        state_index = state2index[state]
        for letter in alphabet:
            state1 = state + (letter,)
            #now truncate it, until it is either one of the alowed states,
            # or one of forbidden.
            while True:
                if state1 in forbidden_set:
                    #this state is forbidden.
                    break
                if state1 in states:
                    #allowed state found
                    #add a transition
                    automaton.add_transition( state_index, letter, state2index[state1] )
                    break
                #truncate head
                state1 = state1[1:]
    return automaton, state2index[()]
