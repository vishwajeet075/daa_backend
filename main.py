from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import networkx as nx

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://delicate-tiramisu-6f2924.netlify.app"],  # Match your frontend URL
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

def find_hamiltonian_cycle(graph: Graph) -> Optional[List[int]]:
    G = nx.Graph()
    G.add_nodes_from(range(len(graph.nodes)))
    G.add_edges_from(graph.edges)
    
    def dfs_hamiltonian(node, path, visited):
        if len(path) == len(G.nodes) and G.has_edge(path[-1], path[0]):
            return path + [path[0]]
        
        for neighbor in G.neighbors(node):
            if neighbor not in visited:
                result = dfs_hamiltonian(neighbor, path + [neighbor], visited | {neighbor})
                if result:
                    return result
        
        return None

    for start_node in G.nodes:
        cycle = dfs_hamiltonian(start_node, [start_node], {start_node})
        if cycle:
            return cycle

    return None

def generate_cycle_text(cycle: List[int]) -> str:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cycle_str = " -> ".join(alphabet[i] for i in cycle)
    return f"Hamiltonian Cycle found: {cycle_str}"

@app.post("/find-hamilton")
async def find_hamilton(graph: Graph):
    cycle = find_hamiltonian_cycle(graph)
    if cycle:
        cycle_text = generate_cycle_text(cycle)
        return {"cycle": cycle, "cycleText": cycle_text}
    else:
        return {"cycle": [], "cycleText": "No Hamiltonian Cycle found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)