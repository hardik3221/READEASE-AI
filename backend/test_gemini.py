from groq import Groq

client = Groq(
    api_key="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"
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": "Explain photosynthesis in simple words"
        }
    ]
)

print(response.choices[0].message.content)