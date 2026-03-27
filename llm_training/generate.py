import torch
import config
from llm_training.tokenizer import CharTokenizer
from llm_training.model import GPTLanguageModel

# load dataset text
with open("dataset/train.txt", "r", encoding="utf-8") as f:
    text = f.read()

# tokenizer
tokenizer = CharTokenizer(text)

# initialize model
model = GPTLanguageModel(tokenizer.vocab_size)

# load trained weights
model.load_state_dict(torch.load("model_weights.pth"))

model.eval()

# generation function
def generate_text(prompt, max_new_tokens=200):

    tokens = torch.tensor(tokenizer.encode(prompt), dtype=torch.long).unsqueeze(0)

    for _ in range(max_new_tokens):

        tokens_cond = tokens[:, -config.block_size:]

        logits, _ = model(tokens_cond)

        logits = logits[:, -1, :]

        probs = torch.softmax(logits, dim=-1)

        next_token = torch.multinomial(probs, num_samples=1)

        tokens = torch.cat((tokens, next_token), dim=1)

    return tokenizer.decode(tokens[0].tolist())


# test prompt
prompt = "Context: Docker is a containerization platform.\nQuestion: What is Docker?\nAnswer:"

output = generate_text(prompt)

print("\nGenerated Response:\n")
print(output)