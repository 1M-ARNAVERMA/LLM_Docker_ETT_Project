from chatbot import answer_question

file_path = "../data/sample.txt"  # create this file

question = "What is Docker?"

response = answer_question(file_path, question)

print("\nAnswer:\n", response)