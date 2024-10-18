from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Tuple
import itertools

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Graph(BaseModel):
    nodes: List[str]
    links: List[Dict[str, str]]

def find_hamiltonian_cycle(graph: Graph):
    n = len(graph.nodes)
    node_to_index = {node: i for i, node in enumerate(graph.nodes)}
    
    # Create adjacency matrix for undirected graph
    adj_matrix = [[0] * n for _ in range(n)]
    for link in graph.links:
        i, j = node_to_index[link['from']], node_to_index[link['to']]
        adj_matrix[i][j] = adj_matrix[j][i] = 1

    def dfs(path, used):
        if len(path) == n:
            # Check if it's a cycle
            if adj_matrix[path[-1]][path[0]] == 1:
                return path + [path[0]]
            return None

        for next_node in range(n):
            if not used[next_node] and adj_matrix[path[-1]][next_node] == 1:
                used[next_node] = True
                result = dfs(path + [next_node], used)
                if result:
                    return result
                used[next_node] = False
        return None

    # Try starting from each node
    for start in range(n):
        used = [False] * n
        used[start] = True
        cycle = dfs([start], used)
        if cycle:
            return [graph.nodes[i] for i in cycle]

    return None

@app.post("/find-hamilton")
async def find_hamilton(graph: Graph):
    cycle = find_hamiltonian_cycle(graph)
    if cycle:
        return {"cycle": cycle}
    else:
         # Return a proper response indicating no cycle instead of raising an HTTP exception
        return {"cycle": None, "message": "No Hamiltonian cycle found"}

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)