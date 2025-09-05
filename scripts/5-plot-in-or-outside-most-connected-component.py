import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from collections import defaultdict, deque

# --- Load embeddings ---
def load_embeddings(file_path):
    embeddings = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) > 2:
                node_id = int(parts[0])
                vector = np.array([float(x) for x in parts[1:]])
                embeddings[node_id] = vector
    return embeddings

# --- Load labels ---
def load_labels(json_path):
    with open(json_path, 'r') as f:
        graph_data = json.load(f)
    labels = {}
    for node in graph_data['graph']:
        if node['type'] == 'NODE':
            node_id = node['id']
            label_str = node['label'].lower()
            labels[node_id] = 'client' if 'client' in label_str else 'table'
    return labels

# --- Read edge list ---
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
            edges.append((int(src), int(dst)))
    return edges

# --- Get connected components ---
def get_connected_components(edges):
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
            components.append(bfs(node))

    return components

# --- Mark nodes by component membership ---
def label_by_component(node_ids, largest_component):
    return ['in_largest_component' if nid in largest_component else 'outside' for nid in node_ids]

# --- Prepare data for plotting ---
def prepare_data(embeddings, component_labels):
    vectors = []
    ids = []
    lbls = []
    for node_id, vec in embeddings.items():
        if node_id in component_labels:
            vectors.append(vec)
            ids.append(node_id)
            lbls.append(component_labels[node_id])
    return np.array(vectors), ids, lbls

# --- Plotting ---
def plot_embeddings(vectors, labels, method='pca'):
    reducer = TSNE(n_components=2, random_state=42) if method == 'tsne' else PCA(n_components=2)
    reduced = reducer.fit_transform(vectors)

    plt.figure(figsize=(10, 8))
    for label in set(labels):
        idxs = [i for i, l in enumerate(labels) if l == label]
        plt.scatter(reduced[idxs, 0], reduced[idxs, 1], label=label, alpha=0.7)
    
    plt.legend()
    plt.title(f'2D Embedding Visualization ({method.upper()}) by Component Membership')
    plt.xlabel('Component 1')
    plt.ylabel('Component 2')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(sys.argv[1] + ".jpg", dpi=300)
    # plt.show()

# --- Paths ---
embeddings_file = sys.argv[1]  
json_file       = sys.argv[2]      
edge_list_file  = sys.argv[3]      

# --- Run ---
embeddings = load_embeddings(embeddings_file)
edges = read_edge_list(edge_list_file)
components = get_connected_components(edges)

largest = max(components, key=len)
component_labels = {node: 'in_largest_component' if node in largest else 'outside' for node in embeddings.keys()}
vectors, ids, lbls = prepare_data(embeddings, component_labels)

print("inside or outside largest CC")
print(embeddings_file)
# --- Plot ---
plot_embeddings(vectors, lbls, method=sys.argv[4])
