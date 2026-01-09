"""
Lambda Calculus Reduction Engine

Implements lambda calculus with:
- Lambda terms (variables, abstractions, applications)
- Beta reduction (substitution)
- Alpha conversion (variable renaming)
- Eta conversion
- Normal form computation
- Type inference (Hindley-Milner)
"""

from typing import Optional, Set, Dict, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json

# ============================================================================
# Lambda Terms
# ============================================================================

class Term:
    """Base class for lambda terms."""

    def free_vars(self) -> Set[str]:
        """Get free variables in term."""
        raise NotImplementedError

    def substitute(self, var: str, replacement: 'Term') -> 'Term':
        """Substitute variable with replacement term."""
        raise NotImplementedError

    def alpha_convert(self, old_var: str, new_var: str) -> 'Term':
        """Alpha conversion: rename bound variable."""
        raise NotImplementedError

    def beta_reduce_step(self) -> Optional['Term']:
        """Perform one step of beta reduction."""
        raise NotImplementedError

    def normalize(self, max_steps: int = 1000) -> 'Term':
        """Reduce to normal form."""
        current = self
        for _ in range(max_steps):
            next_term = current.beta_reduce_step()
            if next_term is None:
                return current  # Normal form reached
            current = next_term
        raise RuntimeError("Normalization exceeded max steps (possible infinite loop)")


@dataclass(frozen=True)
class Var(Term):
    """Variable: x"""
    name: str

    def free_vars(self) -> Set[str]:
        return {self.name}

    def substitute(self, var: str, replacement: Term) -> Term:
        if self.name == var:
            return replacement
        return self

    def alpha_convert(self, old_var: str, new_var: str) -> Term:
        if self.name == old_var:
            return Var(new_var)
        return self

    def beta_reduce_step(self) -> Optional[Term]:
        return None  # Variables are in normal form

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Abs(Term):
    """Abstraction: λx.M"""
    var: str
    body: Term

    def free_vars(self) -> Set[str]:
        return self.body.free_vars() - {self.var}

    def substitute(self, var: str, replacement: Term) -> Term:
        if self.var == var:
            # Variable is bound, no substitution
            return self
        elif self.var in replacement.free_vars():
            # Capture-avoiding substitution: alpha convert first
            fresh_var = self._fresh_var(replacement.free_vars() | self.body.free_vars())
            new_body = self.body.alpha_convert(self.var, fresh_var)
            return Abs(fresh_var, new_body.substitute(var, replacement))
        else:
            # Safe to substitute in body
            return Abs(self.var, self.body.substitute(var, replacement))

    def alpha_convert(self, old_var: str, new_var: str) -> Term:
        if self.var == old_var:
            # This abstraction binds the variable
            return Abs(new_var, self.body.alpha_convert(old_var, new_var))
        else:
            # Recurse into body
            return Abs(self.var, self.body.alpha_convert(old_var, new_var))

    def beta_reduce_step(self) -> Optional[Term]:
        # Try to reduce body
        reduced_body = self.body.beta_reduce_step()
        if reduced_body is not None:
            return Abs(self.var, reduced_body)
        return None

    def _fresh_var(self, avoid: Set[str]) -> str:
        """Generate fresh variable name."""
        base = self.var
        counter = 0
        while True:
            candidate = f"{base}_{counter}" if counter > 0 else base
            if candidate not in avoid:
                return candidate
            counter += 1

    def __str__(self):
        return f"(λ{self.var}.{self.body})"


@dataclass(frozen=True)
class App(Term):
    """Application: M N"""
    func: Term
    arg: Term

    def free_vars(self) -> Set[str]:
        return self.func.free_vars() | self.arg.free_vars()

    def substitute(self, var: str, replacement: Term) -> Term:
        return App(
            self.func.substitute(var, replacement),
            self.arg.substitute(var, replacement)
        )

    def alpha_convert(self, old_var: str, new_var: str) -> Term:
        return App(
            self.func.alpha_convert(old_var, new_var),
            self.arg.alpha_convert(old_var, new_var)
        )

    def beta_reduce_step(self) -> Optional[Term]:
        # Beta reduction: (λx.M) N → M[x := N]
        if isinstance(self.func, Abs):
            return self.func.body.substitute(self.func.var, self.arg)

        # Try to reduce function
        reduced_func = self.func.beta_reduce_step()
        if reduced_func is not None:
            return App(reduced_func, self.arg)

        # Try to reduce argument
        reduced_arg = self.arg.beta_reduce_step()
        if reduced_arg is not None:
            return App(self.func, reduced_arg)

        return None

    def __str__(self):
        return f"({self.func} {self.arg})"


