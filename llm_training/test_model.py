import torch
from backend.llm.tokenizer import CharTokenizer
from backend.llm.model import GPTLanguageModel

with open("dataset/train.txt", "r", encoding="utf-8") as f:
    text = f.read()

tokenizer = CharTokenizer(text)

vocab_size = tokenizer.vocab_size

model = GPTLanguageModel(vocab_size)

x = torch.randint(vocab_size, (4, 128))
y = torch.randint(vocab_size, (4, 128))

logits, loss = model(x, y)

print("Logits shape:", logits.shape)
print("Loss:", loss)