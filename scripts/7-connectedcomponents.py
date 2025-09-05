from collections import defaultdict, deque
import sys
import csv

def read_edge_list(path, delimiter=' '):
    edges = []
    with open(path, 'r') as f:
        for line in f:
            if line.strip() == "":
                continue
            parts = line.strip().split(delimiter)
            if len(parts) != 2:
                continue
            src, dst = parts
            edges.append((src.strip(), dst.strip()))
    return edges


def get_connected_components(edges):
    # Build adjacency list
    graph = defaultdict(set)
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)

    visited = set()
    components = []

    def bfs(start):
        queue = deque([start])
        component = set([start])
        visited.add(start)
        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        return component

    for node in graph:
        if node not in visited:
            component = bfs(node)
            components.append(component)

    return components

# Example usage:
edge_list_path = sys.argv[1]  # Path to your file with "src;dst" per line
output_csv = sys.argv[2] 

edges = read_edge_list(edge_list_path)
components = get_connected_components(edges)

# Print the connected components and their sizes
# for i, comp in enumerate(components):
#     print(f"Component {i+1}: {len(comp)} nodes")

print(len(edges))
j = 0

# Write to CSV
with open(output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Component", "Node", "Component Size"])  # header
    for i, comp in enumerate(components, start=1):
        comp_size = len(comp)
        j+=comp_size
        for node in comp:
            writer.writerow([i, node, comp_size])

print(j)