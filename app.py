import streamlit as st
import torch
import pickle
import os
import sys
import re

# ── PDF extraction ──────────────────────────────────────────────────────────
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

# ── Add llm_training package path ───────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from llm_training.tokenizer import CharTokenizer
from llm_training.model import GPTLanguageModel
import config

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocMind — PDF Q&A",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0e0e10;
    color: #e8e6e0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #13131a;
    border-right: 1px solid #2a2a3a;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: 'Syne', sans-serif;
    color: #c8ff57;
}

/* ── Main title ── */
.main-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: -0.02em;
    color: #c8ff57;
    margin-bottom: 0;
    line-height: 1.1;
}
.main-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: #6b6b7e;
    margin-top: 4px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Chat messages ── */
.msg-user {
    background: #1a1a28;
    border: 1px solid #2e2e42;
    border-left: 3px solid #c8ff57;
    border-radius: 6px 6px 6px 0;
    padding: 12px 16px;
    margin: 10px 0;
    font-size: 0.9rem;
    color: #e8e6e0;
}
.msg-bot {
    background: #161620;
    border: 1px solid #232335;
    border-left: 3px solid #5555cc;
    border-radius: 6px 6px 0 6px;
    padding: 12px 16px;
    margin: 10px 0;
    font-size: 0.9rem;
    color: #d4d2cc;
}
.msg-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 4px;
    opacity: 0.55;
}
.msg-user .msg-label { color: #c8ff57; }
.msg-bot  .msg-label { color: #8888ee; }

/* ── Input box ── */
.stTextInput > div > div > input {
    background: #1a1a28 !important;
    border: 1px solid #2e2e42 !important;
    border-radius: 6px !important;
    color: #e8e6e0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.88rem !important;
    padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #c8ff57 !important;
    box-shadow: 0 0 0 1px #c8ff57 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #c8ff57 !important;
    color: #0e0e10 !important;
    border: none !important;
    border-radius: 5px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    padding: 8px 20px !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── Divider ── */
hr { border-color: #2a2a3a !important; }

/* ── File uploader ── */
[data-testid="stFileUploadDropzone"] {
    background: #13131a !important;
    border: 1px dashed #3a3a55 !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #c8ff57 !important;
}

/* ── Status / info boxes ── */
.stAlert { border-radius: 6px !important; }

/* ── PDF context preview ── */
.context-box {
    background: #111118;
    border: 1px solid #232335;
    border-radius: 6px;
    padding: 12px;
    font-size: 0.78rem;
    color: #7070a0;
    max-height: 180px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-family: 'DM Mono', monospace;
}

/* ── Metrics ── */
.stat-pill {
    display: inline-block;
    background: #1a1a28;
    border: 1px solid #2e2e42;
    border-radius: 4px;
    padding: 3px 10px;
    font-size: 0.74rem;
    color: #888;
    margin-right: 6px;
}
.stat-val { color: #c8ff57; font-weight: 600; }

/* ── Scroll anchor ── */
#chat-bottom { height: 1px; }

/* ── Generation config sliders ── */
.stSlider > div > div > div > div {
    background: #c8ff57 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers ─────────────────────────────────────────────────────────────────

WEIGHTS_PATH  = os.path.join(BASE_DIR, "model_weights.pth")
TOKENIZER_PATH = os.path.join(BASE_DIR, "tokenizer.pkl")
TRAIN_TEXT_PATH = os.path.join(BASE_DIR, "dataset", "train.txt")


@st.cache_resource(show_spinner=False)
def load_model_and_tokenizer():
    """Load model weights + tokenizer once, cache forever."""
    # prefer pickled tokenizer (trained vocab) if available
    if os.path.exists(TOKENIZER_PATH):
        with open(TOKENIZER_PATH, "rb") as f:
            tokenizer = pickle.load(f)
    elif os.path.exists(TRAIN_TEXT_PATH):
        with open(TRAIN_TEXT_PATH, "r", encoding="utf-8") as f:
            text = f.read()
        tokenizer = CharTokenizer(text)
    else:
        raise FileNotFoundError(
            "Neither tokenizer.pkl nor dataset/train.txt found. "
            "Please place them next to app.py."
        )

    model = GPTLanguageModel(tokenizer.vocab_size)

    if os.path.exists(WEIGHTS_PATH):
        state = torch.load(WEIGHTS_PATH, map_location="cpu")
        model.load_state_dict(state)
    else:
        st.warning("⚠️  model_weights.pth not found — using random weights.")

    model.eval()
    return tokenizer, model


def extract_pdf_text(uploaded_file) -> str:
    """Extract all text from a PDF using PyMuPDF."""
    if not HAS_PYMUPDF:
        return ""
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text())
    return "\n".join(pages)


def find_relevant_context(pdf_text: str, question: str, max_chars: int = 500) -> str:
    """
    Simple relevance: score each sentence by keyword overlap with the question,
    return the top-scoring chunk capped at max_chars.
    """
    q_words = set(re.sub(r"[^\w\s]", "", question.lower()).split())
    sentences = re.split(r"(?<=[.!?])\s+", pdf_text)

    scored = []
    for s in sentences:
        s_words = set(re.sub(r"[^\w\s]", "", s.lower()).split())
        overlap = len(q_words & s_words)
        scored.append((overlap, s))

    scored.sort(key=lambda x: -x[0])
    context = " ".join(s for _, s in scored[:8])
    return context[:max_chars].strip()


def generate_answer(
    tokenizer: CharTokenizer,
    model: GPTLanguageModel,
    context: str,
    question: str,
    max_new_tokens: int = 200,
    temperature: float = 0.8,
) -> str:
    """
    Build a prompt in the training format and auto-regressively generate.
    """
    # Truncate context to fit block_size budget
    budget = config.block_size - 60  # leave room for Q + "Answer:"
    context_trimmed = context[:budget]

    prompt = f"Context: {context_trimmed}\nQuestion: {question}\nAnswer:"

    tokens = torch.tensor(
        tokenizer.encode(prompt), dtype=torch.long
    ).unsqueeze(0)

    answer_tokens: list[int] = []
    stop_seq = [
        tokenizer.encode("\n\n"),
        tokenizer.encode("\nContext"),
        tokenizer.encode("\nQuestion"),
    ]
    stop_len = 2  # stop after 2 consecutive newlines

    newline_id = tokenizer.stoi.get("\n", -1)
    nl_count = 0

    with torch.no_grad():
        for _ in range(max_new_tokens):
            tokens_cond = tokens[:, -config.block_size:]
            logits, _ = model(tokens_cond)
            logits = logits[:, -1, :] / temperature
            probs = torch.softmax(logits, dim=-1)
            next_tok = torch.multinomial(probs, num_samples=1)
            tid = next_tok.item()
            answer_tokens.append(tid)
            tokens = torch.cat((tokens, next_tok), dim=1)

            # simple stop: two newlines in a row
            if tid == newline_id:
                nl_count += 1
                if nl_count >= stop_len:
                    break
            else:
                nl_count = 0

    answer = tokenizer.decode(answer_tokens).strip()
    # strip trailing prompt artifacts
    for marker in ["\nContext:", "\nQuestion:", "\nAnswer:"]:
        if marker in answer:
            answer = answer[: answer.index(marker)]
    return answer.strip()


# ── Session state ────────────────────────────────────────────────────────────

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": "user"|"bot", "text": str}

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📄 DocMind")
    st.markdown("<div style='font-size:0.78rem;color:#555;margin-top:-10px;'>Character-level GPT · PDF Q&A</div>", unsafe_allow_html=True)
    st.divider()

    st.markdown("### Upload PDF")
    pdf_file = st.file_uploader(
        label="Drop a PDF here",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if pdf_file is not None:
        if pdf_file.name != st.session_state.pdf_name:
            if not HAS_PYMUPDF:
                st.error("PyMuPDF not installed. Run: `pip install pymupdf`")
            else:
                with st.spinner("Extracting text…"):
                    text = extract_pdf_text(pdf_file)
                if text.strip():
                    st.session_state.pdf_text = text
                    st.session_state.pdf_name = pdf_file.name
                    st.session_state.chat_history = []
                    st.success(f"✓ {pdf_file.name}")
                else:
                    st.error("Could not extract text. Is it a scanned image PDF?")
    elif st.session_state.pdf_name:
        st.info(f"📎 {st.session_state.pdf_name}")

    st.divider()

    st.markdown("### Generation Settings")
    max_tokens = st.slider("Max tokens", 50, 400, 200, 10)
    temperature = st.slider("Temperature", 0.1, 1.5, 0.8, 0.05,
                            help="Higher = more creative, lower = more focused")
    context_window = st.slider("Context window (chars)", 100, 500, 300, 50,
                               help="How many PDF chars to feed as context")

    st.divider()

    if st.button("🗑  Clear chat"):
        st.session_state.chat_history = []
        st.rerun()

    # PDF stats
    if st.session_state.pdf_text:
        words = len(st.session_state.pdf_text.split())
        chars = len(st.session_state.pdf_text)
        st.markdown(
            f"<div style='font-size:0.75rem;color:#555;'>"
            f"<span class='stat-pill'>words <span class='stat-val'>{words:,}</span></span>"
            f"<span class='stat-pill'>chars <span class='stat-val'>{chars:,}</span></span>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ── Main area ────────────────────────────────────────────────────────────────

col_title, _ = st.columns([3, 1])
with col_title:
    st.markdown('<div class="main-title">DocMind</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-sub">PDF-grounded Q&A · Character-level GPT</div>',
        unsafe_allow_html=True,
    )

st.divider()

# Load model (cached)
try:
    with st.spinner("Loading model…"):
        tokenizer, model = load_model_and_tokenizer()
    model_loaded = True
except FileNotFoundError as e:
    st.error(f"**Model load error:** {e}")
    model_loaded = False

# Warn if no PDF yet
if not st.session_state.pdf_text and model_loaded:
    st.info("👈  Upload a PDF in the sidebar to start asking questions.")

# ── Chat display ─────────────────────────────────────────────────────────────

chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="msg-user"><div class="msg-label">You</div>{msg["text"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="msg-bot"><div class="msg-label">DocMind</div>{msg["text"]}</div>',
                unsafe_allow_html=True,
            )

# ── Input ────────────────────────────────────────────────────────────────────

if model_loaded and st.session_state.pdf_text:
    with st.container():
        cols = st.columns([8, 1])
        with cols[0]:
            user_q = st.text_input(
                "Ask a question about the PDF",
                placeholder="e.g. What is the main topic of this document?",
                label_visibility="collapsed",
                key="question_input",
            )
        with cols[1]:
            send = st.button("Ask →")

    if send and user_q.strip():
        question = user_q.strip()

        # retrieve relevant context
        context = find_relevant_context(
            st.session_state.pdf_text, question, max_chars=context_window
        )

        # store user message
        st.session_state.chat_history.append({"role": "user", "text": question})

        # generate answer
        with st.spinner("Thinking…"):
            answer = generate_answer(
                tokenizer, model, context, question,
                max_new_tokens=max_tokens,
                temperature=temperature,
            )

        if not answer:
            answer = "(The model returned an empty response. Try adjusting temperature or context window.)"

        st.session_state.chat_history.append({"role": "bot", "text": answer})
        st.rerun()

elif model_loaded and not st.session_state.pdf_text:
    pass  # info already shown above

# ── Context preview expander ─────────────────────────────────────────────────
if st.session_state.pdf_text and st.session_state.chat_history:
    last_q = next(
        (m["text"] for m in reversed(st.session_state.chat_history) if m["role"] == "user"),
        None,
    )
    if last_q:
        with st.expander("🔍 Last retrieved context snippet", expanded=False):
            ctx = find_relevant_context(
                st.session_state.pdf_text, last_q, max_chars=context_window
            )
            st.markdown(f'<div class="context-box">{ctx}</div>', unsafe_allow_html=True)
