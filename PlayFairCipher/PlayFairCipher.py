import math
import random
from collections import defaultdict
import re


from collections import deque
import random
from typing import Optional



import random

from collections import defaultdict
import math


class FitnessCalculator:
    def __init__(self, textfile="PlayFairCipher/files/4grams.txt"):
        self.dictionary = self.parse(textfile)
        self.total_quadgrams = self.get_total_quadgrams()

    def parse(self, file_name):
        quadgrams = defaultdict(int)
        with open(file_name, "r") as file:
            for line in file:
                key, value = line.split()
                quadgrams[key.upper()] = int(value)
        return quadgrams

    def get_total_quadgrams(self):
        return sum(self.dictionary.values())

    def quadgram_probability(self, key):
        return math.log10(self.dictionary.get(key.upper(), 1) / self.total_quadgrams)

    def log_probability(self, text):
        text = text.replace(" ", "")
        return sum(
            self.quadgram_probability(text[i:i + 4])
            for i in range(len(text) - 4 + 1)
        )
   

def to_matrix(key):
     key_matrix = [[None for _ in range(5)] for _ in range(5)]
     index = 0
    
     for i in range(5):
        for j in range(5):
            key_matrix[i][j] = key[index]
            index += 1
    
     return key_matrix


def matrix_to_string(key_matrix):
     sb = []
    
     for i in range(5):
        for j in range(5):
            sb.append(key_matrix[i][j])
    
     return ''.join(sb)

