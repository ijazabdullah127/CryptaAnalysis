import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
import threading
import nltk
from nltk.corpus import words
import re

from VigenereCipher.util.transforms import Masker

from VigenereCipher.data.en import load_ngrams
from VigenereCipher.score.ngram import NgramScorer




from VigenereCipher.breaking.vigenere import VigenereBreak



nltk.download("words")
english_words = set(words.words())
decryption_results=[]

def decrypt_text(text,key,ngram):
        key_length = key
        ngram_value = ngram
        plaintext, masker = Masker.from_text(text)

        try:
            scorer = NgramScorer(load_ngrams(int(ngram_value)))
            breaker = VigenereBreak(int(key_length), scorer)
            decryption, score, keyfound = breaker.guess(plaintext)[0]
            result = [{
        'key_length': key_length,
        'Key': keyfound,
        'ngram': ngram_value,
        'decrypted_text': masker.extend(decryption),
     
        'english_percentage': calculate_english_word_percentage(masker.extend(decryption))
    }]
            return result
            
        except Exception as e:
            return(f"Error: Decryption failed: {e}")
        
def calculate_english_word_percentage(text):
        
        words_in_text = re.findall(r'\b\w+\b', text.lower())
        if not words_in_text:
            return 0
        english_word_count = sum(1 for word in words_in_text if word in english_words)
        return english_word_count / len(words_in_text)

def store_decryption_result( key_length,keyfound, ngram_value, decryption, english_word_percentage):
   
    result = {
        'key_length': key_length,
        'Key': keyfound,
        'ngram': ngram_value,
        'decrypted_text': decryption,
        
        'english_percentage': english_word_percentage
    }
    
    
    decryption_results.append(result)
        
        
    
    
    
def auto_decrypt_text(text):
        
        plaintext, masker = Masker.from_text(text)
        
        try:
            for key_length in range(1, 20):  # Example range for key lengths
                for ngram_value in range(1, 5):  # Example range for n-gram values
                    

                    scorer = NgramScorer(load_ngrams(ngram_value))
                    breaker = VigenereBreak(key_length, scorer)
                    decryption, score, keyfound = breaker.guess(plaintext)[0]

                    english_word_percentage = calculate_english_word_percentage( masker.extend(decryption))

                    store_decryption_result(key_length,keyfound, ngram_value, masker.extend(decryption), english_word_percentage)
                 
                    
                    
                    # Check for high score or high percentage of English words
                    if  english_word_percentage > 0.6:
                        
                        sorted_data = sorted(decryption_results, key=lambda x: x['english_percentage'], reverse=True)
                        return sorted_data
                    
        except Exception as e:
            return(f"Error Automatic decryption failed: {e}")



   

    

    
















