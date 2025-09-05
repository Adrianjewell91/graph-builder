# ------- How to Use: -------- #
# source .venv/bin/activate;
# example: sudo sh pipeline.sh input/csn_product_global.csv

# ------- Clear all outputs -------- #
rm -rf output/*;

mkdir output/graphs;
mkdir output/embeddings;
mkdir output/edgelists;
mkdir output/cosmograph;
mkdir output/reports;
mkdir output/reports/connectedcomponents;

mkdir output/graphs/tablestotables;
mkdir output/embeddings/tablestotables;
mkdir output/edgelists/tablestotables;
mkdir output/cosmograph/tablestotables;
mkdir output/cosmograph/tablestotables/metadata;
mkdir output/reports/connectedcomponents/tablestotables;

mkdir output/graphs/clientstotables;
mkdir output/embeddings/clientstotables;
mkdir output/edgelists/clientstotables;
mkdir output/cosmograph/clientstotables;
mkdir output/cosmograph/clientstotables/metadata;
mkdir output/reports/connectedcomponents/clientstotables;

mkdir output/preprocessed;

# ------- Preprocessing -------- #
python3 scripts/0-1-normalizesql.py $1;
python3 scripts/0-2-deduplicate.py  output/preprocessed/normalized.csv 

# ------- Build Graph, Edgelists -------- #
python3 scripts/1-parsesql-tablestotables.py  output/preprocessed/deduplicated.csv;
python3 scripts/2-buildedgelist.py            output/graphs/tablestotables/output.json  output/edgelists/tablestotables/output.edgelist;

python3 scripts/1-parsesql-clientstotables.py output/preprocessed/deduplicated.csv;
python3 scripts/2-buildedgelist.py            output/graphs/clientstotables/output.json output/edgelists/clientstotables/output.edgelist;

# ------- Build Cosmograph Files -------- #
python3 scripts/3-buildcosmographedges.py    output/edgelists/tablestotables/output.edgelist  output/cosmograph/tablestotables/output.edgelist.csv;
python3 scripts/3-buildcosmographmetadata.py output/graphs/tablestotables/output.json         output/cosmograph/tablestotables/metadata/output.csv;

python3 scripts/3-buildcosmographedges.py    output/edgelists/clientstotables/output.edgelist output/cosmograph/clientstotables/output.edgelist.csv;
python3 scripts/3-buildcosmographmetadata.py output/graphs/clientstotables/output.json        output/cosmograph/clientstotables/metadata/output.csv;

# ------- Run Node2Vec -------- #
# Parameters:
# Input graph path (-i:)
# Output graph path (-o:)
# Number of dimensions. Default is 128 (-d:)
# Length of walk per source. Default is 80 (-l:)
# Number of walks per source. Default is 10 (-r:)
# Context size for optimization. Default is 10 (-k:)
# Number of epochs in SGD. Default is 1 (-e:)
# Return hyperparameter. Default is 1 (-p:)
# Inout hyperparameter. Default is 1 (-q:)
# Verbose output. (-v)
# Graph is directed. (-dr)
# Graph is weighted. (-w)
# Output random walks instead of embeddings. (-ow)
sudo ./scripts/4-node2vec -i:output/edgelists/clientstotables/output.edgelist -o:output/embeddings/clientstotables/output-directed.emb   -l:20 -dr -v;
sudo ./scripts/4-node2vec -i:output/edgelists/clientstotables/output.edgelist -o:output/embeddings/clientstotables/output-undirected.emb -l:20     -v;

sudo ./scripts/4-node2vec -i:output/edgelists/tablestotables/output.edgelist  -o:output/embeddings/tablestotables/output-directed.emb    -l:20 -dr -v;
sudo ./scripts/4-node2vec -i:output/edgelists/tablestotables/output.edgelist  -o:output/embeddings/tablestotables/output-undirected.emb  -l:20     -v;


# ------- Plot Embeddings -------- #

# In/Outside most-connected component.
# undirected shows homophily separation.
python3 scripts/5-plot-in-or-outside-most-connected-component.py output/embeddings/clientstotables/output-undirected.emb output/graphs/clientstotables/output.json output/edgelists/clientstotables/output.edgelist pca;
python3 scripts/5-plot-in-or-outside-most-connected-component.py output/embeddings/tablestotables/output-undirected.emb  output/graphs/tablestotables/output.json  output/edgelists/tablestotables/output.edgelist  pca;

# Client vs Table.  
# directed shows better structural equivalence (client and table have differen structural eq.)
python3 scripts/5-plot-clients-vs-tables.py output/embeddings/clientstotables/output-directed.emb output/graphs/clientstotables/output.json tsne;
# this one is worse than the others.
python3 scripts/5-plot-clients-vs-tables.py output/embeddings/tablestotables/output-directed.emb output/graphs/tablestotables/output.json tsne;

# ------- Report Connected Components -------- #
# There is typcially one massive connected component (about 1500 nodes) and a ton of small ones (btw 1 and 10 mostly)
python3 scripts/7-connectedcomponents.py output/edgelists/clientstotables/output.edgelist output/reports/connectedcomponents/clientstotables/output.csv;
python3 scripts/7-connectedcomponents.py output/edgelists/tablestotables/output.edgelist  output/reports/connectedcomponents/tablestotables/output.csv;

# ------- Research -------- #

# Vector Search: Only works for directed embeddings in the client-to-table.
# python3 scripts/vectorsearchmostdenselyconnectnode.py graphs/clientstotables/output.json embeddings/clientstotables/output-directed.emb;

