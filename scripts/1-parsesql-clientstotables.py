# This script parses the SQL logs and builds a mapping between tables and clients.
# Every sql hash is a client and all the referenced tables get an edge to the client.

# The complexity of the sql is not accounted for. 
# The script attempts to remove duplicates.

# "SQL hash","SQL text","Wait time (s)"
import csv
import json
import re
from collections import defaultdict
import hashlib
import sys

# Store normalized SQL hashes to detect duplicates
normalized_sql_hashes = set()


input_file = sys.argv[1]
graph = []
node_id_counter = 1
edge_id_counter = 1
node_map = {}  # maps label -> node_id
client_map = {}  # maps SQL hash -> client node_id

# Regex patterns
table_pattern = re.compile(r'(FROM|JOIN)\s+([a-zA-Z0-9_.#]+)', re.IGNORECASE)
# select_pattern = re.compile(r'^\s*SELECT', re.IGNORECASE)
# I removed the requirement for the sql to start at the beginning of the line.
select_pattern = re.compile(r'\s*SELECT', re.IGNORECASE)

def normalize_table_label(table_name):
    """
    Extracts the table label starting from the 'tbl' prefix, converts to lowercase,
    and ignores preceding schema/database names.
    """
    match = re.search(r'(tbl[a-zA-Z0-9_]+)', table_name, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    else:
        return table_name.lower() 
    

def filter_tbl_tables(table_names):
    """
    Filters the list of table names, keeping only those that start with 'tbl' (case-insensitive),
    ignoring schema/database prefixes.
    """
    filtered = []
    for table in table_names:
        # Normalize by extracting part starting with 'tbl'
        match = re.search(r'(tbl[a-zA-Z0-9_]+)', table, re.IGNORECASE)
        if match:
            filtered.append(match.group(1).lower())
    return filtered    


def get_or_create_node(label):
    global node_id_counter
    if label not in node_map:
        node_map[label] = node_id_counter
        graph.append({
            "type": "NODE",
            "id": node_id_counter,
            "label": label
        })
        node_id_counter += 1
    return node_map[label]

def get_or_create_client_node(sql_hash):
    global node_id_counter
    label = f"client{sql_hash}"
    if sql_hash not in client_map:
        client_map[sql_hash] = node_id_counter
        graph.append({
            "type": "NODE",
            "id": node_id_counter,
            "label": label
        })
        node_id_counter += 1
    return client_map[sql_hash]

with open(input_file, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row["SQL hash"])
        sql_hash = row["SQL hash"]
        sql_text = row["SQL text"]

        # if not select_pattern.search(sql_text):
            # print('skipping sql hash')
            # print(sql_hash)
            # continue  # Skip non-SELECT queries

        # print(normalized_sql)

        normalized_hash = hashlib.md5(sql_text.encode()).hexdigest()
        if normalized_hash in normalized_sql_hashes:
            continue
        normalized_sql_hashes.add(normalized_hash)        

        tables = []
        for match in table_pattern.finditer(sql_text):
            table_name = match.group(2)
            tables.append(normalize_table_label(table_name))
        
        # remove any entities that aren't tables (tbl*)
        tables = filter_tbl_tables(tables)

        # Add table nodes
        table_node_ids = [get_or_create_node(t) for t in tables]

        # Add client node
        client_node_id = get_or_create_client_node(sql_hash)

        # global edge_id_counter # This broke the graph and I don't know why.

        for i in range(0, len(table_node_ids)):
            graph.append({
                "type": "EDGE",
                "id": edge_id_counter,
                "from": client_node_id,
                "to": table_node_ids[i]
            })
            edge_id_counter += 1        


# Final JSON structure
output = {
    "name": "Graph A",
    "desc": "Client connects to all tables",
    "graph": graph
}

try:
    with open("output/graphs/clientstotables/output.json", "w", encoding='utf-8') as json_file:
        json.dump(output, json_file, indent=4, ensure_ascii=False)
    print("JSON data successfully written to output.json")
except IOError as e:
    print(f"Error writing to file: {e}")

# print(json.dumps(client_map, indent=4))
# print(json.dumps(node_map, indent=4))
# print(json.dumps(output, indent=4))
