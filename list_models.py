import google.generativeai as genai

genai.configure(api_key="")  # Replace with your actual key

for m in genai.list_models():
    print(m.name)
