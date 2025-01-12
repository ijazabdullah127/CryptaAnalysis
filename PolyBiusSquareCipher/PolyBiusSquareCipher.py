import random
import pickle
import string
trigram_file = open('PolyBiusSquareCipher/Files/trigrams', 'rb')
ENGLISH_TRIGRAMS = pickle.load(trigram_file)
ALPHABET = string.ascii_uppercase
def decrypt(ciphertext, key, letters):
        c_list = [ciphertext[i-1]+ciphertext[i] for i in range(1, len(ciphertext), 2)]
        return ''.join([key[letters.index(ch[0])*5+letters.index(ch[1])] for ch in c_list])

def counttrigrams(text):
    return len(text)-3+1


def trigramfrequency(text, trigram):
    return text.count(trigram)/counttrigrams(text)
def trigramfitness(text):
    return sum([trigramfrequency(text, k) for k in ENGLISH_TRIGRAMS.keys()])  
def generatekey():
        alph = ALPHABET.replace('J', '')
        l = list(alph)
        random.shuffle(l)
        return ''.join(l)
def breakpolybiussquare(ciphertext):
    ciphertext = ciphertext.replace(" ", "")
    result=[]
    for i in range(10):
        parentkey = list(generatekey())
        d = decrypt(ciphertext, parentkey, '12345')
        fitness = trigramfitness(d)
        count = 0
        while count < 1500:
            i = random.randrange(25)
            j = random.randrange(25)
            childkey = parentkey[:]
            childkey[i], childkey[j] = childkey[j], childkey[i]
            d = decrypt(ciphertext, childkey, '12345')
            if trigramfitness(d) > fitness:
                parentkey = childkey
                fitness = trigramfitness(d)
                count = 0
            count += 1
        result.append(decrypt(ciphertext, parentkey, '12345'))
    return max(result, key=trigramfitness)


