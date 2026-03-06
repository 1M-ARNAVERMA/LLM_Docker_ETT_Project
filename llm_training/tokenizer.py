import torch

class CharTokenizer:

    def __init__(self, text):
        # get all unique characters
        chars = sorted(list(set(text)))

        # vocabulary size
        self.vocab_size = len(chars)

        # character → index
        self.stoi = {ch: i for i, ch in enumerate(chars)}

        # index → character
        self.itos = {i: ch for i, ch in enumerate(chars)}

    def encode(self, text):
        return [self.stoi[c] for c in text]

    def decode(self, tokens):
        return ''.join([self.itos[i] for i in tokens])
    
from tokenizer import CharTokenizer

# Load dataset text
with open("dataset/train.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Create tokenizer
tokenizer = CharTokenizer(text)

# Test word
test_text = "Docker"

encoded = tokenizer.encode(test_text)
decoded = tokenizer.decode(encoded)

print("Original:", test_text)
print("Encoded:", encoded)
print("Decoded:", decoded)
print("Vocabulary size:", tokenizer.vocab_size)