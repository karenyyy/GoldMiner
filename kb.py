
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


class WumpusKnowledgeBase():
    """KnowledgeBase for wumpus world"""

    def __init__(self):
        self.k = expr('~P00 & ~W00')

        li = []
        for i in range(4):
            for j in range(4):
                for fringe, death in (('B', 'P'), ('S', 'W')):
                    left = "%s%s%s" % (fringe, i, j)

                    '''
                    left_list:
                    B00
                    S00
                    B01
                    S01
                    B10
                    S10
                    B11
                    S11
                    ......

                    '''
                    right_list = []
                    for s, t in neighbors(i, j):
                        right_list.append("%s%s%s" % (death, s, t))

                    '''
                    FACTS SETTING UP :
                    STEP 1:
                    self.pos, [all possible situations that could be encountered in its neighboring spots]

                    B00  ['PXX']        XX be the neighbors of (0,0)
                    S00  ['PXX', 'WXX',...]         XX be the neighbors of (0,0)
                    B01  ['PXX', 'WXX',...]         XX be the neighbors of (0,1)
                    S01  ['PXX', 'WXX',...]         ...
                    B10  ['PXX', 'WXX',...]         ...
                    S10  ['PXX', 'WXX',...]         ...
                    ......
                    '''
                    li.append("(%s <=> (%s))" % \
                              (left, ' | '.join(right_list)))

        rule = expr(' & '.join(li))
        self.addRules(rule)

        # FACTS SETTING UP :
        # STEP 2:

        # must have one wumpus
        li = ['W%s%s' % (i, j) for i in range(4) for j in range(4)]
        rule = expr(' | '.join(li))
        self.addRules(rule)

        # And only one wumpus
        # make sure every (~W%s%s | ~W%s%s)==True
        li = ['(~W%s%s | ~W%s%s)' % \
              (i, j, x, y)
              for i in range(4) \
              for j in range(4) \
              for x in range(4) \
              for y in range(4) \
              if not ((i == x) and (j == y))]
        rule = expr(' & '.join(li))
        self.addRules(rule)

    def addRules(self, s):
        self.k = self.k & s

    def ask(self, s):
        print "===================="
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
w=WumpusKnowledgeBase()
w.ask(expr("(P12 | W12)"))
w.ask(expr("(~P12 | ~W22)"))
'''

