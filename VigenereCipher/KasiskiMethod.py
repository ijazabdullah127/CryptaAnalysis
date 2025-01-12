import tkinter as tk
from collections import defaultdict
from itertools import combinations

def find_repeating_sequences(ciphertext, n=3):
    
    sequences = defaultdict(list)
    for i in range(len(ciphertext) - n + 1):
        seq = ciphertext[i:i + n]
        sequences[seq].append(i)
    return {seq: pos for seq, pos in sequences.items() if len(pos) > 1}

def calculate_distances(repeating_sequences):
   
    distances = []
    for positions in repeating_sequences.values():
        for (pos1, pos2) in combinations(positions, 2):
            distances.append(abs(pos2 - pos1))
    return distances

def factorize_distances(distances):
   
    factor_counts = defaultdict(int)
    for distance in distances:
        for i in range(2, min(25, distance + 1)):
            if distance % i == 0:
                factor_counts[i] += 1
    return sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)

def kasiski_analysis(ciphertext, n=3):
    
    repeating_sequences = find_repeating_sequences(ciphertext, n)
    distances = calculate_distances(repeating_sequences)
    factors = factorize_distances(distances)
    return factors

def analyze(text,chunksize):
    try:
        ciphertext = text.replace('\n', '').replace(' ', '').upper()
     
        ciphertext = ''.join(filter(str.isalpha, ciphertext))
        n = int(chunksize)
        if n <= 0:
            return "Chunk size must be greater than 0."
        key_lengths = kasiski_analysis(ciphertext, n=n)
        total_count = sum(count for i, count in key_lengths)
        result = "\n".join([f"Possible Key Size: {factor}, Confidence: {count / total_count * 100:.2f}%" for factor, count in key_lengths])
        return result
    except ValueError as e:
         return "Error"


