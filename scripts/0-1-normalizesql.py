# normalized and deduplicates sql 

import re
import csv
import sys

def normalize_sql(sql: str) -> str:
    # Remove variables like @brandCatalogId
    sql = re.sub(r'@\w+', '', sql)

    # Remove single-quoted string literals (even if broken at the end)
    sql = re.sub(r"'[^']*'?", "''", sql)

    # Strip integer literals (standalone numbers)
    # Matches integers not part of identifiers (avoids killing column names like col123)
    sql = re.sub(r'\b\d+\b', '', sql)

    # Collapse multiple commas (caused by stripping values in IN(...))
    sql = re.sub(r"(,\s*)+", ",", sql)

    # Replace things like "IN (,,,,)" with just "IN ()"
    sql = re.sub(r"in\s*\(\s*,*\s*\)", "in ()", sql, flags=re.IGNORECASE)

    # Collapse whitespace
    sql = re.sub(r'\s+', ' ', sql)

    # Remove numeric suffixes from table names
    sql = re.sub(r'(\b\w+)_\d+(?=\b|$)', r'\1', sql)

    return sql.strip().lower()

# print(normalize_sql(s))

def normalize_csv(input_file: str, output_file: str):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["SQL hash", "SQL text"]  # only keep hash + normalized

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            sql_hash = row["SQL hash"]
            sql_text = row["SQL text"]
            writer.writerow({
                "SQL hash": sql_hash,
                "SQL text": normalize_sql(sql_text)
            })

# Example usage
normalize_csv(sys.argv[1], "output/preprocessed/normalized.csv")