# DocMind — PDF Q&A Chatbot

A Dockerized Streamlit chatbot powered by your character-level GPT.  
Upload any PDF and ask questions; the app retrieves the most relevant  
passage and feeds it to your model as `Context: … Question: … Answer:`.

---

## Project Structure

```
docker_chatbot/
├── app.py                  ← Streamlit UI + inference logic
├── config.py               ← GPT hyper-parameters (copied from yours)
├── llm_training/
│   ├── __init__.py
│   ├── model.py            ← GPTLanguageModel
│   ├── tokenizer.py        ← CharTokenizer
│   └── config.py
├── model_weights.pth       ← your trained weights  ← ADD THIS
├── tokenizer.pkl           ← your pickled tokenizer ← ADD THIS
├── dataset/
│   └── train.txt           ← needed only if tokenizer.pkl is missing
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .streamlit/
    └── config.toml
```

---

## Quick Start

### 1. Place your artefacts

Copy `model_weights.pth` and `tokenizer.pkl` (produced by `train.py`)  
into the root of this folder.

### 2. Build & run with Docker Compose

```bash
docker compose up --build
```

Open **http://localhost:8501** in your browser.

### 3. (Alternative) run locally without Docker

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## How it works

1. **PDF upload** — PyMuPDF extracts all text from the uploaded PDF.
2. **Relevance retrieval** — for each question, sentences are ranked by  
   keyword overlap and the top chunk is selected as context.
3. **Prompt assembly** — the prompt follows your training format:
   ```
   Context: <retrieved chunk>
   Question: <user question>
   Answer:
   ```
4. **Generation** — the model auto-regressively generates tokens until  
   two consecutive newlines or `max_tokens` is reached.

---

## Tuning tips

| Setting | Effect |
|---------|--------|
| **Temperature** | Lower → more deterministic; higher → more creative |
| **Max tokens** | Longer answers (may degrade quality for small models) |
| **Context window** | More PDF text fed to model; watch block_size limits |

---

## Re-training

To extend the model on your own Q&A data, update `dataset/train.txt`  
and re-run `train.py`. Replace `model_weights.pth` + `tokenizer.pkl`.
