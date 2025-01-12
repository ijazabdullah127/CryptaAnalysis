
import random
from AffineCipher.AffineCipher import ALPHABET, ENGLISH_FREQUENCY, frequency
from PolyBiusSquareCipher.PolyBiusSquareCipher import trigramfitness
from VigenereCipher.util.transforms import Masker


def offset(char, offset):
    return ALPHABET[(ALPHABET.index(char)+offset)%26]

  

def buildAlphabet(key):
        offseted_alph = ''.join(map(offset, list(ALPHABET), [ALPHABET.index(key.upper()[-1])+1,]*len(ALPHABET)))
        return (key.upper()+''.join([ch for ch in offseted_alph if not (ch in key.upper())]))


def decrypt(ciphertex, key):
        cipher_alph = buildAlphabet(key)
        return ''.join(ALPHABET[cipher_alph.index(ch.upper())] for ch in ciphertex)

def breaksubstitutioncipher(ciphertext):
    text,masker=Masker.from_text(ciphertext)
    eng_freq = sorted(ENGLISH_FREQUENCY.items(), key=lambda x: x[1], reverse=True)
    ciph_freq = sorted(frequency(text).items(), key=lambda x: x[1], reverse=True)
    parentkey = [ch[0] for ch in sorted(map(lambda x, y: (x[0], y[0]), ciph_freq, eng_freq), key=lambda x: x[1])]
    d = decrypt(text, ''.join(parentkey))
    fitness = trigramfitness(d)
    count = 0
    while count < 1500:
        i = random.randrange(26)
        j = random.randrange(26)
        childkey = parentkey[:]
        childkey[i], childkey[j] = childkey[j], childkey[i]
        d = decrypt(text, ''.join(childkey))
        if trigramfitness(d) > fitness:
            parentkey = childkey
            fitness = trigramfitness(d)
            count = 0
        count += 1
    return masker.extend(decrypt(text, ''.join(parentkey)))