"""
HyperQL Parser & AST

SQL-like query language with hyperbolic extensions for geodesic joins,
curvature filters, and distance-based operations.
"""
import logging
from typing import List, Optional, Any, Dict
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """AST node types."""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    FROM = "from"
    WHERE = "where"
    JOIN = "join"
    GEODESIC_JOIN = "geodesic_join"
    CURVATURE_FILTER = "curvature_filter"
    DISTANCE_FILTER = "distance_filter"
    COLUMN = "column"
    LITERAL = "literal"
    BINARY_OP = "binary_op"
    FUNCTION = "function"


@dataclass
class ASTNode:
    """Base AST node."""
    node_type: NodeType

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {'type': self.node_type.value}


@dataclass
class ColumnRef(ASTNode):
    """Column reference."""
    table: Optional[str]
    column: str

    def __init__(self, column: str, table: Optional[str] = None):
        super().__init__(NodeType.COLUMN)
        self.table = table
        self.column = column

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'table': self.table,
            'column': self.column
        }


@dataclass
class Literal(ASTNode):
    """Literal value."""
    value: Any

    def __init__(self, value: Any):
        super().__init__(NodeType.LITERAL)
        self.value = value

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'value': self.value
        }


@dataclass
class BinaryOp(ASTNode):
    """Binary operation."""
    operator: str
    left: ASTNode
    right: ASTNode

    def __init__(self, operator: str, left: ASTNode, right: ASTNode):
        super().__init__(NodeType.BINARY_OP)
        self.operator = operator
        self.left = left
        self.right = right

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'operator': self.operator,
            'left': self.left.to_dict(),
            'right': self.right.to_dict()
        }


@dataclass
class Function(ASTNode):
    """Function call."""
    name: str
    args: List[ASTNode]

    def __init__(self, name: str, args: List[ASTNode]):
        super().__init__(NodeType.FUNCTION)
        self.name = name
        self.args = args

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'name': self.name,
            'args': [arg.to_dict() for arg in self.args]
        }


@dataclass
class FromClause(ASTNode):
    """FROM clause."""
    table: str
    alias: Optional[str]

    def __init__(self, table: str, alias: Optional[str] = None):
        super().__init__(NodeType.FROM)
        self.table = table
        self.alias = alias

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'table': self.table,
            'alias': self.alias
        }


@dataclass
class WhereClause(ASTNode):
    """WHERE clause."""
    condition: ASTNode

    def __init__(self, condition: ASTNode):
        super().__init__(NodeType.WHERE)
        self.condition = condition

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'condition': self.condition.to_dict()
        }


@dataclass
class JoinClause(ASTNode):
    """JOIN clause."""
    join_type: str  # INNER, LEFT, RIGHT, FULL
    table: str
    alias: Optional[str]
    condition: ASTNode

    def __init__(self, join_type: str, table: str, condition: ASTNode, alias: Optional[str] = None):
        super().__init__(NodeType.JOIN)
        self.join_type = join_type
        self.table = table
        self.alias = alias
        self.condition = condition

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'join_type': self.join_type,
            'table': self.table,
            'alias': self.alias,
            'condition': self.condition.to_dict()
        }


@dataclass
class GeodesicJoin(ASTNode):
    """
    Geodesic join - hyperbolic extension.

    Example: JOIN table2 USING GEODESIC_DISTANCE < 0.5
    """
    table: str
    alias: Optional[str]
    distance_threshold: float
    left_point: ColumnRef
    right_point: ColumnRef

    def __init__(
        self,
        table: str,
        distance_threshold: float,
        left_point: ColumnRef,
        right_point: ColumnRef,
        alias: Optional[str] = None
    ):
        super().__init__(NodeType.GEODESIC_JOIN)
        self.table = table
        self.alias = alias
        self.distance_threshold = distance_threshold
        self.left_point = left_point
        self.right_point = right_point

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'table': self.table,
            'alias': self.alias,
            'distance_threshold': self.distance_threshold,
            'left_point': self.left_point.to_dict(),
            'right_point': self.right_point.to_dict()
        }


