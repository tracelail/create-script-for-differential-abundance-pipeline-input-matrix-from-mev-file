"""Utility functions for working with FASTA files."""

def read_fasta(filepath):
    """
    Read a FASTA file and return sequences as a dictionary.
    
    Parameters
    ----------
    filepath : str
        Path to the FASTA file
        
    Returns
    -------
    dict
        Dictionary with sequence IDs as keys and sequences as values
    
    Examples
    --------
    >>> sequences = read_fasta('data/raw/sequences.fasta')
    >>> print(list(sequences.keys())[:5])
    ['seq1', 'seq2', 'seq3', 'seq4', 'seq5']
    """
    sequences = {}
    current_id = None
    current_seq = []
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                # Save the previous sequence if it exists
                if current_id is not None:
                    sequences[current_id] = ''.join(current_seq)
                # Start a new sequence
                current_id = line[1:].split()[0]  # Extract just the ID
                current_seq = []
            else:
                current_seq.append(line)
                
    # Save the last sequence
    if current_id is not None:
        sequences[current_id] = ''.join(current_seq)
        
    return sequences

def write_fasta(sequences, filepath):
    """
    Write sequences to a FASTA file.
    
    Parameters
    ----------
    sequences : dict
        Dictionary with sequence IDs as keys and sequences as values
    filepath : str
        Path to the output FASTA file
        
    Examples
    --------
    >>> sequences = {'seq1': 'ATGC', 'seq2': 'CGTA'}
    >>> write_fasta(sequences, 'data/processed/filtered_sequences.fasta')
    """
    with open(filepath, 'w') as f:
        for seq_id, sequence in sequences.items():
            f.write(f'>{seq_id}\n')
            # Write sequence in chunks of 60 characters
            for i in range(0, len(sequence), 60):
                f.write(f'{sequence[i:i+60]}\n')
