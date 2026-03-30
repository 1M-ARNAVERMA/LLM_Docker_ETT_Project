# chatbot.py
import torch
import os
import pickle

import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from document_processing.loader import load_document
from document_processing.chunker import chunk_text
from retrieval.vector_store import simple_search

from llm_training.model import GPTLanguageModel

import config

# Load LLM once (important)
def load_llm():

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    import sys
    sys.path.append(os.path.join(BASE_DIR, "llm_training"))

    tokenizer_path = os.path.join(BASE_DIR, "llm_training", "tokenizer.pkl")
    model_path = os.path.join(BASE_DIR, "llm_training", "model_weights.pth")

    import pickle
    with open(tokenizer_path, "rb") as f:
        tokenizer = pickle.load(f)

    model = GPTLanguageModel(tokenizer.vocab_size)
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))

    model.eval()

    return model, tokenizer


model, tokenizer = load_llm()


# Prompt builder (simplified for better results)
def build_prompt(context, question):
    return f"""Context: {context}

Question: {question}

Answer:"""


# Text generation function
def generate_answer(prompt, context, max_new_tokens=40):

    tokens = torch.tensor(tokenizer.encode(prompt), dtype=torch.long).unsqueeze(0)

    for _ in range(max_new_tokens):

        tokens_cond = tokens[:, -config.block_size:]

        logits, _ = model(tokens_cond)

        logits = logits[:, -1, :]

        probs = torch.softmax(logits, dim=-1)

        next_token = torch.multinomial(probs, num_samples=1)

        tokens = torch.cat((tokens, next_token), dim=1)

    output = tokenizer.decode(tokens[0].tolist())

    # Extract only answer part
    if "Answer" in output:
        output = output.split("Answer")[-1]

    # Remove context repetition
    output = output.lower().replace(context.lower(), "")

    # Clean final output
    return output.strip().split("\n")[0]


# MAIN FUNCTION (this is what backend will call)
def answer_question(file_path, question):

    # 1. Load document
    text = load_document(file_path)

    # 2. Chunk it
    chunks = chunk_text(text)

    # 3. Retrieve relevant chunks
    top_chunks = simple_search(question, chunks, top_k=1)

    if not top_chunks:
        return "Information not found in the document."

    # Combine top chunks
    context = " ".join(top_chunks)

    print("Retrieved context:", context)

    # 🔥 Not found detection (NEW)
    import re

    clean_question = re.sub(r'[^\w\s]', '', question.lower())
    keywords = [w for w in clean_question.split() if w not in ["what", "is", "the", "a", "an"]]
    
    if not any(word in context.lower() for word in keywords):
        return "Information not found in the document."

    # 🔥 SMART RULE-BASED ANSWERING
    if question.lower().startswith("what is"):
        return context.split(".")[0].strip()

    # 4. Build prompt
    prompt = build_prompt(context, question)

    # 5. Fallback to LLM
    response = generate_answer(prompt, context)

    # fallback safety
    if len(response) < 3:
        return context.split(".")[0].strip()

    return response