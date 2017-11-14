# used some of the book code of Russell And Norvig's "Artificial Intelligence - A Modern Approach"
# https://github.com/aimacode/aima-python/blob/master/logic.py

import re

def find_if(predicate, seq):
    """If there is an element of seq that satisfies predicate; return it."""
    for x in seq:
        if predicate(x): return x
    return None


def every(predicate, seq):
    """True if every element of seq satisfies predicate."""

    for x in seq:
        if not predicate(x): return False
    return True


def isnumber(x):
    "Is x a number? We say it is if it has a __int__ method."
    return hasattr(x, '__int__')


def num_or_str(x):

    if isnumber(x): return x
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return str(x).strip()


def removeall_expr(item, seq):
    # remove all the items in tt_entails
    return [x for x in seq if not tt_entails(x, item)]


class Expr:
    def __init__(self, op, *args):
        # assert isinstance(op, str) or (isnumber(op) and not args)
        self.op = num_or_str(op)
        self.args = map(expr, args)

    def __call__(self, *args):
        assert is_symbol(self.op) and not self.args
        return Expr(self.op, *args)

    def __repr__(self):
        "Show something like 'P' or 'P(x, y)', or '~P' or '(P | Q | R)'"
        if len(self.args) == 0:  # Constant or proposition with arity 0
            return str(self.op)
        elif is_symbol(self.op):  # Functional or Propositional operator
            return '%s(%s)' % (self.op, ', '.join(map(repr, self.args)))
        elif len(self.args) == 1:  # Prefix operator
            return self.op + repr(self.args[0])
        else:  # Infix operator
            return '(%s)' % (' ' + self.op + ' ').join(map(repr, self.args))

    def __eq__(self, other):
        """x and y are equal iff their ops and args are equal."""
        return (other is self) or (isinstance(other, Expr)
                                   and self.op == other.op and self.args == other.args)

    def __hash__(self):
        "Need a hash method so Exprs can live in dicts."
        return hash(self.op) ^ hash(tuple(self.args))

    # See http://www.python.org/doc/current/lib/module-operator.html
    # Not implemented: not, abs, pos, concat, contains, *item, *slice
    def __lt__(self, other):
        return Expr('<', self, other)

    def __le__(self, other):
        return Expr('<=', self, other)

    def __ge__(self, other):
        return Expr('>=', self, other)

    def __gt__(self, other):
        return Expr('>', self, other)

    def __add__(self, other):
        return Expr('+', self, other)

    def __sub__(self, other):
        return Expr('-', self, other)

    def __and__(self, other):
        return Expr('&', self, other)

    def __div__(self, other):
        return Expr('/', self, other)

    def __truediv__(self, other):
        return Expr('/', self, other)

    def __invert__(self):
        return Expr('~', self)

    def __lshift__(self, other):
        return Expr('<<', self, other)

    def __rshift__(self, other):
        return Expr('>>', self, other)

    def __mul__(self, other):
        return Expr('*', self, other)

    def __neg__(self):
        return Expr('-', self)

    def __or__(self, other):
        return Expr('|', self, other)

    def __pow__(self, other):
        return Expr('**', self, other)

    def __xor__(self, other):
        return Expr('^', self, other)

    def __mod__(self, other):
        return Expr('<=>', self, other)  ## (x % y)


def expr(s):
    if isinstance(s, Expr): return s
    if isnumber(s): return Expr(s)

    s = s.replace('==>', '>>').replace('<==', '<<')
    s = s.replace('<=>', '%').replace('=/=', '^')
    s = re.sub(r'([a-zA-Z0-9_.]+)', r'Expr("\1")', s)
    return eval(s, {'Expr': Expr})


def is_symbol(s):
    "A string s is a symbol if it starts with an alphabetic char."
    return isinstance(s, str) and s[0].isalpha()


def is_var_symbol(s):
    "A logic variable symbol is an initial-lowercase string."
    return is_symbol(s) and s[0].islower()


def is_prop_symbol(s):
    """A proposition logic symbol is an initial-uppercase string other than
    TRUE or FALSE."""
    return is_symbol(s) and s[0].isupper() and s != 'TRUE' and s != 'FALSE'


def is_positive(s):
    """s is an unnegated logical expression
    # is_positive(expr('F(A, B)'))
    True
    # is_positive(expr('~F(A, B)'))
    False
    """
    return s.op != '~'


