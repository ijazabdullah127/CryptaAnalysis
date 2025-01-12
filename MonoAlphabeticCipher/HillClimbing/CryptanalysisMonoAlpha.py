
from string import ascii_uppercase
import threading
import numpy as np
import time
from typing import List
import re
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import random


@dataclass
class DecryptionResult:
    score: float
    key: List[str]
    plaintext: str
    iteration: int
    time_taken: float
    def __str__(self):
        return (
            f"Best fitness score so far: {self.score:.2f} on iteration {self.iteration}\n"
            f"    Best Key: {''.join(self.key)}\n"
            f"    Best Plaintext: {self.plaintext}\n"
            f"    Time Taken: {self.time_taken:.6f} s"
        )


class MonoalphabeticSolver:
    def __init__(self, fitness_file: str, max_iterations: int = 1000, population_size: int = 4):
      
        self.fitness = self._load_fitness(fitness_file)
        self.max_iterations = max_iterations
        self.population_size = population_size
        self.running = False
        self.stop_flag = False
        
        self.best_result = DecryptionResult(
            score=-float('inf'),
            key=list(ascii_uppercase),
            plaintext="",
            iteration=0,
            time_taken=0
        )

    
    def _load_fitness(self, filename: str) -> dict:
     
        fitness_data = {}
        total = 0
        
        with open(filename, 'r') as f:
            for line in f:
                gram, count = line.strip().split()
                count = int(count)
                fitness_data[gram] = count
                total += count
        
      
        log_total = np.log10(total)
        fitness_data = {
            k: np.log10(v) - log_total 
            for k, v in fitness_data.items()
        }
        
        self.floor = np.log10(0.01) - log_total
        return fitness_data

    def decipher(self, text: str, key: List[str]) -> str:
      
        trans = str.maketrans(''.join(key), ascii_uppercase)
        

        result = []
        for char in text:
            if char.isalpha():
              
                result.append(char.upper().translate(trans))
            else:
              
                result.append(char)
                
        return ''.join(result)

    def calculate_fitness(self, text: str) -> float:
        """
        Calculate fitness score using only alphabetic characters.
        """
      
        letters_only = ''.join(c for c in text if c.isalpha())
        
        score = 0
        quad_len = 4
        
       
        if len(letters_only) < quad_len:
            return score
        
       
        quads = np.array([letters_only[i:i+quad_len] 
                         for i in range(len(letters_only) - quad_len + 1)])
        scores = np.array([self.fitness.get(quad, self.floor) for quad in quads])
        return float(np.sum(scores))

    def _hill_climb(self, ctext: str, start_key: List[str], iteration: int) -> DecryptionResult:
        """Single hill climbing attempt."""
        current_key = start_key[:]
        current_score = -float('inf')
        count = 0
        start_time = time.time()
        
        while count < self.max_iterations:
           
            a, b = random.sample(range(26), 2)
            new_key = current_key[:]
            new_key[a], new_key[b] = new_key[b], new_key[a]
            
           
            plaintext = self.decipher(ctext, new_key)
            score = self.calculate_fitness(plaintext)
            
            if score > current_score:
                current_score = score
                current_key = new_key[:]
                count = 0
               
                if score > self.best_result.score:
                    self.best_result = DecryptionResult(
                        score=score,
                        key=current_key[:],
                        plaintext=plaintext,
                        iteration=iteration,
                        time_taken=time.time() - start_time
                    )
                    
            count += 1
            
        return self.best_result

    

    def solve(self, ciphertext: str) -> list:
        print("Starting cryptanalysis with parallel hill climbing...")

        iteration = 0
        results = []
        self.running = True
        
        try:
            while iteration < self.max_iterations and not self.stop_flag:
                
                start_keys = [list(np.random.permutation(list(ascii_uppercase))) 
                            for _ in range(self.population_size)]
                
              
                with ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(self._hill_climb, ciphertext, key, iteration + i)
                        for i, key in enumerate(start_keys)
                    ]

                    for future in futures:
                        result = future.result()
                        results.append(result)

                iteration += self.population_size

        except Exception as e:
            print(f"\nError during analysis: {str(e)}\n")

        print("\nAnalysis completed. Sorting results by score...\n")

      
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        return sorted_results



def HillClimbing(ciphertext, max_iterations, population_size):
    solver=MonoalphabeticSolver('MonoAlphabeticCipher/HillClimbing/Files/quadgrams.txt',max_iterations, population_size) 
    results=solver.solve(ciphertext)
    return results

