
import random
from AffineCipher.AffineCipher import ALPHABET
from PolyBiusSquareCipher.PolyBiusSquareCipher import trigramfitness



def letterscount(message):
    return {ch: message.count(ch) for ch in ALPHABET}

def indexcoincidence(message):
    lettersnumbers, length = letterscount(message), len(message)
    return sum([dict.get(lettersnumbers, num, 0) * (dict.get(lettersnumbers, num, 0) - 1) / (length * (length - 1)) for num in ALPHABET])

def transformkey(key):
        return [i[0] for i in sorted([i for i in enumerate(key)], key=lambda x: x[1])]
def decrypt(ciphertext, key):
        return  ''.join([ciphertext[transformkey(key).index(i)*len(ciphertext)//len(key)+k] for k in range(len(ciphertext)//len(key)) for i in range(len(key))])


def breakcolumnarcipher(ciphertext, keysize):
    
    result = []
    for cnt in range(10):
        parentkey = list(ALPHABET[:keysize])
        d = decrypt( ciphertext, ''.join(parentkey))
        fitness = trigramfitness(d)
        count = 0
        while count < 1500:
            i = random.randrange(keysize)
            j = random.randrange(keysize)
            childkey = parentkey[:]
            childkey[i], childkey[j] = childkey[j], childkey[i]
            d = decrypt( ciphertext, ''.join(childkey))
            if trigramfitness(d) > fitness:
                parentkey = childkey
                fitness = trigramfitness(d)
                count = 0
            count += 1
        result.append(decrypt( ciphertext, ''.join(parentkey)))
    return max(result, key=trigramfitness)