class CharTokenizer:

    def __init__(self, text):
        chars = sorted(list(set(text)))
        self.stoi = {ch: i for i, ch in enumerate(chars)}
        self.itos = {i: ch for i, ch in enumerate(chars)}
        self.vocab_size = len(chars)

    def encode(self, text):
        text = text.lower()
        return [self.stoi.get(c, 0) for c in text]

    def decode(self, tokens):
        return ''.join([self.itos[i] for i in tokens])
    
