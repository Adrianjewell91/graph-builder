import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import sys

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
        if node['type'] == 'NODE' and node['label'] is not None:
            # print(node['id'])
            node_id = node['id']
            label_str = node['label'].lower()
            labels[node_id] = 'client' if 'client' in label_str else 'table'
    return labels

# --- Combine data ---
def prepare_data(embeddings, labels):
    vectors = []
    ids = []
    lbls = []
    for node_id, vec in embeddings.items():
        if node_id in labels:
            vectors.append(vec)
            ids.append(node_id)
            lbls.append(labels[node_id])
    return np.array(vectors), ids, lbls

# --- Plotting ---
def plot_embeddings(vectors, labels, method='pca'):
    if method == 'tsne':
        reducer = TSNE(n_components=2, random_state=42)
    else:
        reducer = PCA(n_components=2)
    
    reduced = reducer.fit_transform(vectors)
    # print(vectors)
    # print(reduced)
    
    plt.figure(figsize=(10, 8))
    for label in set(labels):
        idxs = [i for i, l in enumerate(labels) if l == label]
        plt.scatter(reduced[idxs, 0], reduced[idxs, 1], label=label, alpha=0.7)
    
    plt.legend()
    plt.title(f'2D Embedding Visualization using {method.upper()}')
    plt.xlabel('Component 1')
    plt.ylabel('Component 2')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(sys.argv[1] + ".jpg", dpi=300)
    # plt.show()

# --- Paths ---
embeddings_file = sys.argv[1]  
json_file       = sys.argv[2]

# --- Run ---
embeddings = load_embeddings(embeddings_file)
labels = load_labels(json_file)
vectors, ids, lbls = prepare_data(embeddings, labels)

print("clients to tables")
print(embeddings_file)
# why don't clients show up? I don't know.

# Plot with PCA (or use method='tsne')
plot_embeddings(vectors, lbls, method=sys.argv[3])
