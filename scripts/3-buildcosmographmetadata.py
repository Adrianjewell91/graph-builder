import sys
import csv
import json


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


# --- Save CSV ---
def write_node_colors_csv(labels_dict, output_csv_path):
    with open(output_csv_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(['id', 'color'])  # Header
        for node_id, label in labels_dict.items():
            color = 'red' if label == 'client' else 'blue'
            writer.writerow([node_id, color])

# --- Run ---
json_file = sys.argv[1]  # Replace with your actual path
labels = load_labels(json_file)
write_node_colors_csv(labels, sys.argv[2])  # Output path

# --- Run ---
labels = load_labels(json_file)