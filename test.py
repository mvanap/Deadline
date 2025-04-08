import AzureOpenai


api_version = "24-02-01"  # Example API version
# azure_endpoint = "https://hexavarsity-secureapi.azurewebsites.net/api/azureai"  # Replace with your Azure OpenAI endpoint
azure_endpoint = "https://stg-secureapi.hexaware.com/api/azureai"
api_key = "72ea4177aee217f3"  # Replace with your API key
 
client = AzureOpenAI(api_version=api_version, azure_endpoint=azure_endpoint, api_key=api_key,)
 
prompt = f"""
        Hello, OpenAI!
        """
res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that provides clear and concise summaries.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1000,
        top_p=0.6,
        frequency_penalty=0.7,
    )
 
print(res.choices[0].message.content)
 