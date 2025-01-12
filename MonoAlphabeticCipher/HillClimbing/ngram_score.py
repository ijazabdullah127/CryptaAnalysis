from math import log10
from typing import Dict
import numpy as np
from pathlib import Path

class NGramScore:

    
    def __init__(self, ngramfile: str | Path, sep: str = ' ') -> None:
       
        self.ngrams: Dict[str, float] = {}
        
    
        with Path(ngramfile).open('r') as f:
         
            entries = [line.strip().split(sep) for line in f]
            ngram_counts = {entry[0]: int(entry[1]) for entry in entries}
        
   
        self.N = sum(ngram_counts.values())
        
       
        log_N = log10(self.N)
        self.ngrams = {
            key: log10(count) - log_N 
            for key, count in ngram_counts.items()
        }
        
       
        self.L = len(next(iter(self.ngrams)))
        self.floor = log10(0.01) - log_N
        
        
        self._ngram_keys = np.array(list(self.ngrams.keys()))
        self._ngram_values = np.array(list(self.ngrams.values()))
    
    def score(self, text: str) -> float:
      
        if len(text) < self.L:
            return 0.0
        
        
        ngrams = [text[i:i + self.L] for i in range(len(text) - self.L + 1)]
        
       
        scores = np.zeros(len(ngrams))
        for i, ngram in enumerate(ngrams):
            if ngram in self.ngrams:
                scores[i] = self.ngrams[ngram]
            else:
                scores[i] = self.floor
                
        return float(np.sum(scores))
    
    def batch_score(self, texts: list[str]) -> list[float]:
     
        return [self.score(text) for text in texts]