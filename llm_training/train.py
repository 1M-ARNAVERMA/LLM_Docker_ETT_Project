import torch
from tokenizer import CharTokenizer
from dataset import get_batch
from model import GPTLanguageModel
import config

# load dataset
with open("dataset/train.txt", "r", encoding="utf-8") as f:
    text = f.read()

# tokenizer
tokenizer = CharTokenizer(text)

# encode dataset
data = torch.tensor(tokenizer.encode(text), dtype=torch.long)