def is_negative(s):
    """s is a negated logical expression
    # is_negative(expr('F(A, B)'))
    False
    # is_negative(expr('~F(A, B)'))
    True
    """
    return s.op == '~'


def is_literal(s):
    """s is a FOL literal
    # is_literal(expr('~F(A, B)'))
    True
    # is_literal(expr('F(A, B)'))
    True
    # is_literal(expr('F(A, B) & G(B, C)'))
    False
    """
    return is_symbol(s.op) or (s.op == '~' and is_literal(s.args[0]))


def literals(s):
    """returns the list of literals of logical expression s.
    # literals(expr('F(A, B)'))
    [F(A, B)]
    # literals(expr('~F(A, B)'))
    [~F(A, B)]
    # literals(expr('(F(A, B) & G(B, C)) ==> R(A, C)'))
    [F(A, B), G(B, C), R(A, C)]
    """
    op = s.op
    if op in set(['&', '|', '<<', '>>', '%', '^']):
        result = []
        for arg in s.args:
            result.extend(literals(arg))
        return result
    elif is_literal(s):
        return [s]
    else:
        return []


def is_definite_clause(s):
    """returns True for exprs s of the form A & B & ... & C ==> D,
    where all literals are positive.  In clause form, this is
    ~A | ~B | ... | ~C | D, where exactly one clause is positive.
    # is_definite_clause(expr('Farmer(Mac)'))
    True
    # is_definite_clause(expr('~Farmer(Mac)'))
    False
    # is_definite_clause(expr('(Farmer(f) & Rabbit(r)) ==> Hates(f, r)'))
    True
    # is_definite_clause(expr('(Farmer(f) & ~Rabbit(r)) ==> Hates(f, r)'))
    False
    """
    op = s.op
    return (is_symbol(op) or
            (op == '>>' and every(is_positive, literals(s))))


TRUE, FALSE, ZERO, ONE, TWO = map(Expr, ['TRUE', 'FALSE', 0, 1, 2])
A, B, C, F, G, P, Q, x, y, z = map(Expr, 'ABCFGPQxyz')


def tt_entails(kb, alpha):
    """Use truth tables to determine if KB entails sentence alpha. [Fig. 7.10]
    # tt_entails(expr('P & Q'), expr('Q'))
    True
    """
    return tt_check_all(kb, alpha, prop_symbols(kb & alpha), {})


def tt_check_all(kb, alpha, symbols, model):
    "Auxiliary routine to implement tt_entails."
    if not symbols:
        if pl_true(kb, model):
            return pl_true(alpha, model)
        else:
            return True
        assert result != None
    else:
        P, rest = symbols[0], symbols[1:]
        return (tt_check_all(kb, alpha, rest, extend(model, P, True)) and
                tt_check_all(kb, alpha, rest, extend(model, P, False)))


def prop_symbols(x):
    "Return a list of all propositional symbols in x."
    # print x
    # print x.op
    # prop_symbols(expr('P & Q') & expr('Q'))
    # -> [P, Q]
    if not isinstance(x, Expr):
        return []
    elif is_prop_symbol(x.op):
        return [x]
    else:
        s = set(())
        for arg in x.args:
            for symbol in prop_symbols(arg):
                s.add(symbol)
        return list(s)


def tt_true(alpha):
    """Is the sentence alpha a tautology? (alpha will be coerced to an expr.)
    # tt_true(expr("(P >> Q) <=> (~P | Q)"))
    True
    """
    return tt_entails(TRUE, expr(alpha))


def pl_true(exp, model={}):
    """Return True if the propositional logic expression is true in the model,
    and False if it is false. If the model does not specify the value for
    every proposition, this may return None to indicate 'not obvious';
    this may happen even when the expression is tautological."""
    op, args = exp.op, exp.args
    if exp == TRUE:
        return True
    elif exp == FALSE:
        return False
    elif is_prop_symbol(op):
        # if is a  proposition logic symbol
        return model.get(exp)
    elif op == '~':
        p = pl_true(args[0], model)
        if p == None:
            return None
        else:
            return not p
    elif op == '|':
        result = False
        for arg in args:
            p = pl_true(arg, model)
            if p == True: return True
            if p == None: result = None
        return result
    elif op == '&':
        result = True
        for arg in args:
            p = pl_true(arg, model)
            if p == False: return False
            if p == None: result = None
        return result
    p, q = args

    # logical equivalence transformation
    if op == '>>':
        return pl_true(~p | q, model)
    elif op == '<<':
        return pl_true(p | ~q, model)
    pt = pl_true(p, model)
    if pt == None: return None
    qt = pl_true(q, model)
    if qt == None: return None
    if op == '<=>':
        return pt == qt
    elif op == '^':
        return pt != qt
    else:
        raise ValueError, "illegal operator in logic expression" + str(exp)