@dataclass
class CurvatureFilter(ASTNode):
    """
    Curvature filter - hyperbolic extension.

    Example: WHERE CURVATURE BETWEEN -1.5 AND -0.5
    """
    column: ColumnRef
    min_curvature: float
    max_curvature: float

    def __init__(self, column: ColumnRef, min_curvature: float, max_curvature: float):
        super().__init__(NodeType.CURVATURE_FILTER)
        self.column = column
        self.min_curvature = min_curvature
        self.max_curvature = max_curvature

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'column': self.column.to_dict(),
            'min_curvature': self.min_curvature,
            'max_curvature': self.max_curvature
        }


@dataclass
class HyperSelect(ASTNode):
    """SELECT statement with hyperbolic extensions."""
    columns: List[ColumnRef]
    from_clause: FromClause
    joins: List[ASTNode]  # Can include JoinClause or GeodesicJoin
    where: Optional[WhereClause]
    group_by: Optional[List[ColumnRef]]
    having: Optional[ASTNode]
    order_by: Optional[List[tuple]]  # (column, direction)
    limit: Optional[int]
    offset: Optional[int]

    def __init__(
        self,
        columns: List[ColumnRef],
        from_clause: FromClause,
        joins: Optional[List[ASTNode]] = None,
        where: Optional[WhereClause] = None,
        group_by: Optional[List[ColumnRef]] = None,
        having: Optional[ASTNode] = None,
        order_by: Optional[List[tuple]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ):
        super().__init__(NodeType.SELECT)
        self.columns = columns
        self.from_clause = from_clause
        self.joins = joins or []
        self.where = where
        self.group_by = group_by
        self.having = having
        self.order_by = order_by
        self.limit = limit
        self.offset = offset

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'columns': [col.to_dict() for col in self.columns],
            'from': self.from_clause.to_dict(),
            'joins': [join.to_dict() for join in self.joins],
            'where': self.where.to_dict() if self.where else None,
            'group_by': [col.to_dict() for col in self.group_by] if self.group_by else None,
            'order_by': self.order_by,
            'limit': self.limit,
            'offset': self.offset
        }


