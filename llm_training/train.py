import torch
from tokenizer import CharTokenizer
from dataset import get_batch
from backend.llm.model import GPTLanguageModel
import config

# load dataset
with open("dataset/train.txt", "r", encoding="utf-8") as f:
    text = f.read()

# tokenizer
tokenizer = CharTokenizer(text)

# encode dataset
data = torch.tensor(tokenizer.encode(text), dtype=torch.long)

# model
model = GPTLanguageModel(tokenizer.vocab_size)

# optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)

# training loop
for iter in range(config.max_iters):

    xb, yb = get_batch(data, config.batch_size)

    logits, loss = model(xb, yb)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if iter % config.eval_interval == 0:
        print(f"step {iter}: loss {loss.item()}")

# save trained model
torch.save(model.state_dict(), "model_weights.pth")

print("Training finished. Model saved.")