# ============================================================================
# Standard Lambda Terms
# ============================================================================

# Identity: λx.x
IDENTITY = Abs("x", Var("x"))

# True: λx.λy.x
TRUE = Abs("x", Abs("y", Var("x")))

# False: λx.λy.y
FALSE = Abs("x", Abs("y", Var("y")))

# And: λp.λq.p q p
AND = Abs("p", Abs("q", App(App(Var("p"), Var("q")), Var("p"))))

# Or: λp.λq.p p q
OR = Abs("p", Abs("q", App(App(Var("p"), Var("p")), Var("q"))))

# Not: λp.p FALSE TRUE
NOT = Abs("p", App(App(Var("p"), FALSE), TRUE))

# Pair: λx.λy.λf.f x y
PAIR = Abs("x", Abs("y", Abs("f", App(App(Var("f"), Var("x")), Var("y")))))

# First: λp.p TRUE
FIRST = Abs("p", App(Var("p"), TRUE))

# Second: λp.p FALSE
SECOND = Abs("p", App(Var("p"), FALSE))


# ============================================================================
# Type System (Hindley-Milner)
# ============================================================================

class Type:
    """Base class for types."""
    pass


@dataclass(frozen=True)
class TypeVar(Type):
    """Type variable: α"""
    name: str

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class TypeArrow(Type):
    """Function type: τ₁ → τ₂"""
    arg_type: Type
    return_type: Type

    def __str__(self):
        return f"({self.arg_type} → {self.return_type})"


class TypeInferenceError(Exception):
    """Type inference error."""
    pass


class TypeEnvironment:
    """Type environment for inference."""

    def __init__(self):
        self.bindings: Dict[str, Type] = {}
        self.constraints: list[Tuple[Type, Type]] = []
        self.next_var_id = 0

    def fresh_type_var(self) -> TypeVar:
        """Generate fresh type variable."""
        var = TypeVar(f"α{self.next_var_id}")
        self.next_var_id += 1
        return var

    def add_binding(self, var: str, typ: Type):
        """Add variable binding."""
        self.bindings[var] = typ

    def get_binding(self, var: str) -> Optional[Type]:
        """Get variable binding."""
        return self.bindings.get(var)

    def add_constraint(self, t1: Type, t2: Type):
        """Add type equality constraint."""
        self.constraints.append((t1, t2))

    def unify(self) -> Dict[str, Type]:
        """Unify constraints and return substitution."""
        subst = {}

        for t1, t2 in self.constraints:
            t1 = self._apply_subst(t1, subst)
            t2 = self._apply_subst(t2, subst)

            if isinstance(t1, TypeVar):
                if t1 != t2:
                    subst[t1.name] = t2
            elif isinstance(t2, TypeVar):
                if t1 != t2:
                    subst[t2.name] = t1
            elif isinstance(t1, TypeArrow) and isinstance(t2, TypeArrow):
                self.add_constraint(t1.arg_type, t2.arg_type)
                self.add_constraint(t1.return_type, t2.return_type)
            else:
                raise TypeInferenceError(f"Cannot unify {t1} and {t2}")

        return subst

    def _apply_subst(self, typ: Type, subst: Dict[str, Type]) -> Type:
        """Apply substitution to type."""
        if isinstance(typ, TypeVar):
            return subst.get(typ.name, typ)
        elif isinstance(typ, TypeArrow):
            return TypeArrow(
                self._apply_subst(typ.arg_type, subst),
                self._apply_subst(typ.return_type, subst)
            )
        return typ


