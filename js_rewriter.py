#Generates JS code that effectively rewrites

import sys
sys.path.append(r"d:\dmishin\prog\knuth-bendix")
sys.path.append(r"../../Prog/knuth_bendix")

from vondyck import *
from knuth_bendix import *

def groupPowers( elemsWithPowers ):
    """ List (elem, power::int) -> List (elem, power::int)"""
    grouped = []
    for elem, power in elemsWithPowers:
        if not grouped:
            grouped.append( (elem, power) )
        elif grouped[-1][0] == elem:
            newPower = grouped[-1][1] + power
            if newPower != 0:
                grouped[-1] = (elem, newPower)
            else:
                grouped.pop()
        else:
            grouped.append( (elem, power) )
    return grouped

__doc__ = """
Every string is a sequence of powers of 2 operators: A and B.
powers are limited to be in range -n/2 ... n/2 and -m/2 ... m/2


rewrite rules work on these pow cahins:


Trivial rewrites:
   a^-1 a       -> e
   b^-1 b       -> e
   a a^-1       -> e
   b b^-1       -> e

Power modulo rewrites.
   b^2  -> b^-2
   b^-3 -> b
   #allower powers: -2, -1, 1
   #rewrite rule: (p + 2)%4-2

   a^2  -> a^-2
   a^-3 -> a
   #allower powers: -2, -1, 1
   #rewrite rule: (p+2)%4-2

Non-trivial rewrites
 Ending with b
   a b  -> b^-1 a^-1
   b^-1 a^-1 b^-1       -> a       *
   a b^-2       -> b^-1 a^-1 b     *
   b a^-1 b^-1  -> b^-2 a          *

 Ending with a
   b a  -> a^-1 b^-1
   a^-1 b^-1 a^-1       -> b       *
   a b^-1 a^-1  -> a^-2 b          *
   b a^-2       -> a^-1 b^-1 a     *


As a tree, sorted in reverse order. Element in square braces is "eraser" for the last element in the matching pattern.

- Root B
  - b^-2   
    - a       REW: [a^-1] b^-1 a^-1 b
  - b^-1
    - a^-1
       - b    REW: [b^-1] b^-2 a
       - b^-1 REW: [b] a
  - b
    - a       REW: [a^-1] b^-1 a^-1

- Root A
  - a^-2 
    - b       REW: [b^-1] a^-1 b^-1 a
  - a^-1
    - b^-1
       - a    REW: [a^-1] a^-2 b
       - a^-1 REW: [a] b
  - a
    - b       REW: [b^-1] a^-1 b^-1
   
Idea: 2 rewriters. For chains ending with A and with B.
Chains are made in functional style, stored from end. 


See sample_rewriter.js for working code.
    
"""


declarations = """
var NodeA = function NodeA( p, tail ){ this.p = p; this.t=tail; };
var NodeB = function NodeB( p, tail ){ this.p = p; this.t=tail; };

NodeA.prototype.letter = "a";
NodeB.prototype.letter = "b";

exports.chainEquals = chainEquals = function chainEquals(a, b){
    if (a===null || b==null) return (a===null) && (b===null);
    return (a.letter === b.letter) && (a.p === b.p) && chainEquals(a.t, b.t);
};
var showNode = exports.showNode = function showNode(node){
    if (node === null){
	return "";
    }else{
	return showNode(node.t) + node.letter + ((node.p==1)?"":("^"+node.p));
    }
};

var nodeConstructors = {a: NodeA, b: NodeB};

exports.NodeA = NodeA;
exports.NodeB = NodeB;
exports.nodeConstructors = nodeConstructors;

exports.appendSimple = appendSimple = function appendSimple(chain, stack){
    while (stack.length > 0){
        var _ep = stack.pop();
        var e=_ep[0], p=_ep[1];
        chain = new nodeConstructors[e](p, chain);
    }
    return chain;
};


//function mod( x, n ){ return (x%n+n)%n; };
"""


from contextlib import contextmanager

otherElem = {'a':'b', 'b':'a'}.get

class JsCodeGenerator:
    def __init__( self, out, debug=True, pretty=True ):
        self.out = out
        self.ident = 0
        self.debug = debug
        self.pretty = pretty
        
    def line(self, text):
        if not self.debug and text.startswith("console.log"):
            return
        
        if not self.pretty and text.startswith("//"):
            return
        
        if self.pretty or "//" in text:
            self.out.write("    "*self.ident)
            
        self.out.write(text)
        self.out.write("\n" if self.pretty else " ")
        
    @contextmanager
    def block(self):
        self.line("{")
        self.ident += 1
        yield
        self.ident -= 1
        self.line("}")
    
