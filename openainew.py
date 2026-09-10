import os
from openai import AzureOpenAI

# Initialize the client with Azure credentials
# It's best practice to use environment variables for keys
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY", "your-api-key-here"),  
    api_version="2024-02-01", # Adjust based on your preferred API version
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://azure.com")
)

# Define your prompt/question
user_question = "What are three key benefits of automated scripting?"

# Send the question to the model
response = client.chat.completions.create(
    model="your-deployment-name", # E.g., 'gpt-4o' or your specific deployment
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_question}
    ]
)

# Print the response
print(response.choices[0].message.content)
