import os
import chromadb
from google import genai

# Load API key from environment variable for security
api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    print("Error: GEMINI_API_KEY not set. Run: export GEMINI_API_KEY='your-key-here'")
    exit(1)

os.environ["GEMINI_API_KEY"] = api_key
client = genai.Client()

print("1. Starting the Vector Database...")
db_client = chromadb.PersistentClient(path="./chroma_data")
collection = db_client.get_or_create_collection(name="notebook")

print("2. Reading our notes...")
with open("my_notes.txt", "r") as file:
    text_content = file.read()

# Split the document into paragraphs
chunks = text_content.split("\n\n")

print(f"3. Found {len(chunks)} paragraphs. Asking Gemini to convert them to numbers (Embeddings)...")

# Get embeddings from Gemini
embeddings = []
for chunk in chunks:
    # We use Gemini's special embedding model
    response = client.models.embed_content(
        model="gemini-embedding-2", 
        contents=chunk
    )
    # Extract the list of numbers from the response
    embeddings.append(response.embeddings[0].values)

print("4. Saving the embeddings to the database...")

# Create unique IDs
ids = [f"paragraph_{i}" for i in range(len(chunks))]

# Save the text and its numbers into ChromaDB
collection.add(
    documents=chunks,
    embeddings=embeddings,
    ids=ids
)

print("5. Done! The embeddings are stored safely in the 'chroma_data' folder.")