class CodeGenerator(JsCodeGenerator):
    def __init__( self, rewriteTable, out, debug=True, pretty=True ):
        JsCodeGenerator.__init__(self, out, debug=debug, pretty=pretty)
        self.rewriteTable = rewriteTable
        self.suffixTree = reverseSuffixTable(rewriteTable)
        
    def generate(self):
        self.out.write(declarations)
    
        self.line("var appendRewrite = function appendRewrite( chain, stack )")
        with self.block():
            self.line("while( stack.length > 0)")
            with self.block():
                self.line("var _e = stack.pop();");
                self.line("var element = _e[0], power = _e[1];");
                self.line("if (chain === null)")
                with self.block():
                    self.line("//empty chain")
                    self.line('console.log("Append to empth chain:"+_e);');
                    self.line('var order=(element==="a")?{orderA}:{orderB};'\
                              .format(orderA = self._nodeOrder('a'),
                                      orderB = self._nodeOrder('b')))
                    self.line('var lowestPow=(element==="a")?{lpowA}:{lpowB};'\
                              .format(lpowA = self._lowestPower('a'),
                                      lpowB = self._lowestPower('b')))
                    
                    self.line('chain = new nodeConstructors[element](((power - lowestPow)%order+order)%order+lowestPow, chain);')
                self.generateMain()
            self.line("return chain;")
        self.line(";")
                
    def generateMain(self):
        self.line('else if (chain.letter==="a")')
        with self.block():
            self.line('console.log("Append to chain ending with A:"+_e);')
            self.generatePowerAccumulation("a")
            self.generateRewriterFrom("b")
            
        self.line('else if (chain.letter==="b")')
        with self.block():
            self.line('console.log("Append to chain ending with B:"+_e);')
            self.generatePowerAccumulation("b")
            self.generateRewriterFrom("a")
            
        self.line('else throw new Error("Chain neither a nor b?");')

    def generatePowerAccumulation(self, letter):
        self.line('if (element == "{letter}")'.format(letter=letter))
        with self.block():
            self.line( 'console.log("    element is {letter}");'.format(**locals()))
            self.line( 'var newPower = ((chain.p + power - {lowestPow})%{order}+{order})%{order}+{lowestPow};'\
                       .format(lowestPow=self._lowestPower(letter), order = self._nodeOrder(letter)))
            
            self.line('if (newPower === 0)')
            with self.block():
                self.line( 'console.log("      power reduced to 0, new chain="+showNode(chain));')
                self.line( 'chain = chain.t;')
            self.line('else')
            with self.block():
                self.line('chain = new {nodeClass}(newPower, chain.t);'.format(nodeClass=self._nodeClass(letter)))
                
    def generateRewriterFrom(self, newElement):
        """Generate rewriters, when `newElement` is added, and it is not the same as the last element of the chain"""
        self.line("else")
        with self.block():
            self.line("//Non-trivial rewrites, when new element is {newElement}".format(**locals()))
            self.line("chain = new {nodeConstructor}(power, chain);".format(nodeConstructor=self._nodeClass(newElement)))
            self.generateRewriteBySuffixTree(newElement, self.suffixTree, 'chain')
            
    def generateRewriteBySuffixTree(self, newElement, suffixTree, chain):

        first = True
        for (elem, elemPower), subTable in sorted( suffixTree.items() ):
            if elem != newElement: continue
            
            if not first:
                self.line("else")
            else:
                first = False
            isLeaf = "rewrite" in subTable
            if isLeaf:
                compOperator = "<=" if elemPower < 0 else ">="
                self.line( '//reached suffix: {suf}'.format(suf = subTable["original"]))
                self.line( 'if ({chain}.p{compOperator}{elemPower})'.format(**locals()))

                with self.block():
                    self.generateLeafRewrite(elem, elemPower, subTable["rewrite"], chain)
                    
            else:
                self.line("if ({chain}.p == {elemPower})".format(**locals()))
                with self.block():
                    self.line("if ({chain}.t)".format(**locals()))
                    with self.block():
                        self.generateRewriteBySuffixTree( otherElem(newElement), subTable, chain+".t")

        
    def generateLeafRewrite(self, elem, elemPower, rewrite, chain):
        self.line("//Leaf: rewrite this to {rewrite}".format(**locals()))
        self.line("//Truncate chain...")
        self.line("chain = {chain};".format(**locals()))
        self.line("//Append rewrite")
        self.line("stack.push(" + \
                  ", ".join( '["{e}", {p}]'.format(e=e,p=p)
                             for e, p in groupPowers(rewrite[::-1]+[(elem, -elemPower)]) ) +\
                  ");")
        
    def _nodeClass(self, letter):
        return "Node"+letter.upper()


        
    def _powerRewriteRules(self):
        for key, rewrite in self.rewriteTable.items():
            gKey = list(groupPowersVd(key))
            gRewrite = list(groupPowersVd(rewrite))
            if len(gKey) == 1 and len(gRewrite) == 1:
                x, p = gKey[0]
                x_, p1 = gRewrite[0]
                if x == x_:
                    yield x, p, p1


    def _lowestPower(self, letter):
        """search for rules of type a^n -> a^m"""
        v = min( (p1, p2) for x, p1, p2 in self._powerRewriteRules()
                 if x == letter)
        p1, p2 = v 
        return p1 + 1
    
        
    def _nodeOrder(self, letter):
        p1, p2 = min( (p1, p2) for x, p1, p2 in self._powerRewriteRules()
                      if x == letter)
        return abs(p2 - p1)

    def generateRewriterTest(self, source, expected):
        gSource, gExpected = map(groupPowersVd, [source, expected])
        def seq2js(s):
            return "[" + ",".join('["{e}",{p}]'.format(e=e,p=p)
                                  for e,p in list(s)[::-1]) + "]"            
        self.line("(function()")
        with self.block():
            
            self.line("var result = appendRewrite( null, {sourceText});".format(sourceText = seq2js(gSource)))
            self.line("var expected = appendSimple( null, {expectedText});".format(expectedText = seq2js(gExpected)))
            self.line("if (chainEquals(result, expected))")
            with self.block():
                self.line('console.log("Test {source}->{expected} passed");'.format(**locals()))
            self.line("else")
            with self.block():
                self.line('console.log("Test {source}->{expected} failed");'.format(**locals()))
                self.line('console.log("   expected result:"+showNode(expected));')
                self.line('console.log("   received result:"+showNode(result));')
        self.line(")();")


