#!/usr/bin/env python
"""
Process raw sequence data.

This script filters sequences based on length and quality criteria.
"""
import os
import sys
import argparse

# Add the project directory to the path so we can import our module
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_dir)

from src.utils.fasta_utils import read_fasta, write_fasta

def filter_sequences(sequences, min_length=200, max_n_content=0.1):
    """
    Filter sequences based on length and N content.
    
    Parameters
    ----------
    sequences : dict
        Dictionary with sequence IDs as keys and sequences as values
    min_length : int, optional
        Minimum sequence length to keep. Default is 200.
    max_n_content : float, optional
        Maximum fraction of Ns allowed. Default is 0.1 (10%).
        
    Returns
    -------
    dict
        Filtered dictionary of sequences
    """
    filtered = {}
    for seq_id, sequence in sequences.items():
        if len(sequence) >= min_length:
            n_count = sequence.upper().count('N')
            n_fraction = n_count / len(sequence)
            if n_fraction <= max_n_content:
                filtered[seq_id] = sequence
    return filtered

def main():
    parser = argparse.ArgumentParser(description='Filter sequences by length and N content.')
    parser.add_argument('input_file', help='Input FASTA file')
    parser.add_argument('output_file', help='Output FASTA file')
    parser.add_argument('--min-length', type=int, default=200, help='Minimum sequence length')
    parser.add_argument('--max-n', type=float, default=0.1, help='Maximum fraction of Ns allowed')
    
    args = parser.parse_args()
    
    print(f"Reading sequences from {args.input_file}")
    sequences = read_fasta(args.input_file)
    print(f"Read {len(sequences)} sequences")
    
    filtered = filter_sequences(sequences, args.min_length, args.max_n)
    print(f"Filtered to {len(filtered)} sequences")
    
    write_fasta(filtered, args.output_file)
    print(f"Wrote filtered sequences to {args.output_file}")

if __name__ == '__main__':
    main()