# ______________________________________________________________________________

## Convert to Conjunctive Normal Form (CNF)

def to_cnf(s):
    """Convert a propositional logical sentence s to conjunctive normal form.
    That is, of the form ((A | ~B | ...) & (B | C | ...) & ...) [p. 215]
    # to_cnf("~(B|C)")
    (~B & ~C)
    # to_cnf("B <=> (P1|P2)")
    ((~P1 | B) & (~P2 | B) & (P1 | P2 | ~B))
    # to_cnf("a | (b & c) | d")
    ((b | a | d) & (c | a | d))
    # to_cnf("A & (B | (D & E))")
    (A & (D | B) & (E | B))
    """
    if isinstance(s, str): s = expr(s)
    s = eliminate_implications(s)  # Steps 1, 2 from p. 215
    s = move_not_inwards(s)  # Step 3
    return distribute_and_over_or(s)  # Step 4


def eliminate_implications(s):
    """Change >>, <<, and <=> into &, |, and ~. That is, return an Expr
    that is equivalent to s, but has only &, |, and ~ as logical operators.
    # eliminate_implications(A >> (~B << C))
    ((~B | ~C) | ~A)
    """
    if not s.args or is_symbol(s.op): return s  ## (Atoms are unchanged.)
    args = map(eliminate_implications, s.args)
    a, b = args[0], args[-1]
    if s.op == '>>':
        return (b | ~a)
    elif s.op == '<<':
        return (a | ~b)
    elif s.op == '<=>':
        return (a | ~b) & (b | ~a)
    else:
        return Expr(s.op, *args)


def move_not_inwards(s):
    """Rewrite sentence s by moving negation sign inward.
    # move_not_inwards(~(A | B))
    (~A & ~B)
    # move_not_inwards(~(A & B))
    (~A | ~B)
    # move_not_inwards(~(~(A | ~B) | ~~C))
    ((A | ~B) & ~C)
    """
    if s.op == '~':
        NOT = lambda b: move_not_inwards(~b)
        a = s.args[0]
        if a.op == '~': return move_not_inwards(a.args[0])  # ~~A ==> A
        if a.op == '&': return NaryExpr('|', *map(NOT, a.args))
        if a.op == '|': return NaryExpr('&', *map(NOT, a.args))
        return s
    elif is_symbol(s.op) or not s.args:
        return s
    else:
        return Expr(s.op, *map(move_not_inwards, s.args))


def distribute_and_over_or(s):
    """Given a sentence s consisting of conjunctions and disjunctions
    of literals, return an equivalent sentence in CNF.
    # distribute_and_over_or((A & B) | C)
    ((A | C) & (B | C))
    """
    if s.op == '|':
        s = NaryExpr('|', *s.args)
        if len(s.args) == 0:
            return FALSE
        if len(s.args) == 1:
            return distribute_and_over_or(s.args[0])
        conj = find_if((lambda d: d.op == '&'), s.args)
        if not conj:
            return NaryExpr(s.op, *map(distribute_and_over_or, s.args))
        others = [a for a in s.args if a is not conj]
        if len(others) == 1:
            rest = others[0]
        else:
            rest = NaryExpr('|', *others)
        return NaryExpr('&', *map(distribute_and_over_or,
                                  [(c | rest) for c in conj.args]))
    elif s.op == '&':
        return NaryExpr('&', *map(distribute_and_over_or, s.args))
    else:
        return s


_NaryExprTable = {'&': TRUE, '|': FALSE, '+': ZERO, '*': ONE}


def NaryExpr(op, *args):
    """Create an Expr, but with an nary, associative op, so we can promote
    nested instances of the same op up to the top level.
    # NaryExpr('&', (A&B),(B|C),(B&C))
    (A & B & (B | C) & B & C)
    """
    arglist = []
    for arg in args:
        if arg.op == op:
            arglist.extend(arg.args)
        else:
            arglist.append(arg)
    if len(args) == 1:
        return args[0]
    elif len(args) == 0:
        return _NaryExprTable[op]
    else:
        return Expr(op, *arglist)


