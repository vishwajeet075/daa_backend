from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import networkx as nx

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://delicate-tiramisu-6f2924.netlify.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    x: float
    y: float

class Graph(BaseModel):
    nodes: List[Node]
    edges: List[List[int]]

def is_valid_next_node(G, current, next_node, path, remaining_nodes):
    """Check if adding next_node to path is promising"""
    if not G.has_edge(current, next_node):
        return False
    
    # If this is the last node, check if it can connect back to start
    if len(remaining_nodes) == 1:
        return G.has_edge(next_node, path[0])
        
    # Check if next_node has at least 2 edges to remaining nodes
    # (needed for eventual cycle completion)
    available_edges = sum(1 for n in G.neighbors(next_node) 
                         if n in remaining_nodes or n == path[0])
    return available_edges >= 2

def canonicalize_cycle(cycle):
    """Convert a cycle to its canonical form for unique identification"""
    # Find the position of the minimum value
    min_val = min(cycle[:-1])  # Exclude the last element as it's same as first
    min_idx = cycle.index(min_val)
    
    # Rotate cycle to start with minimum value
    canonical = cycle[min_idx:-1] + cycle[:min_idx] + [cycle[min_idx]]
    
    # Return the smaller of forward and reverse orientations
    reverse = canonical[::-1]
    reverse = reverse[-1:] + reverse[:-1]  # Rotate to ensure same start point
    return tuple(min(canonical, reverse))

def find_hamiltonian_cycles(graph: Graph) -> (Optional[List[int]], int):
    """Find all unique Hamiltonian cycles in the graph"""
    G = nx.Graph()
    G.add_nodes_from(range(len(graph.nodes)))
    G.add_edges_from(graph.edges)
    
    # Early validation
    if not nx.is_connected(G):
        return None, 0
    
    for node in G.nodes:
        if G.degree(node) < 2:
            return None, 0

    unique_cycles = set()
    example_cycle = None

    def dfs_hamiltonian(node, path, remaining_nodes):
        nonlocal example_cycle
        
        # Base case: if path includes all nodes and can return to start
        if not remaining_nodes and G.has_edge(path[-1], path[0]):
            cycle = path + [path[0]]
            canonical = canonicalize_cycle(cycle)
            if canonical not in unique_cycles:
                unique_cycles.add(canonical)
                if example_cycle is None:
                    example_cycle = cycle
            return
        
        # Sort neighbors by degree for better efficiency
        neighbors = sorted(
            [n for n in G.neighbors(node) if n in remaining_nodes],
            key=lambda x: G.degree(x)
        )
        
        # Try each possible next node
        for next_node in neighbors:
            if is_valid_next_node(G, node, next_node, path, remaining_nodes):
                new_remaining = remaining_nodes - {next_node}
                dfs_hamiltonian(next_node, path + [next_node], new_remaining)

    # Start from the vertex with minimum degree to reduce branching
    start_node = min(G.nodes, key=lambda x: G.degree(x))
    remaining_nodes = set(G.nodes) - {start_node}
    dfs_hamiltonian(start_node, [start_node], remaining_nodes)

    return example_cycle, len(unique_cycles)

def generate_cycle_text(cycle: List[int]) -> str:
    """Generate a human-readable representation of the cycle"""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cycle_str = " → ".join(alphabet[i] for i in cycle)
    return f"Hamiltonian Cycle found: {cycle_str}"

@app.post("/find-hamilton")
async def find_hamilton(graph: Graph):
    cycle, total_cycles = find_hamiltonian_cycles(graph)
    if cycle:
        cycle_text = generate_cycle_text(cycle)
        return {
            "cycle": cycle,
            "cycleText": cycle_text,
            "totalCycles": total_cycles
        }
    else:
        return {
            "cycle": [],
            "cycleText": "No Hamiltonian Cycle found.",
            "totalCycles": 0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)