import json
import sys

input_file = sys.argv[1]  # Replace with your actual file name
print(input_file)

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build a set of valid node IDs
node_ids = {node['id'] for node in data['graph'] if node['type'] == 'NODE'}

# Generate edge list as "from to"

# Key point: if there are no edges then the node won't be part of the edge, should be apparent from 
# the idea of edge list...anyway.
edge_list = []
for item in data['graph']:
    if item['type'] == 'EDGE':
        from_id = item['from']
        to_id = item['to']
        if from_id in node_ids and to_id in node_ids:
            edge_list.append(f"{from_id} {to_id}")

# Output edge list as newline-separated text
# print("\n".join(edge_list))

try:
    with open(sys.argv[2], "w", encoding='utf-8') as out_file:
        out_file.write("\n".join(edge_list))
    print("edgelist data successfully written to output.edgelist")
except IOError as e:
    print(f"Error writing to file: {e}")

# this is for this node2vec algorithm: https://github.com/snap-stanford/snap/tree/master/examples/node2vec
# sudo ./node2vec -i:graph/clientstotableswithjoins.edgelist -o:emb/clientstotableswithjoins.emb -l:3 -d:24 -p:0.3 -v
# which I ran locally. it is c++

# sudo ./scripts/node2vec -i:graph/clientstotableswithjoins.edgelist -o:emb/clientstotableswithjoins.emb -l:3 -d:24 -p:0.3 -v