def conjuncts(s):
    """Return a list of the conjuncts in the sentence s.
    # conjuncts(A & B)
    [A, B]
    # conjuncts(A | B)
    [(A | B)]
    """
    if isinstance(s, Expr) and s.op == '&':
        return s.args
    else:
        return [s]


def disjuncts(s):
    """Return a list of the disjuncts in the sentence s.
    # disjuncts(A | B)
    [A, B]
    # disjuncts(A & B)
    [(A & B)]
    """
    if isinstance(s, Expr) and s.op == '|':
        return s.args
    else:
        return [s]


# DPLL-Satisfiable [Fig. 7.16]

def dpll_satisfiable(s):
    """Check satisfiability of a propositional sentence.
    (1) it returns a model rather than True when it succeeds; this is more useful. 
    (2) The function find_pure_symbol is passed a list of unknown clauses, rather
    than a list of all clauses and the model; this is more efficient.
    # ppsubst(dpll_satisfiable(A&~B))
    {A: True, B: False}
    # dpll_satisfiable(P&~P)
    False
    """
    clauses = conjuncts(to_cnf(s))
    #print clauses, "clauses"
    symbols = prop_symbols(s)
    #print symbols, "symbols"
    return dpll(clauses, symbols, {})


def dpll(clauses, symbols, model):
    "See if the clauses are true in a partial model."
    unknown_clauses = []
    for c in clauses:
        # print model,"model"
        val = pl_true(c, model)

        if val == False:
            return False
        if val != True:
            unknown_clauses.append(c)
    # when there's nothing in the symbols that can entail P: return model
    if len(unknown_clauses) == 0:
        return model
    P, value = find_pure_symbol(symbols, unknown_clauses)
    # print P, value, "find_pure_symbol"
    if P:
        '''
        def removeall_expr(item, seq):
            return [x for x in seq if not logic.tt_entails(x, item)]
        '''
        # remove all in symbols that can directly entail P
        # print symbols, removeall_expr(P, symbols)
        return dpll(clauses, removeall_expr(P, symbols), extend(model, P, value))
    P, value = find_unit_clause(clauses, model)
    # print P, value, "find_unit_clause"
    if P:
        return dpll(clauses, removeall_expr(P, symbols), extend(model, P, value))
    P = symbols.pop()
    return (dpll(clauses, symbols, extend(model, P, True)) or
            dpll(clauses, symbols, extend(model, P, False)))


def find_pure_symbol(symbols, unknown_clauses):
    """Find a symbol and its value if it appears only as a positive literal
    (or only as a negative) in clauses.
    # find_pure_symbol([A, B, C], [A|~B,~B|~C,C|A])
    (A, True)
    """
    for s in symbols:
        # print s
        found_pos, found_neg = False, False
        for c in unknown_clauses:
            # print c
            if not found_pos and s in disjuncts(c): found_pos = True
            if not found_neg and ~s in disjuncts(c): found_neg = True
        if found_pos != found_neg:
            return s, found_pos
    return None, None


def find_unit_clause(clauses, model):
    """A unit clause has only 1 variable that is not bound in the model.
    # find_unit_clause([A|B|C, B|~C, A|~B], {A:True})
    (B, False)
    """
    for clause in clauses:
        num_not_in_model = 0
        some_true = False
        for literal in disjuncts(clause):
            sym = literal_symbol(literal)
            # print sym,"sym"
            if sym not in model:
                num_not_in_model += 1
                # print num_not_in_model,"num"
                P, value = sym, (literal.op != '~')

            elif pl_true(literal, model):
                some_true = True
                break
        if (num_not_in_model == 1) and (not some_true):
            return P, value
    return None, None


def literal_symbol(literal):
    """The symbol in this literal (without the negation).
    # literal_symbol(P)
    P
    # literal_symbol(~P)
    P
    """
    if literal.op == '~':
        return literal.args[0]
    else:
        return literal


def extend(s, var, val):
    """Copy the substitution s and extend it by setting var to val;
    return copy.

    # ppsubst(extend({x: 1}, y, 2))
    {x: 1, y: 2}
    """
    s2 = s.copy()
    s2[var] = val
    return s2


# test code
'''
print prop_symbols(expr('P & Q') & expr('Q'))
print find_unit_clause([A | B | C, B | ~C, A | ~B], {B: True})
print tt_check_all(expr('P & Q'), expr('Q'), [P, Q], {})
print dpll_satisfiable(A & ~B)
'''

