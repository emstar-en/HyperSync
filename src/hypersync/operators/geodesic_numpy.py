from __future__ import annotations
from typing import List, Tuple, Dict, Any
import numpy as np
import heapq

class GeodesicError(Exception):
    pass

"""
Mathematical Foundations:
Solves the Eikonal equation |grad T(x)| = n(x) on a 2D grid, where T(x) is the arrival time (distance) and n(x) is the refractive index (slowness).
This is equivalent to finding the shortest path in a Riemannian metric g_ij = n(x)^2 delta_ij.
The algorithm used is a Dijkstra-like Fast Marching Method on a graph with 4-connectivity.
The edge weight between neighbors is approximated as 0.5 * (1/n(x) + 1/n(neighbor)).

Fault Detection Logic:
- Validates input dimensions (2D grid).
- Checks source coordinates are within bounds.
- Handles infinite costs/walls (n=0 or very small).
- Returns infinity for unreachable nodes.

Detailed Mechanisms:
1. Initialize distance map with infinity.
2. Set distance 0 at source points and push to priority queue.
3. While queue not empty:
    a. Pop node with smallest distance.
    b. If already visited, skip.
    c. Mark as visited.
    d. For each neighbor:
        i. Calculate tentative distance using trapezoidal rule for cost.
        ii. If shorter, update distance and push to queue.
4. Return distance map.
"""

def solve_eikonal_grid(index_of_refraction: List[List[float]], sources: List[Tuple[int,int]]) -> Dict[str, Any]:
    n = np.asarray(index_of_refraction, dtype=float)
    if n.ndim != 2:
        raise GeodesicError('index_of_refraction must be 2D list/array')
    H, W = n.shape
    for (i,j) in sources:
        if not (0 <= i < H and 0 <= j < W):
            raise GeodesicError(f'source ({i},{j}) out of bounds ({H},{W})')

    w = 1.0 / (n + 1e-12)
    dist = np.full((H, W), np.inf)
    visited = np.zeros((H, W), dtype=bool)
    pq: List[Tuple[float,int,int]] = []

    for (i,j) in sources:
        dist[i,j] = 0.0
        heapq.heappush(pq, (0.0, i, j))

    nbrs = [(1,0),(-1,0),(0,1),(0,-1)]

    while pq:
        d,i,j = heapq.heappop(pq)

        if visited[i,j]:
            continue
        visited[i,j] = True

        for di,dj in nbrs:
            ni, nj = i+di, j+dj
            if 0 <= ni < H and 0 <= nj < W:
                cost = 0.5 * (w[i,j] + w[ni,nj])
                nd = d + cost
                if nd < dist[ni,nj]:
                    dist[ni,nj] = nd
                    heapq.heappush(pq, (nd, ni, nj))

    return {'distance': dist}
