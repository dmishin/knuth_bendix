import unittest
from automaton import *

class TestAutomaton(unittest.TestCase):
    def test_empty(self):
        a = Automaton()
        s1,s2,s3 = map(a.add_state, '123')
        
        self.assertEqual(a.state_names[s1], '1')
        self.assertEqual(a.state_names[s2], '2')
        self.assertEqual(a.state_names[s3], '3')
        with self.assertRaises(KeyError):
            a.next(s1, 1)

    def test_simple(self):
        a = Automaton()
        s1,s2,s3 = map(a.add_state, '123')
        a.add_transition(s1, 1, s2)
        a.add_transition(s2, 1, s3)
        a.add_transition(s3, 1, s1)
        
        self.assertEqual(a.next(s1,1), s2)
        self.assertEqual(a.next(s2,1), s3)
        self.assertEqual(a.next(s3,1), s1)

    def test_accept_seq(self):
        a = Automaton()
        s1,s2,s3 = map(a.add_state, '123')
        a.add_transition(s1, 1, s2)
        a.add_transition(s2, 1, s3)
        a.add_transition(s3, 1, s1)
        a.add_transition(s3, 2, s2)


        self.assertEqual(a.accept_seq(s1, [1,1,1,1,1]), s3)
        self.assertEqual(a.accept_seq(s1, [1,1,2]), s2)
        self.assertEqual(a.accept_seq(s1, [1,1,2,1]), s3)

        with self.assertRaises(KeyError):
            a.accept_seq(s1, [1,2])
        with self.assertRaises(KeyError):
            a.accept_seq(s1, [2,1])
