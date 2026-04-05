import streamlit as st
import os
from backend.chatbot import answer_question
from backend.document_processing.loader import load_pdf

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

st.set_page_config(page_title="PDF QA System", layout="wide")

st.title("📄 AI Document Question Answering System")

# -------------------------------
# PDF Upload Section
# -------------------------------
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    st.success("PDF uploaded successfully!")

    # Extract text
    with st.spinner("Extracting text from PDF..."):
        text = load_pdf("temp.pdf")

        # Save into sample.txt
        with open("data/sample.txt", "w", encoding="utf-8") as f:
            f.write(text)

    st.success("Text extracted and saved!")

# -------------------------------
# Question Section
# -------------------------------
st.subheader("Ask a Question")

question = st.text_input("Enter your question:")

if st.button("Get Answer"):
    if not os.path.exists("data/sample.txt"):
        st.error("Please upload a PDF first!")
    elif question.strip() == "":
        st.warning("Please enter a question!")
    else:
        with st.spinner("Generating answer..."):
            try:
                answer = answer_question("data/sample.txt", question)
                st.success("Answer:")
                st.write(answer)
            except Exception as e:
                st.error(f"Error: {str(e)}")