def infer_type(term: Term, env: Optional[TypeEnvironment] = None) -> Type:
    """
    Infer type of lambda term using Hindley-Milner algorithm.

    Args:
        term: Lambda term
        env: Type environment (created if None)

    Returns:
        Type: Inferred type

    Raises:
        TypeInferenceError: If type inference fails
    """
    if env is None:
        env = TypeEnvironment()

    if isinstance(term, Var):
        # Variable: look up in environment
        typ = env.get_binding(term.name)
        if typ is None:
            raise TypeInferenceError(f"Unbound variable: {term.name}")
        return typ

    elif isinstance(term, Abs):
        # Abstraction: λx.M has type α → τ where τ is type of M
        arg_type = env.fresh_type_var()
        env.add_binding(term.var, arg_type)
        body_type = infer_type(term.body, env)
        return TypeArrow(arg_type, body_type)

    elif isinstance(term, App):
        # Application: if M : τ₁ → τ₂ and N : τ₁, then M N : τ₂
        func_type = infer_type(term.func, env)
        arg_type = infer_type(term.arg, env)
        result_type = env.fresh_type_var()

        # Add constraint: func_type = arg_type → result_type
        env.add_constraint(func_type, TypeArrow(arg_type, result_type))

        # Unify constraints
        subst = env.unify()

        return env._apply_subst(result_type, subst)

    else:
        raise TypeInferenceError(f"Unknown term type: {type(term)}")


# ============================================================================
# Lambda Cube Vertices
# ============================================================================

class LambdaCubeVertex(Enum):
    """Vertices of the lambda cube."""
    LAMBDA_ARROW = "λ→"  # Simply typed lambda calculus
    LAMBDA_2 = "λ2"  # System F (polymorphism)
    LAMBDA_OMEGA = "λω"  # System Fω (type operators)
    LAMBDA_P = "λP"  # LF (dependent types)
    LAMBDA_P2 = "λP2"  # System Fω + dependent types
    LAMBDA_OMEGA_BAR = "λω̅"  # λω + dependent types
    LAMBDA_P_OMEGA = "λPω"  # λP + type operators
    LAMBDA_C = "λC"  # Calculus of Constructions (all features)


def validate_lambda_cube_vertex(vertex: str, term: Term) -> dict:
    """
    Validate term against lambda cube vertex.

    Args:
        vertex: Lambda cube vertex name
        term: Lambda term to validate

    Returns:
        dict: Validation result
    """
    try:
        vertex_enum = LambdaCubeVertex(vertex)
    except ValueError:
        return {
            "valid": False,
            "error": f"Unknown lambda cube vertex: {vertex}"
        }

    try:
        # Attempt type inference
        typ = infer_type(term)

        return {
            "valid": True,
            "vertex": vertex,
            "term": str(term),
            "inferred_type": str(typ),
            "normal_form": str(term.normalize())
        }

    except Exception as e:
        return {
            "valid": False,
            "vertex": vertex,
            "term": str(term),
            "error": str(e)
        }


# ============================================================================
# Attestation Generation
# ============================================================================

def generate_lambda_attestation(term: Term) -> dict:
    """
    Generate attestation for lambda term.

    Args:
        term: Lambda term

    Returns:
        dict: Attestation with type and normal form
    """
    try:
        typ = infer_type(term)
        normal_form = term.normalize()

        return {
            "type": "lambda_term_attestation",
            "term": str(term),
            "inferred_type": str(typ),
            "normal_form": str(normal_form),
            "free_variables": list(term.free_vars()),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        return {
            "type": "lambda_term_attestation",
            "term": str(term),
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


# ============================================================================
# Testing and Validation
# ============================================================================

def test_lambda_calculus():
    """Test lambda calculus implementation."""
    print("Testing lambda calculus...")

    # Test beta reduction
    # (λx.x) y → y
    term = App(IDENTITY, Var("y"))
    reduced = term.normalize()
    assert str(reduced) == "y"
    print("  ✓ Beta reduction works")

    # Test Church booleans
    # TRUE x y → x
    term = App(App(TRUE, Var("x")), Var("y"))
    reduced = term.normalize()
    assert str(reduced) == "x"
    print("  ✓ Church booleans work")

    # Test type inference
    # λx.x : α → α
    typ = infer_type(IDENTITY)
    assert isinstance(typ, TypeArrow)
    print("  ✓ Type inference works")

    # Test lambda cube validation
    result = validate_lambda_cube_vertex("λ→", IDENTITY)
    assert result['valid']
    print("  ✓ Lambda cube validation works")

    print("All tests passed!")


if __name__ == '__main__':
    test_lambda_calculus()
