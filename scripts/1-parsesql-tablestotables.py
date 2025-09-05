
# "SQL hash","SQL text","Wait time (s)"
import csv
import json
import re
from collections import defaultdict
import hashlib
import sqlparse
from sqlparse.tokens import Keyword, DML, Whitespace, Punctuation
from sqlparse.sql import Identifier, IdentifierList, Token
import re
import sys

def is_meaningful(token):
    return not token.ttype in (Whitespace, Punctuation)

def normalize_table_label(table_name):
    # print(table_name)
    """
    Extracts the table label starting from the 'tbl' prefix, converts to lowercase,
    and ignores preceding schema/database names.
    """
    match = re.search(r'(tbl[a-zA-Z0-9_]+)', table_name, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    else:
        return table_name.lower() 


def extract_tables_and_joins(statement, sql_hash):
    # print(sql_hash)
    tables = {}
    
    client = None
    tokens = [t for t in statement.tokens if is_meaningful(t)]

    i = 0
    while i < len(tokens) - 1:
        token = tokens[i]

        # Detect client SELECT (client node)
        if token.ttype is DML and token.value.upper() == "SELECT":
            client = f"client{sql_hash}" # You can hash the query or index to give unique IDs if needed
        # Handle FROM clause
        if token.is_keyword and token.normalized == "FROM":
            next_token = tokens[i + 1]
            if isinstance(next_token, Identifier):
                # print(next_token.value)
                # print(next_token.get_alias())
                # table_name = next_token.get_name().lower()
                table_name = normalize_table_label(next_token.value)
                alias = next_token.get_alias() or table_name
                alias = alias.lower()
                tables[alias] = table_name
                yield (client, table_name, "FROM")

        # Handle JOIN clauses
        if token.is_keyword and "JOIN" in token.normalized:
            # Example: JOIN schema.tblX AS alias ON ...
            next_token = tokens[i + 1]
            if isinstance(next_token, Identifier):
                # print(next_token.get_alias())
                # table_name = next_token.get_name().lower()
                table_name = normalize_table_label(next_token.value)
                alias = next_token.get_alias() or table_name
                alias = alias.lower()
                tables[alias] = table_name
                yield ("JOIN", table_name)

        i += 1

    # print(tables)
    # Now parse the ON clauses to match aliases
    for token in tokens:
        if isinstance(token, sqlparse.sql.Comparison) or "ON" in token.value.upper():
            # print(token.value)
            on_clause = token.value
            aliases = re.findall(r'(\b\w+)\.', on_clause)
            
            # print(aliases)
            aliases = [a.lower() for a in aliases]
            if len(set(aliases)) >= 2:
                for a, b in zip(aliases, aliases[1:]):
                    # print(a, b)
                    # print(a in tables)
                    if a in tables and b in tables:
                        yield (tables[a], tables[b], "JOIN")

def parse_sql_to_graph(sql_text, hash):
    statements = sqlparse.split(sql_text)
    edges = set()
    nodes = set()

    for raw in statements:
        parsed = sqlparse.parse(raw)[0]
        for item in extract_tables_and_joins(parsed, hash):
            if len(item) == 3:
                src, tgt, etype = item
                nodes.add(src)
                nodes.add(tgt)
                edges.add((src, tgt, etype))

    return nodes, edges



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

# def normalize_table_label(table_name):
#     """
#     Extracts the table label starting from the 'tbl' prefix, converts to lowercase,
#     and ignores preceding schema/database names.
#     """
#     match = re.search(r'(tbl[a-zA-Z0-9_]+)', table_name, re.IGNORECASE)
#     if match:
#         return match.group(1).lower()
#     else:
#         return table_name.lower() 
    

def filter_tbl_tables(table_names):
    """
    Filters the list of table names, keeping only those that start with 'tbl' (case-insensitive),
    ignoring schema/database prefixes.
    """
    filtered = []
    # table_names = [item for item in table_names if item is not None]
    for table in table_names:
        # Normalize by extracting part starting with 'tbl'
        if (table == None): 
            continue

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

        if not select_pattern.search(sql_text):
            # print('skipping sql hash')
            # print(sql_hash)
            continue  # Skip non-SELECT queries

        normalized_hash = hashlib.md5(sql_text.encode()).hexdigest()
        if normalized_hash in normalized_sql_hashes:
            continue
        normalized_sql_hashes.add(normalized_hash)      

        nodes, edges = parse_sql_to_graph(sql_text, sql_hash)

        tables = []
        for table_name in nodes:
            tables.append(table_name)
        
        # remove any entities that aren't tables (tbl*)
        # tables = filter_tbl_tables(tables)

        # Add table nodes
        table_node_ids = [get_or_create_node(t) for t in tables]

        # Add client node , should work bc even though nodes has a client it will get filtered
        client_node_id = get_or_create_client_node(sql_hash)

        # Append edges according to the tables.
        for src, tgt, label in edges:
            # This is the problem, i need to check rather src == None
            # if (src not in node_map and src not in client_map) or tgt not in node_map: 
            #     continue
                           
            if label == "FROM" or src == None:
                graph.append({
                    "type": "EDGE",
                    "id": edge_id_counter,
                    "from": client_node_id,
                    "to": node_map[tgt]
                })             
            else:
                graph.append({
                    "type": "EDGE",
                    "id": edge_id_counter,
                    "from": node_map[src],
                    "to": node_map[tgt]
                })            
            edge_id_counter += 1  

# Final JSON structure
output = {
    "name": "Graph B",
    "desc": "Clients to tables with FROM, JOINs connect tables to tables",
    "graph": graph
}

try:
    with open("output/graphs/tablestotables/output.json", "w", encoding='utf-8') as json_file:
        json.dump(output, json_file, indent=4, ensure_ascii=False)
    print("JSON data successfully written to output.json")
except IOError as e:
    print(f"Error writing to file: {e}")

# print(json.dumps(client_map, indent=4))
# print(json.dumps(node_map, indent=4))
# print(json.dumps(output, indent=4))
