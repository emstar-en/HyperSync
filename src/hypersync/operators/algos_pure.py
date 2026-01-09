
import math

def dot_product(v1, v2):
    """Computes the dot product of two vectors."""
    return sum(x * y for x, y in zip(v1, v2))

def vector_add(v1, v2):
    """Adds two vectors element-wise."""
    return [x + y for x, y in zip(v1, v2)]

def vector_sub(v1, v2):
    """Subtracts v2 from v1 element-wise."""
    return [x - y for x, y in zip(v1, v2)]

def vector_scalar_mul(v, s):
    """Multiplies a vector by a scalar."""
    return [x * s for x in v]

def l2_norm(v):
    """Computes the L2 norm of a vector."""
    return math.sqrt(sum(x * x for x in v))

def normalize(v):
    """Normalizes a vector to unit length."""
    norm = l2_norm(v)
    if norm == 0:
        return v
    return [x / norm for x in v]

def matrix_vector_mul(matrix, vector):
    """
    Multiplies a matrix (list of lists) by a vector.
    Assumes matrix is a list of rows.
    """
    result = []
    for row in matrix:
        result.append(dot_product(row, vector))
    return result

def transpose(matrix):
    """Transposes a matrix (list of lists)."""
    if not matrix:
        return []
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

def solve_linear_system_gauss(A, b):
    """
    Solves Ax = b using Gaussian elimination (pure python).
    A is a list of lists, b is a list.
    Returns x as a list.
    """
    n = len(b)
    # Deep copy to avoid modifying inputs
    M = [row[:] for row in A]
    y = b[:]
    
    # Forward elimination
    for i in range(n):
        # Find pivot
        max_el = abs(M[i][i])
        max_row = i
        for k in range(i + 1, n):
            if abs(M[k][i]) > max_el:
                max_el = abs(M[k][i])
                max_row = k
        
        # Swap rows
        M[i], M[max_row] = M[max_row], M[i]
        y[i], y[max_row] = y[max_row], y[i]
        
        # Make triangular
        for k in range(i + 1, n):
            c = -M[k][i] / M[i][i]
            for j in range(i, n):
                if i == j:
                    M[k][j] = 0
                else:
                    M[k][j] += c * M[i][j]
            y[k] += c * y[i]
            
    # Back substitution
    x = [0 for _ in range(n)]
    for i in range(n - 1, -1, -1):
        x[i] = y[i] / M[i][i]
        for k in range(i - 1, -1, -1):
            y[k] -= M[k][i] * x[i]
            
    return x
