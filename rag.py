import os
import chromadb
from google import genai

# Set up Gemini
api_key = "AQ.Ab8RN6LTbqwose4rUEKuJ5JlA7G2sOKihmODkEA_rvV92-Po8A"
os.environ["GEMINI_API_KEY"] = api_key
client = genai.Client()

print("1. Connecting to our database...")
db_client = chromadb.PersistentClient(path="./chroma_data")
collection = db_client.get_collection(name="notebook")

# The question we want to ask our "Notebook"
question = "What is Usman building?"
print(f"\nQuestion: {question}")

print("2. Converting the question to numbers and searching the database...")
# Convert question to embeddings
response = client.models.embed_content(
    model="gemini-embedding-2", 
    contents=question
)
question_embedding = response.embeddings[0].values

# Search the database for the 2 most relevant paragraphs (to be safe!)
results = collection.query(
    query_embeddings=[question_embedding],
    n_results=2
)

# Extract the matching paragraphs and join them together with a new line
best_match_paragraph = "\n".join(results['documents'][0])
print("\n3. Found the most relevant notes!")
print("-" * 30)
print(best_match_paragraph)
print("-" * 30)

print("\n4. Asking Gemini to answer the question using ONLY the notes above...")

# Give Gemini the rules, the context, and the question
prompt = f"""
You are a helpful assistant. Use ONLY the following Context to answer the Question. 
If the answer is not in the Context, say "I don't know based on the notes."

Context: 
{best_match_paragraph}

Question: {question}
"""

# Get the final answer from Gemini
answer_response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
)

print("\n--- Final Answer from Mini-NotebookLM ---")
print(answer_response.text)
