# Example Snakefile for bioinformatics workflow

# Define configuration file
configfile: "config/config.yaml"

# Define all target outputs
rule all:
    input:
        "results/processed_sequences.fasta"

# Example rule for filtering sequences
rule filter_sequences:
    input:
        "data/raw/{sample}.fasta"
    output:
        "results/{sample}_filtered.fasta"
    params:
        min_length = config["min_length"],
        max_n = config["max_n_content"]
    log:
        "logs/filter_sequences_{sample}.log"
    shell:
        """
        python src/data/process_sequences.py {input} {output}             --min-length {params.min_length}             --max-n {params.max_n} > {log} 2>&1
        """
