import unittest
from knuth_bendix import shortLex, overlap, splitBy

class TestComparatros(unittest.TestCase):
    def test_shortlex(self):
        
        self.assertTrue( shortLex( "", "a") )
        self.assertTrue( shortLex( "", "") )
        self.assertTrue( shortLex( "a", "a") )
        self.assertTrue( shortLex( "a", "a") )
        
        self.assertTrue( shortLex( "a", "bb") )
        self.assertTrue( shortLex( "a", "b") )
        self.assertFalse( shortLex( "bb", "a") )
        

class TestSplits(unittest.TestCase):

    def assertOverlap(self, s1, s2, x, y, z):
        self.assertEqual( overlap(tuple(s1), tuple(s2)),
                          (tuple(x), tuple(y), tuple(z)))

    def assertSplit(self, s1, s2, hasSplit, x, z):
        self.assertEqual( splitBy(tuple(s1), tuple(s2)),
                          (hasSplit,
                           tuple(x) if x is not None else None,
                           tuple(z) if z is not None else None))
    def test_split(self):
        self.assertSplit( "123456", "34",
                          True, "12", "56" )
        self.assertSplit( "123456", "35",
                          False, None, None )
        self.assertSplit( "123456", "123456",
                          True, (), () )
        self.assertSplit( "123456", "456",
                          True, "123", "" )
        
    def test_overlap(self):

        self.assertOverlap("123", "234", "1","23", "4") 
        self.assertOverlap("123", "1234", "","123", "4") 
        self.assertOverlap("123", "123", "","123", "") 
        self.assertOverlap("1123", "2345", "11","23", "45")
        self.assertOverlap("1123", "22345", "1123","", "22345")


