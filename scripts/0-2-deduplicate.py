import csv
import sys

def deduplicate_csv(input_file: str, output_file: str):
    seen = set()
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            norm_sql = row["SQL text"]

            if norm_sql in seen:
                continue  # skip duplicates
            seen.add(norm_sql)

            writer.writerow(row)


deduplicate_csv(sys.argv[1], "output/preprocessed/deduplicated.csv")