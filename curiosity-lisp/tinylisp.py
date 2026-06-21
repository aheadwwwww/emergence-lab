"""
tinylisp.py — A Lisp interpreter in under 100 lines of Python

Based on Peter Norvig's lis.py (http://norvig.com/lispy.html).
Core: 4 special forms (quote, if, define, lambda) + procedure calls.
"""

import math, operator as op
from collections import ChainMap

Symbol = str
List = list
Number = (int, float)


class Proc:
    """User-defined Scheme procedure with lexical closure."""
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args):
        return eval(self.body, ChainMap(dict(zip(self.parms, args)), self.env))


def env_builtins():
    """Create environment with built-in procedures."""
    e = {}
    e.update(vars(math))
    e.update({
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        '>': op.gt, '<': op.lt, '=': op.eq,
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x, y: [x] + y,
        'list': lambda *x: list(x),
        'length': len,
        'null?': lambda x: x == [],
        'not': op.not_,
        'eq?': op.is_,
        'equal?': op.eq,
        'begin': lambda *x: x[-1],
        'display': print,
    })
    return e


def tokenize(s):
    return s.replace('(', ' ( ').replace(')', ' ) ').split()


def parse(tokens):
    """Read one expression from token list. Returns nested Python list."""
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(parse(tokens))
        tokens.pop(0)
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return Symbol(token)


def eval(x, env):
    """The heart: evaluate an expression in an environment."""
    if isinstance(x, Symbol):       # variable reference
        return env[x]
    elif not isinstance(x, List):   # self-evaluating (number)
        return x
    elif x[0] == 'quote':           # (quote exp)
        return x[1]
    elif x[0] == 'if':             # (if test conseq alt)
        return eval(x[2] if eval(x[1], env) else x[3], env)
    elif x[0] == 'define':         # (define var exp)
        env[x[1]] = eval(x[2], env)
    elif x[0] == 'lambda':         # (lambda (var...) body)
        return Proc(x[1], x[2], env)
    elif x[0] == 'let':            # (let ((var val)...) body)
        new_env = ChainMap(dict((var, eval(val, env)) for var, val in x[1]), env)
        return eval(x[2], new_env)
    elif x[0] == 'set!':           # (set! var val) — mutate existing binding
        env[x[1]] = eval(x[2], env)
    else:                           # (proc arg...)
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)


def to_string(exp):
    """Convert Python object to Lisp-readable string."""
    if isinstance(exp, list):
        return '(' + ' '.join(map(to_string, exp)) + ')'
    return str(exp)


def repl(prompt='tl> '):
    """Read-Eval-Print Loop."""
    env = ChainMap({}, env_builtins())
    while True:
        try:
            s = input(prompt)
            if s.strip().lower() in ('exit', 'quit'):
                break
            val = eval(parse(tokenize(s)), env)
            if val is not None:
                print(to_string(val))
        except (SyntaxError, NameError, TypeError, ZeroDivisionError, IndexError) as e:
            print(f'Error: {e}')
        except (EOFError, KeyboardInterrupt):
            print()
            break


# ─── Demo: run some Lisp code ───

if __name__ == '__main__':
    test_code = [
        "(+ 1 2)",
        "(* 3 (+ 4 5))",
        "(quote (a b c))",
        "'(a b c)",       # quote shorthand isn't supported, use (quote (a b c))
        "(define square (lambda (x) (* x x)))",
        "(square 5)",
        "(define fact (lambda (n) (if (< n 2) 1 (* n (fact (- n 1))))))",
        "(fact 5)",
        "(define fib (lambda (n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2))))))",
        "(fib 10)",
        "(let ((x 3)) (+ x 1))",
        "(car (quote (1 2 3)))",
        "(cdr (quote (1 2 3)))",
        "(list 1 2 3)",
    ]

    print("=== tinylisp test ===")
    env = ChainMap({}, env_builtins())
    for code in test_code:
        try:
            result = eval(parse(tokenize(code)), env)
            print(f"  {code:40s} => {to_string(result)}")
        except Exception as e:
            print(f"  {code:40s} => ERROR: {e}")

    print()
    print("Architecture: 4 special forms + procedure calls")
    print("  parse: tokenize → s-expression (nested Python lists)")
    print("  eval:  Symbol→lookup | List→special/call | else→self")
    import os
print(f"  Total: ~{sum(1 for _ in open(os.path.abspath(__file__), 'r', encoding='utf-8'))} lines")
