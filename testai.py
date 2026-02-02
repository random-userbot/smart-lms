import yaml
import google.generativeai as genai

# 1. Load the YAML file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# 2. Extract settings
api_key = config['gemini']['api_key']
model_name = config['gemini']['model_name']

# 3. Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)

# 4. Test it
response = model.generate_content("Explain YAML in one sentence.")
print(response.text)