class HyperQLParser:
    """
    Parser for HyperQL language.

    Simplified parser using recursive descent. In production, would use
    a proper parser generator like Lark or ANTLR.
    """

    def __init__(self):
        self.tokens = []
        self.pos = 0

    def parse(self, query: str) -> ASTNode:
        """
        Parse HyperQL query.

        Args:
            query: Query string

        Returns:
            AST root node
        """
        # Tokenize
        self.tokens = self._tokenize(query)
        self.pos = 0

        # Parse based on first keyword
        first_token = self._peek().upper()

        if first_token == 'SELECT':
            return self._parse_select()
        elif first_token == 'INSERT':
            return self._parse_insert()
        elif first_token == 'UPDATE':
            return self._parse_update()
        elif first_token == 'DELETE':
            return self._parse_delete()
        else:
            raise ValueError(f"Unexpected query type: {first_token}")

    def _tokenize(self, query: str) -> List[str]:
        """Simple tokenizer."""
        # In production, would use proper lexer
        import re
        tokens = re.findall(r'\w+|[<>=!]+|[(),*.]|'[^']*'', query)
        return tokens

    def _peek(self, offset: int = 0) -> str:
        """Peek at token."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return ''

    def _consume(self) -> str:
        """Consume and return current token."""
        token = self._peek()
        self.pos += 1
        return token

    def _expect(self, expected: str):
        """Expect specific token."""
        token = self._consume()
        if token.upper() != expected.upper():
            raise ValueError(f"Expected {expected}, got {token}")

    def _parse_select(self) -> HyperSelect:
        """Parse SELECT statement."""
        self._expect('SELECT')

        # Parse columns
        columns = self._parse_column_list()

        # Parse FROM
        self._expect('FROM')
        from_clause = self._parse_from()

        # Parse optional clauses
        joins = []
        where = None

        while self.pos < len(self.tokens):
            keyword = self._peek().upper()

            if keyword in ('JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL'):
                joins.append(self._parse_join())
            elif keyword == 'WHERE':
                where = self._parse_where()
            elif keyword == 'LIMIT':
                break
            else:
                break

        return HyperSelect(
            columns=columns,
            from_clause=from_clause,
            joins=joins,
            where=where
        )

    def _parse_column_list(self) -> List[ColumnRef]:
        """Parse column list."""
        columns = []

        while True:
            col_name = self._consume()

            # Check for table.column
            if self._peek() == '.':
                self._consume()  # consume '.'
                table = col_name
                col_name = self._consume()
                columns.append(ColumnRef(col_name, table))
            else:
                columns.append(ColumnRef(col_name))

            if self._peek() != ',':
                break
            self._consume()  # consume ','

        return columns

    def _parse_from(self) -> FromClause:
        """Parse FROM clause."""
        table = self._consume()

        # Check for alias
        alias = None
        if self._peek().upper() not in ('WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', ''):
            alias = self._consume()

        return FromClause(table, alias)

    def _parse_join(self) -> ASTNode:
        """Parse JOIN clause."""
        # Check for geodesic join
        if self._peek(1).upper() == 'USING' and self._peek(2).upper() == 'GEODESIC_DISTANCE':
            return self._parse_geodesic_join()

        # Regular join
        join_type = 'INNER'
        if self._peek().upper() in ('INNER', 'LEFT', 'RIGHT', 'FULL'):
            join_type = self._consume().upper()

        self._expect('JOIN')
        table = self._consume()

        # Alias
        alias = None
        if self._peek().upper() == 'ON':
            pass
        else:
            alias = self._consume()

        self._expect('ON')
        condition = self._parse_condition()

        return JoinClause(join_type, table, condition, alias)

    def _parse_geodesic_join(self) -> GeodesicJoin:
        """Parse geodesic join."""
        self._expect('JOIN')
        table = self._consume()

        self._expect('USING')
        self._expect('GEODESIC_DISTANCE')

        # Parse distance condition
        op = self._consume()  # <, <=, =, etc.
        threshold = float(self._consume())

        # For now, assume default point columns
        left_point = ColumnRef('point')
        right_point = ColumnRef('point', table)

        return GeodesicJoin(table, threshold, left_point, right_point)

    def _parse_where(self) -> WhereClause:
        """Parse WHERE clause."""
        self._expect('WHERE')
        condition = self._parse_condition()
        return WhereClause(condition)

    def _parse_condition(self) -> ASTNode:
        """Parse condition expression."""
        # Simplified - just parse binary comparison
        left = self._parse_value()

        if self.pos >= len(self.tokens):
            return left

        op = self._peek()
        if op in ('=', '<', '>', '<=', '>=', '!=', '<>'):
            self._consume()
            right = self._parse_value()
            return BinaryOp(op, left, right)

        return left

    def _parse_value(self) -> ASTNode:
        """Parse value expression."""
        token = self._consume()

        # Check if it's a number
        try:
            value = float(token)
            return Literal(value)
        except ValueError:
            pass

        # Check if it's a string literal
        if token.startswith("'"):
            return Literal(token.strip("'"))

        # Otherwise it's a column reference
        return ColumnRef(token)

    def _parse_insert(self) -> ASTNode:
        """Parse INSERT statement."""
        # Simplified implementation
        raise NotImplementedError("INSERT parsing not yet implemented")

    def _parse_update(self) -> ASTNode:
        """Parse UPDATE statement."""
        raise NotImplementedError("UPDATE parsing not yet implemented")

    def _parse_delete(self) -> ASTNode:
        """Parse DELETE statement."""
        raise NotImplementedError("DELETE parsing not yet implemented")


# Export public API
__all__ = [
    'HyperQLParser',
    'ASTNode',
    'HyperSelect',
    'GeodesicJoin',
    'CurvatureFilter',
    'ColumnRef',
    'Literal',
    'BinaryOp',
    'Function',
    'FromClause',
    'WhereClause',
    'JoinClause'
]
