# chatbot.py

import torch

from document_processing.loader import load_document
from document_processing.chunker import chunk_text
from retrieval.vector_store import simple_search

from llm.model import GPTLanguageModel
from llm.tokenizer import CharTokenizer

import config


# Load LLM once (important)
def load_llm():
    with open("llm_training/dataset/train.txt", "r", encoding="utf-8") as f:
        text = f.read()

    tokenizer = CharTokenizer(text)

    model = GPTLanguageModel(tokenizer.vocab_size)
    model.load_state_dict(torch.load("llm_training/model_weights.pth"))

    model.eval()

    return model, tokenizer


model, tokenizer = load_llm()


# Prompt builder
def build_prompt(context, question):
    return f"""Context: {context}
Question: {question}
Answer:"""


# Text generation function
def generate_answer(prompt, max_new_tokens=40):

    tokens = torch.tensor(tokenizer.encode(prompt), dtype=torch.long).unsqueeze(0)

    for _ in range(max_new_tokens):

        tokens_cond = tokens[:, -config.block_size:]

        logits, _ = model(tokens_cond)

        logits = logits[:, -1, :]

        probs = torch.softmax(logits, dim=-1)

        next_token = torch.multinomial(probs, num_samples=1)

        tokens = torch.cat((tokens, next_token), dim=1)

    return tokenizer.decode(tokens[0].tolist())


# MAIN FUNCTION (this is what backend will call)
def answer_question(file_path, question):

    # 1. Load document
    text = load_document(file_path)

    # 2. Chunk it
    chunks = chunk_text(text)

    # 3. Retrieve relevant chunk
    top_chunks = simple_search(question, chunks, top_k=1)

    if not top_chunks:
        return "No relevant information found."

    context = top_chunks[0]

    # 4. Build prompt
    prompt = build_prompt(context, question)

    # 5. Generate answer
    response = generate_answer(prompt)

    return response