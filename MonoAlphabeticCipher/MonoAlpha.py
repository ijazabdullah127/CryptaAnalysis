
from typing import Counter
from MonoAlphabeticCipher.HillClimbing.CryptanalysisMonoAlpha import DecryptionResult

english_freq = {
            'E': 12.02, 'T': 9.10, 'A': 8.12, 'O': 7.68, 'I': 7.31,
            'N': 6.95, 'S': 6.28, 'R': 6.02, 'H': 5.92, 'D': 4.32,
            'L': 3.98, 'U': 2.88, 'C': 2.71, 'M': 2.61, 'F': 2.30,
            'Y': 2.11, 'W': 2.09, 'G': 2.03, 'P': 1.82, 'B': 1.49,
            'V': 1.11, 'K': 0.69, 'X': 0.17, 'Q': 0.11, 'J': 0.10,
            'Z': 0.07
        }
        
def calculate_frequencies(text):
     
        text = ''.join(c.upper() for c in text if c.isalpha())
        counter = Counter(text)
        total = len(text)
        
     
        frequencies = {letter: (count / total * 100) for letter, count in counter.items()}
        return frequencies


        

def suggest_mappings(frequencies):
        
        sorted_eng = sorted(english_freq.items(), key=lambda x: x[1], reverse=True)
        sorted_cipher = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
        
        
        suggestions = {}
        for (cipher_letter, i), (eng_letter, i) in zip(sorted_cipher, sorted_eng):
            suggestions[cipher_letter] = eng_letter
            
        return suggestions



def apply_mappings_to_ciphertext(ciphertext, mappings):
   
    
    translation_table = str.maketrans(mappings)
    
 
    plaintext = ciphertext.translate(translation_table)
    
    return plaintext

                
            