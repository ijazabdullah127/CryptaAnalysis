
import enchant
dictionary = enchant.Dict("en_US")
def caesar_decrypt( text, shift):
        result = ""
        for char in text.upper():
            if char.isalpha():
                ascii_offset = ord('A')
                
                shifted = (ord(char) - ascii_offset - shift) % 26
                result += chr(shifted + ascii_offset)
            else:
                result += char
        return result

def score_text( text):
       
        words = text.split()
        valid_words = sum(1 for word in words if dictionary.check(word.lower()))
        return valid_words / len(words) if words else 0
