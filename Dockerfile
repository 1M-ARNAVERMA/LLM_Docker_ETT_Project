# ── Base ────────────────────────────────────────────────────────────────────
FROM python:3.10-slim

# ── System deps ─────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ────────────────────────────────────────────────────────
WORKDIR /app

# ── Python deps ─────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project files ───────────────────────────────────────────────────────
COPY . .

# ── Streamlit config ─────────────────────────────────────────────────────────
RUN mkdir -p /root/.streamlit
COPY .streamlit/config.toml /root/.streamlit/config.toml

# ── Expose port ──────────────────────────────────────────────────────────────
EXPOSE 8501

# ── Entry point ──────────────────────────────────────────────────────────────
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
