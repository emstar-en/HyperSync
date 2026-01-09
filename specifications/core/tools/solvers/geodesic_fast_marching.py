
import numpy as np
import heapq

def solve_eikonal(speed_grid, source_points, grid_spacing=1.0):
    """
    Solves the Eikonal equation |grad T| = 1/f using the Fast Marching Method.

    Args:
        speed_grid (np.ndarray): 2D array of speed values (f) at each grid point.
        source_points (list of tuples): List of (row, col) tuples for source points where T=0.
        grid_spacing (float): Distance between grid points (h).

    Returns:
        np.ndarray: 2D array of arrival times T.
    """
    rows, cols = speed_grid.shape
    arrival_times = np.full((rows, cols), np.inf)
    status = np.zeros((rows, cols), dtype=int) # 0: Far, 1: Narrow Band, 2: Frozen

    FAR = 0
    NARROW = 1
    FROZEN = 2

    heap = []

    # Initialize sources
    for r, c in source_points:
        arrival_times[r, c] = 0.0
        status[r, c] = NARROW
        heapq.heappush(heap, (0.0, r, c))

    while heap:
        t, r, c = heapq.heappop(heap)

        if status[r, c] == FROZEN:
            continue

        status[r, c] = FROZEN

        # Check neighbors
        neighbors = [
            (r+1, c), (r-1, c), (r, c+1), (r, c-1)
        ]

        for nr, nc in neighbors:
            if 0 <= nr < rows and 0 <= nc < cols and status[nr, nc] != FROZEN:
                # Calculate tentative time
                # Solve quadratic equation for T: (T - Tx)^2 + (T - Ty)^2 = (h/f)^2

                # Get min time of frozen neighbors in x and y directions
                tx = min(
                    arrival_times[nr+1, nc] if nr+1 < rows and status[nr+1, nc] == FROZEN else np.inf,
                    arrival_times[nr-1, nc] if nr-1 >= 0 and status[nr-1, nc] == FROZEN else np.inf
                )

                ty = min(
                    arrival_times[nr, nc+1] if nc+1 < cols and status[nr, nc+1] == FROZEN else np.inf,
                    arrival_times[nr, nc-1] if nc-1 >= 0 and status[nr, nc-1] == FROZEN else np.inf
                )

                h = grid_spacing
                f = speed_grid[nr, nc]

                # Standard Eikonal update
                if np.isinf(tx) and np.isinf(ty):
                    new_t = np.inf
                elif np.isinf(tx):
                    new_t = ty + h/f
                elif np.isinf(ty):
                    new_t = tx + h/f
                else:
                    # Quadratic: 2*T^2 - 2*(tx+ty)*T + (tx^2 + ty^2 - (h/f)^2) = 0
                    # Simplified: (T-tx)^2 + (T-ty)^2 = (h/f)^2
                    # Let T = t + delta
                    # Actually, standard solution:
                    diff = abs(tx - ty)
                    if diff < h/f:
                        new_t = (tx + ty + np.sqrt(2*(h/f)**2 - diff**2)) / 2
                    else:
                        new_t = min(tx, ty) + h/f

                if new_t < arrival_times[nr, nc]:
                    arrival_times[nr, nc] = new_t
                    status[nr, nc] = NARROW
                    heapq.heappush(heap, (new_t, nr, nc))

    return arrival_times
