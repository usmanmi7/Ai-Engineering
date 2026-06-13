import os

# We will read the text file we just created
file_path = "my_notes.txt"

print(f"Reading file: {file_path}...\n")

# Open the file in 'read' mode ('r') and read its contents
with open(file_path, "r") as file:
    text_content = file.read()

print("Here is what the file contains:")
print("-" * 30)
print(text_content)
print("-" * 30)
print("\nSuccess! We can now read documents.")
