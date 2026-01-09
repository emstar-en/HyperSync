
import math
import heapq

def compute_geodesic_distance(graph, start_node):
    """
    Computes geodesic distances from a start node to all other nodes in a weighted graph
    using Dijkstra's algorithm.
    
    Args:
        graph: Dictionary where keys are node indices and values are lists of (neighbor, weight) tuples.
        start_node: The index of the starting node.
        
    Returns:
        Dictionary mapping node indices to their geodesic distance from start_node.
    """
    distances = {node: float('inf') for node in graph}
    distances[start_node] = 0.0
    
    # Priority queue stores (distance, node)
    pq = [(0.0, start_node)]
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
        if current_dist > distances[current_node]:
            continue
            
        for neighbor, weight in graph.get(current_node, []):
            distance = current_dist + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
                
    return distances

def euclidean_distance(p1, p2):
    """Pure python euclidean distance between two n-dimensional points."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

def build_mesh_graph(vertices, faces):
    """
    Builds a graph representation from mesh vertices and faces for geodesic approximation.
    Edges are created between vertices sharing a face edge. Weights are euclidean distances.
    
    Args:
        vertices: List of tuples/lists representing vertex coordinates.
        faces: List of tuples/lists representing vertex indices for each face.
        
    Returns:
        Adjacency dictionary representing the graph.
    """
    graph = {i: [] for i in range(len(vertices))}
    
    for face in faces:
        # Assuming triangle faces, add edges (0,1), (1,2), (2,0)
        for i in range(len(face)):
            u, v = face[i], face[(i + 1) % len(face)]
            dist = euclidean_distance(vertices[u], vertices[v])
            
            # Add undirected edge
            # Check if edge already exists to avoid duplication if faces share edges
            if not any(n == v for n, _ in graph[u]):
                graph[u].append((v, dist))
            if not any(n == u for n, _ in graph[v]):
                graph[v].append((u, dist))
                
    return graph
