import os
from google import genai

# We set the API key here so the SDK can find it.
# In a real app, we usually hide this key in a separate file, but for learning, this is okay!
api_key = "AQ.Ab8RN6LTbqwose4rUEKuJ5JlA7G2sOKihmODkEA_rvV92-Po8A"
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