class KeyShuffler:
    rng = random.SystemRandom()  # Secure random number generator

    @staticmethod
    def shuffle_key(key: str) -> str:
        choice = KeyShuffler.rng.randint(0, 99)

        if choice in (0, 1):
            return KeyShuffler.key_reverse(key)
        elif choice in (2, 3):
            return KeyShuffler.key_swap_cols(key, KeyShuffler.rng.randint(0, 4), KeyShuffler.rng.randint(0, 4))
        elif choice in (4, 5):
            return KeyShuffler.key_swap_rows(key, KeyShuffler.rng.randint(0, 4), KeyShuffler.rng.randint(0, 4))
        elif choice in (6, 7):
            return KeyShuffler.key_flip_cols(key)
        elif choice in (8, 9):
            return KeyShuffler.key_flip_rows(key)
        else:
            ch1 = key[KeyShuffler.rng.randint(0, 24)]
            ch2 = key[KeyShuffler.rng.randint(0, 24)]
            return KeyShuffler.key_swap_chars(key, ch1, ch2)

    @staticmethod
    def key_swap_chars(key, one, two):
     return two.join(part.replace(two, one) for part in key.split(one))

    @staticmethod
    def key_reverse(key: str) -> str:
        return key[::-1]
    @staticmethod
    def key_swap_cols(key, c1, c2):
     c_key = list(key)
    
     for i in range(5):
        temp = c_key[i * 5 + c1]
        c_key[i * 5 + c1] = c_key[i * 5 + c2]
        c_key[i * 5 + c2] = temp
    
     return ''.join(c_key)

    @staticmethod
    def key_swap_rows(key, r1, r2):
     c_key = list(key)
    
     for i in range(5):
        temp = c_key[r1 * 5 + i]
        c_key[r1 * 5 + i] = c_key[r2 * 5 + i]
        c_key[r2 * 5 + i] = temp
    
     return ''.join(c_key)

    @staticmethod
    def key_flip_cols(key):
     key_matrix = to_matrix(key)
     
     for col in range(len(key_matrix[0])):
        for row in range(len(key_matrix) // 2):
            temp = key_matrix[row][col]
            key_matrix[row][col] = key_matrix[len(key_matrix) - row - 1][col]
            key_matrix[len(key_matrix) - row - 1][col] = temp
    
     return matrix_to_string(key_matrix)

    @staticmethod
    def key_flip_rows(key):
     key_matrix = to_matrix(key)
    
     for row in range(len(key_matrix)):
        for col in range(len(key_matrix[row]) // 2):
            temp = key_matrix[row][col]
            key_matrix[row][col] = key_matrix[row][len(key_matrix[row]) - col - 1]
            key_matrix[row][len(key_matrix[row]) - col - 1] = temp
    
     return matrix_to_string(key_matrix)

    



class Masker(object):
    def __init__(self, text, alphabet=r"[a-zA-Z]"):
        self.text = text  # the text which has additional characters
        self.alphabet = alphabet  # must be a regex defining the alphabet

        self.alphabet_mask = self._get_alphabet_mask()
        self.lowercase_mask = self._get_lowercase_mask()
        self.reduced_text, self.non_alphabet_chars = self._get_reduced_text()

    @staticmethod
    def from_text(text):
        masker = Masker(text)
        return masker.reduce(), masker

    def _get_alphabet_mask(self):
        return [1 if re.match(self.alphabet, char) else 0
                for char in list(self.text)]

    def _get_lowercase_mask(self):
        return [1 if str.islower(char) else 0 for char in list(self.text)]

    def _get_reduced_text(self):
        result = []
        non_alphabet_chars = []
        for i, char in enumerate(list(self.text)):
            if self.alphabet_mask[i] == 1:
                result.append(char.upper())
            else:
                non_alphabet_chars.append(char)
        return "".join(result), non_alphabet_chars

    def reduce(self):
        return self.reduced_text

    def extend(self, new_text):
        assert len(new_text) == sum(self.alphabet_mask), \
            "You must have the same chars"
        new_text = deque(new_text)
        chars_to_add = deque(self.non_alphabet_chars)
        result = []
        for i, indicator in enumerate(list(self.alphabet_mask)):
            if indicator == 1:
                char = new_text.popleft()
                if self.lowercase_mask[i] == 1:
                    char = char.lower()
                result.append(char)
            else:
                result.append(chars_to_add.popleft())
        return "".join(result)
















results=[]
mask=None
class SimulatedAnnealing:
    def __init__(self):
        self.fitness = FitnessCalculator()
        self.rand = random.Random()
        self.Shuffler=KeyShuffler()

    def solve(self, cipher, temperature,masker,debug=True):
        global mask
        mask=masker
        parent_key = cipher.key
        best_key = parent_key
        deciphered_text = cipher.decrypt(parent_key)
        best_text = deciphered_text
        parent_score = self.fitness.log_probability(deciphered_text)
        best_score = parent_score

        for temp in range(temperature, 0, -1):
            for i in range(50000):
                child_key = self.Shuffler.shuffle_key(parent_key)
                deciphered_text = cipher.decrypt(child_key)
                child_score = self.fitness.log_probability(deciphered_text)
                delta_score = child_score - parent_score

                if delta_score > 0:
                    parent_score = child_score
                    parent_key = child_key
                else:
                    if(math.exp(delta_score / temp) > self.rand.random()):
                     parent_score = child_score
                     parent_key = child_key  
                if parent_score > best_score:
                    best_score = parent_score
                    best_key = parent_key
                    best_text = deciphered_text
                    if debug:
                        self.debug_stats(best_key, best_score, best_text, temp)

            if parent_score == best_score:
                break
        results.append( {"key": best_key, "text": mask.extend(best_text), "score": best_score})
        return  results

   
    def debug_stats(self, key, score, text, temp):
        results.append({"key":key, "text": mask.extend(text), "score":  round(float(score), 5)})
       
masker=None


class PlayfairCipher:
    def __init__(self, text=None, key=None):
        self.digrams = self.create_digrams(text) if text else []
      #  self.keygen=KeyGenerator()
      #  self.key = self.keygen.generate_key()
        self.key="RCMVFPUQAOBDWNSHGXEYKLTZI"
        print(self.key)
    
    
    
    @staticmethod
    def create_digrams(text):
        digrams = [text[i:i+2] for i in range(0, len(text), 2)]
    
        return digrams
   
    def decrypt(self, key):
        plain_text = []
        for ngram in self.digrams:
            row1, col1 = divmod(key.index(ngram[0]), 5)
            row2, col2 = divmod(key.index(ngram[1]), 5)

            if col1 == col2:  
                plain_text.append(key[(row1 + 4) % 5 * 5 + col1])
                plain_text.append(key[(row2 + 4) % 5 * 5 + col2])
            elif row1 == row2:  
                plain_text.append(key[row1 * 5 + (col1 + 4 ) % 5])
                plain_text.append(key[row2 * 5 + (col2 + 4) % 5])
            else:  
                plain_text.append(key[row1 * 5 + col2])
                plain_text.append(key[row2 * 5 + col1])

        return "".join(plain_text)

    







def break_cipher(temperature, debug, text):
    cipher = PlayfairCipher(text)
    sa = SimulatedAnnealing()
    results = sa.solve(cipher, temperature,masker, debug)
    sorted_data = sorted(results , key=lambda x: x['score'], reverse=True)

    print(sorted_data)
    return sorted_data
    
    
def playfair(text,temperature):
    global masker
    temp = temperature
    debug_mode = True
    ciphertext,masker=Masker.from_text(text)
    return break_cipher(temp, debug_mode,ciphertext)


''' 
class KeyGenerator:
    PLAYFAIR_ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    _instance = None

    def __init__(self):
        self.rng = random.SystemRandom()  # Secure random number generator

    @classmethod
    def get_instance(cls) -> 'KeyGenerator':
        if cls._instance is None:
            cls._instance = KeyGenerator()
        return cls._instance

    def generate_key(self) -> str:
        sequence = list(self.PLAYFAIR_ALPHABET)
        self.rng.shuffle(sequence)
        return ''.join(sequence)

    def generate_key_with_secret(self, secret: str) -> str:
        key = (secret.upper().replace("J", "I") + self.PLAYFAIR_ALPHABET)
        return self.remove_duplicates(key)

    @staticmethod
    def remove_duplicates(string: str) -> str:
        seen = set()
        return ''.join(ch for ch in string if not (ch in seen or seen.add(ch)))
'''