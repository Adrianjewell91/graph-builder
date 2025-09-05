import sys

def convert_edge_list(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        # Write CSV header
        outfile.write("source;target\n")

        for line in infile:
            parts = line.strip().split()
            if len(parts) != 2:
                continue  # skip malformed lines
            source, target = parts
            outfile.write(f"{source},{target}\n")

# Example usage
if __name__ == "__main__":
    convert_edge_list(sys.argv[1], sys.argv[2])
