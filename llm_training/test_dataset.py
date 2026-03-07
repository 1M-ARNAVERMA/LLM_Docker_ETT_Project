import torch
from tokenizer import CharTokenizer
from dataset import get_batch

with open("dataset/train.txt", "r", encoding="utf-8") as f:
    text = f.read()

tokenizer = CharTokenizer(text)

data = torch.tensor(tokenizer.encode(text), dtype=torch.long)

x, y = get_batch(data, 4)

print("Input shape:", x.shape)
print("Target shape:", y.shape)

print("Sample input:", x[0])
print("Sample target:", y[0])