def reverseSuffixTable(ruleset, ignorePowers = True):
    revTable = {}
    
    for suffix, rewrite in ruleset.items():
        gSuffix = list(groupPowersVd(suffix))
        gRewrite = list(groupPowersVd(rewrite))

        if ignorePowers:
            if len(gSuffix)== 1 and len(gRewrite)==1 and gSuffix[0][0] == gRewrite[0][0]:
                continue
            if len(gSuffix) == 2 and len(gRewrite)==0:
                continue
        
        table = revTable
        for e_p in gSuffix[::-1]:
            if e_p in table:
                table = table[e_p]
            else:
                table1 = {}
                table[e_p] = table1
                table = table1
        table["rewrite"] = gRewrite
        table["original"] = gSuffix
    return revTable
        
if __name__=="__main__":
    import sys
    table = {('b', 'a'): ('A', 'B'), ('b', 'B'): (), ('B', 'A', 'B'): ('a',), ('B', 'B', 'B'): ('b',), ('B', 'b'): (), ('a', 'B', 'B'): ('B', 'A', 'b'), ('A', 'B', 'A'): ('b',), ('A', 'A', 'A'): ('a',), ('A', 'a'): (), ('b', 'A', 'A'): ('A', 'B', 'a'),
 ('a', 'b'): ('B', 'A'), ('a', 'B', 'A'): ('A', 'A', 'b'), ('b', 'A', 'B'): ('B', 'B', 'a'), ('b', 'b'): ('B', 'B'), ('a', 'A'): (), ('a', 'a'): ('A', 'A')}
    s = RewriteRuleset(table)

    with open("js_rewriter_gen.js", "w") as ofile:
        g = CodeGenerator(s, ofile,
                          #debug=False, pretty=False
        )
        g.debug=False
        g.generate()
        
        g.debug=True
        g.line("console.log('============================');")
        for s, t in table.items():
            g.generateRewriterTest(s,t)
            
#        ofile.write("""\
# console.log(showNode(appendRewrite( null, [['a',1], ['b',1]])));
#        """)
    #print (reverseSuffixTable (s))
    import os
    os.system("node js_rewriter_gen.js")
    
    
