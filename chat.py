import os
from google import genai

# Load API key from environment variable for security
# Set it with: export GEMINI_API_KEY="your-key-here"
api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    print("Error: GEMINI_API_KEY not set. Run: export GEMINI_API_KEY='your-key-here'")
    exit(1)

os.environ["GEMINI_API_KEY"] = api_key

print("Connecting to Gemini...")

# Create a client to talk to the AI
client = genai.Client()

# Ask a question
question = "What is an AI Engineer in one sentence?"
print(f"\nYou asked: {question}")
print("Gemini says:")

# We use the 'gemini-2.5-flash' model because it is very fast and capable
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=question,
)

# Print the AI's answer!
print(response.text)
