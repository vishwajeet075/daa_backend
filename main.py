from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://delicate-tiramisu-6f2924.netlify.app"],  # Adjust this to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Graph(BaseModel):
    nodes: List[str]
    links: List[Dict[str, str]]

# Bitmask Hamiltonian Cycle Solver
def find_hamiltonian_cycle(graph: Graph):
    n = len(graph.nodes)
    node_to_index = {node: i for i, node in enumerate(graph.nodes)}
    
    # Create adjacency matrix for undirected graph
    adj_matrix = [[0] * n for _ in range(n)]
    for link in graph.links:
        i, j = node_to_index[link['from']], node_to_index[link['to']]
        adj_matrix[i][j] = adj_matrix[j][i] = 1

    # DP table where dp[mask][i] stores the shortest path to reach node i using nodes in 'mask'
    dp = [[float('inf')] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]  # To reconstruct the path
    
    # Start from each node
    for i in range(n):
        dp[1 << i][i] = 0  # Starting point, no cost to reach self

    # Fill the DP table
    for mask in range(1 << n):
        for u in range(n):
            if mask & (1 << u):  # If u is in the current set represented by mask
                for v in range(n):
                    if adj_matrix[u][v] == 1 and not mask & (1 << v):  # If v is a neighbor and not yet in the mask
                        new_mask = mask | (1 << v)
                        if dp[mask][u] + 1 < dp[new_mask][v]:
                            dp[new_mask][v] = dp[mask][u] + 1
                            parent[new_mask][v] = u

    # Check if we can return to the starting point
    end_mask = (1 << n) - 1  # All nodes visited
    cycle_end = -1
    for i in range(n):
        if dp[end_mask][i] < float('inf') and adj_matrix[i][0] == 1:  # Check if there's an edge back to start
            cycle_end = i
            break

    # If no cycle was found
    if cycle_end == -1:
        return None

    # Reconstruct the cycle
    cycle = []
    mask = end_mask
    node = cycle_end
    while node != -1:
        cycle.append(graph.nodes[node])
        next_node = parent[mask][node]
        mask ^= (1 << node)  # Remove node from the mask
        node = next_node

    cycle.append(graph.nodes[0])  # Complete the cycle
    return cycle[::-1]  # Reverse the cycle to start from the initial node

@app.post("/find-hamilton")
async def find_hamilton(graph: Graph):
    cycle = find_hamiltonian_cycle(graph)
    if cycle:
        return {"cycle": cycle}
    else:
        return {"cycle": None, "message": "No Hamiltonian cycle found"}

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)
