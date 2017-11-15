
import time

from logicalExpr import dpll_satisfiable, expr


def neighbors(i, j):
    li = set()
    if (i - 1) in range(4):
        li.add((i - 1, j))
    if (i + 1) in range(4):
        li.add((i + 1, j))
    if (j - 1) in range(4):
        li.add((i, j - 1))
    if (j + 1) in range(4):
        li.add((i, j + 1))
    return li


class KnowledgeBase():

    def __init__(self):
        self.k = expr('~P00 & ~W00')

        l = []
        for i in range(4):
            for j in range(4):
                for fringe, death in (('B', 'P'), ('S', 'W')):
                    left = "%s%s%s" % (fringe, i, j)
                    right_list = []
                    for s, t in neighbors(i, j):
                        right_list.append("%s%s%s" % (death, s, t))

                    
                    l.append("(%s <=> (%s))" % \
                              (left, ' | '.join(right_list)))
        '''
        FACTS SETTING UP :
        Step1:
        ~P(0,0) & ~W(0,0) ==True
        B(0,0) <=> P(0,1) | P(1,0) 
        S(0,0) <=> W(0,1) | W(1,0) 
        B(0,1) <=> P(0,0) | P(1,1) | P(0,2) 
        S(0,1) <=> W(0,0) | W(1,1) | W(0,2) 
        B(0,2) <=> P(1,2) | P(0,1) | P(0,3) 
        S(0,2) <=> W(1,2) | W(0,1) | W(0,3) 
        B(0,3) <=> P(1,3) | P(0,2) 
        S(0,3) <=> W(1,3) | W(0,2)
        B(1,0) <=> P(2,0) | P(0,0) | P(1,1) 
        S(1,0) <=> W(2,0) | W(0,0) | W(1,1) 
        B(1,1) <=> P(0,1) | P(1,2) | P(1,0) | P(2,1)
        S(1,1) <=> W(0,1) | W(1,2) | W(1,0) | W(2,1) 
        B(1,2) <=> P(1,1) | P(1,3) | P(0,2) | P(2,2) 
        S(1,2) <=> W(1,1) | W(1,3) | W(0,2) | W(2,2) 
        B(1,3) <=> P(1,2) | P(0,3) | P(2,3) 
        S(1,3) <=> W(1,2) | W(0,3) | W(2,3) 
        B(2,0) <=> P(3,0) | P(1,0) | P(2,1) 
        S(2,0) <=> W(3,0) | W(1,0) | W(2,1) 
        B(2,1) <=> P(2,0) | P(3,1) | P(1,1) | P(2,2) 
        S(2,1) <=> W(2,0) | W(3,1) | W(1,1) | W(2,2) 
        B(2,2) <=> P(1,2) | P(3,2) | P(2,3) | P(2,1) 
        S(2,2) <=> W(1,2) | W(3,2) | W(2,3) | W(2,1) 
        B(2,3) <=> P(1,3) | P(3,3) | P(2,2) 
        S(2,3) <=> W(1,3) | W(3,3) | W(2,2) 
        B(3,0) <=> P(2,0) | P(3,1) 
        S(3,0) <=> W(2,0) | W(3,1) 
        B(3,1) <=> P(3,0) | P(3,2) | P(2,1) 
        S(3,1) <=> W(3,0) | W(3,2) | W(2,1) 
        B(3,2) <=> P(3,1) | P(3,3) | P(2,2) 
        S(3,2) <=> W(3,1) | W(3,3) | W(2,2)
        B(3,3) <=> P(3,2) | P(2,3) 
        S(3,3) <=> W(3,2) | W(2,3) 
        ......
        
        '''

        rule = expr(' & '.join(l))
        self.addRules(rule)

        # FACTS SETTING UP :
        # Step 2:

        # must have one wumpus
        l = ['W%s%s' % (i, j) for i in range(4) for j in range(4)]
        rule = expr(' | '.join(l))
        self.addRules(rule)

        # And only one wumpus
        # make sure every (~W%s%s | ~W%s%s)==True
        l = ['(~W%s%s | ~W%s%s)' % \
              (i, j, x, y)
              for i in range(4) \
              for j in range(4) \
              for x in range(4) \
              for y in range(4) \
              if not ((i == x) and (j == y))]
        rule = expr(' & '.join(l))
        self.addRules(rule)

    def addRules(self, s):
        self.k = self.k & s

    def ask(self, s):
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "  waiting for result from knowledge base...  "
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "checking ", s
        start = time.time()

        res = dpll_satisfiable(self.k & ~s)
        print "time elasped: ", time.time() - start
        if res is False:
            return True
        else:
            return False


# test code
'''
w=KnowledgeBase()
w.ask(expr("(P12 | W12)"))
w.ask(expr("(~P12 | ~W22)"))
'''

