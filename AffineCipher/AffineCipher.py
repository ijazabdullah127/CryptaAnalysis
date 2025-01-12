
import string

from VigenereCipher.util.transforms import Masker

ALPHABET = string.ascii_uppercase
LETTERS = ['E', 'T', 'A', 'O', 'I', 'N', 'S', 'H', 'R', 'D', 'L', 'C', 'U', 'M', 'W', 'F', 'G', 'Y', 'P', 'B', 'V', 'K', 'J', 'X', 'Q', 'Z']
FREQUENCY = [0.12702, 0.09056, 0.08167, 0.07507, 0.06966, 0.06749, 0.06327, 0.06094, 0.05987, 0.04253, 0.04025, 0.02782, 0.02758, 0.02406, 0.02360, 0.02228, 0.02015, 0.01974, 0.01929, 0.01492, 0.00978, 0.00772, 0.00153, 0.00150, 0.00095, 0.00074]

ENGLISH_FREQUENCY = dict(zip(LETTERS, FREQUENCY))


def frequency(message):
    return {ch: message.count(ch)/len(message) for ch in ALPHABET}

def alphabetcorrelation(messagefrequency):
    return sum(ENGLISH_FREQUENCY[ch]*messagefrequency[ch] for ch in ALPHABET)

def modReverse(a, b):
        r, s, t = [min(a, b), max(a, b)], [1, 0], [0,1]
        while r[-1]!=1:
            q = r[-2]//r[-1]
            r.append(r[-2]-q*r[-1])
            s.append(s[-2]-q*s[-1])
            t.append(t[-2]-q*t[-1])
        return (s[-1]%r[1])

    

def decrypt(ciphertext, key):
        try:
            return ''.join(ALPHABET[modReverse(key[0], 26)*(ALPHABET.index(ch)-key[1])%26] for ch in ciphertext)
        except ZeroDivisionError:
            pass
        
def breakaffine(ciphertext):
    variants=[]
    text, masker = Masker.from_text(ciphertext)
    print(text)
    for i in range(25):
        for j in range(25):
            try:
                d=decrypt(text, (i, j))
                msg_frequency=frequency(d)
                variants.append((i, j, alphabetcorrelation(msg_frequency)))
            except:
                pass
    decrypter=(decrypt(text, (max(variants, key=lambda x: x[2])[0], max(variants, key=lambda x: x[2])[1])))
    return masker.extend(decrypter)

