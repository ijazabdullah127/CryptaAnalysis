
from pycipher import Caesar


class VigenereBreak(object):
    def __init__(self, key_length, scorer=None):
        self.key_length = key_length
        self.scorer = scorer
        self.alphabet_size = 26
    def scores(self, text):
        scores = [(i, self.scorer.score(self.decipher(text, i)))
                  for i in range(self.alphabet_size)]
        return sorted(scores, reverse=True, key=lambda t: t[1])
    
    def caesar_guess(self, text, n=3):
        return [(self.decipher(text, key), score, chr(key + 65))
                for key, score in self.scores(text)][:n]
    
    

    def decipher(self, text, key):
        return Caesar(key).decipher(text)
    
  
    def guess(self, text):
        ciphertext_chunks = self.chunk(text)
        plaintext_chunks, keys = self.break_caesars(ciphertext_chunks)
        plaintext = self.zip(plaintext_chunks)
        return [(plaintext, None, "".join(keys))]

    def chunk(self, text):
        chunks = {key: [] for key in range(self.key_length)}
        for i in range(len(text)):
            chunks[i % self.key_length].append(text[i])
        
        return ["".join(chunk) for _, chunk in chunks.items()]

    def break_caesars(self, chunks):
        plaintexts, keys = [], []
        for chunk in chunks:
            plaintext, score, key = self.caesar_guess(chunk, 1)[0]
            
            plaintexts.append(plaintext)
            keys.append(key)
        return plaintexts, keys

    def zip(self, chunks):
        result = []
        max_lenght = max([len(chunk) for chunk in chunks])
        for i in range(max_lenght):
            for chunk in chunks:
                if i < len(chunk):
                    result.append(chunk[i])
        return "".join(result)




