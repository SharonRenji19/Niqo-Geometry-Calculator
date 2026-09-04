"""
Geometric Calculator REPL.

Grammar (recursive-descent, precedence low -> high):

    statement := NAME '=' expr | expr
    expr      := term (('+' | '-') term)*
    term      := factor (('*' | '/') factor)*
    factor    := NUMBER | '(' expr ')' | call_chain
    call_chain:= NAME ( '(' arglist? ')' )? ( '.' NAME '(' arglist? ')' )*
    arglist   := expr (',' expr)*

A bare NAME with no '(' after it is a variable lookup; a NAME immediately
followed by '(' is treated as a shape constructor (Point, Line, ...).
"""

import re

from shapes.point import Point
from shapes.line import Line
from shapes.circle import Circle

CLASSES = {"Point": Point, "Line": Line, "Circle": Circle}

_TOKEN_RE = re.compile(
    r"""
    \s*(?:
        (?P<NUMBER>-?\d+\.?\d*)
      | (?P<NAME>[A-Za-z_][A-Za-z0-9_]*)
      | (?P<OP>[=(),.]|\+|-|\*|/)
    )
    """,
    re.VERBOSE,
)


class Token:
    __slots__ = ("kind", "value")

    def __init__(self, kind: str, value: str):
        self.kind = kind
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.kind}, {self.value!r})"


def tokenize(line: str) -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    while pos < len(line):
        match = _TOKEN_RE.match(line, pos)
        if not match or match.end() == pos:
            if line[pos:].strip() == "":
                break
            raise SyntaxError(f"Unexpected character {line[pos]!r} at position {pos}")
        pos = match.end()
        kind = match.lastgroup
        tokens.append(Token(kind, match.group(kind)))
    return tokens


class Parser:
    def __init__(self, tokens: list[Token], env: dict):
        self.tokens = tokens
        self.pos = 0
        self.env = env

    def _peek(self) -> Token | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _advance(self) -> Token:
        tok = self._peek()
        if tok is None:
            raise SyntaxError("Unexpected end of input")
        self.pos += 1
        return tok

    def _expect(self, value: str) -> Token:
        tok = self._peek()
        if tok is None or tok.value != value:
            raise SyntaxError(f"Expected '{value}', got {tok.value if tok else 'end of input'}")
        return self._advance()

    def parse_statement(self):
        """Returns (assigned_name_or_None, resulting_value)."""
        is_assignment = (
            self._peek() is not None
            and self._peek().kind == "NAME"
            and self.pos + 1 < len(self.tokens)
            and self.tokens[self.pos + 1].value == "="
        )
        if is_assignment:
            name = self._advance().value
            self._expect("=")
            value = self.parse_expr()
            if self._peek() is not None:
                raise SyntaxError(f"Unexpected trailing input near {self._peek().value!r}")
            self.env[name] = value
            return name, value

        value = self.parse_expr()
        if self._peek() is not None:
            raise SyntaxError(f"Unexpected trailing input near {self._peek().value!r}")
        return None, value

    def parse_expr(self):
        value = self.parse_term()
        while self._peek() and self._peek().value in ("+", "-"):
            op = self._advance().value
            rhs = self.parse_term()
            value = self._apply_add_sub(value, rhs, op)
        return value

    def parse_term(self):
        value = self.parse_factor()
        while self._peek() and self._peek().value in ("*", "/"):
            op = self._advance().value
            rhs = self.parse_factor()
            value = self._apply_mul_div(value, rhs, op)
        return value

    def parse_factor(self):
        tok = self._peek()
        if tok is None:
            raise SyntaxError("Unexpected end of input")
        if tok.kind == "NUMBER":
            self._advance()
            return float(tok.value)
        if tok.value == "(":
            self._advance()
            value = self.parse_expr()
            self._expect(")")
            return value
        if tok.kind == "NAME":
            return self.parse_call_chain()
        raise SyntaxError(f"Unexpected token {tok.value!r}")

    def parse_call_chain(self):
        name = self._advance().value

        if self._peek() and self._peek().value == "(":
            if name not in CLASSES:
                raise NameError(f"Unknown shape type '{name}'")
            args = self.parse_arglist()
            try:
                value = CLASSES[name](*args)
            except TypeError as exc:
                raise TypeError(f"{name}(...): {exc}") from None
        else:
            if name not in self.env:
                raise NameError(f"Undefined variable '{name}'")
            value = self.env[name]

        while self._peek() and self._peek().value == ".":
            self._advance()
            if self._peek() is None or self._peek().kind != "NAME":
                raise SyntaxError("Expected method name after '.'")
            method_name = self._advance().value
            args = self.parse_arglist()
            if not hasattr(value, method_name) or method_name.startswith("_"):
                raise AttributeError(
                    f"{type(value).__name__} object has no method '{method_name}'"
                )
            value = getattr(value, method_name)(*args)

        return value

    def parse_arglist(self):
        self._expect("(")
        args = []
        if self._peek() and self._peek().value != ")":
            args.append(self.parse_expr())
            while self._peek() and self._peek().value == ",":
                self._advance()
                args.append(self.parse_expr())
        self._expect(")")
        return args

    @staticmethod
    def _apply_add_sub(lhs, rhs, op):
        # Numeric arithmetic only; shapes don't support +/- in this version.
        if not isinstance(lhs, (int, float)) or not isinstance(rhs, (int, float)):
            raise TypeError(f"Unsupported operand types for '{op}'")
        return lhs + rhs if op == "+" else lhs - rhs

    @staticmethod
    def _apply_mul_div(lhs, rhs, op):
        if not isinstance(lhs, (int, float)) or not isinstance(rhs, (int, float)):
            raise TypeError(f"Unsupported operand types for '{op}'")
        if op == "/":
            if rhs == 0:
                raise ZeroDivisionError("division by zero")
            return lhs / rhs
        return lhs * rhs


def format_result(value) -> str:
    if isinstance(value, float):
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.10g}"
    return repr(value)


def evaluate_line(line: str, env: dict) -> str | None:
    """Tokenize + parse + evaluate one input line. Returns the text to print, or None."""
    tokens = tokenize(line)
    if not tokens:
        return None
    name, value = Parser(tokens, env).parse_statement()
    if name is not None:
        return f"{name}{format_result(value)}"
    return format_result(value)


def run_repl() -> None:
    env: dict = {}
    print("Geometric Calculator — supports Point, Line. Type 'exit' to quit.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line in ("exit", "quit"):
            break
        if not line:
            continue
        try:
            output = evaluate_line(line, env)
            if output is not None:
                print(output)
        except (SyntaxError, NameError, TypeError, ValueError, AttributeError, ZeroDivisionError) as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    run_repl()
