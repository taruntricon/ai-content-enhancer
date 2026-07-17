from openai import OpenAI
import google.generativeai as genai
from huggingface_hub import InferenceClient


from app.config import (
    AI_PROVIDERS,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROK_API_KEY,
    GROK_MODEL,
    HF_API_KEY,
    HF_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL
)

# Initialize clients
# OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(GEMINI_MODEL)

# Grok
grok_client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1"
)


hf_client = InferenceClient(
    provider="hf-inference",
    api_key=HF_API_KEY
)

def call_gemini(prompt):

    response = gemini_model.generate_content(prompt)

    return response.text

def call_grok(prompt):

    response = grok_client.chat.completions.create(
        model=GROK_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

def call_openai(prompt):

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

def call_huggingface(prompt):

    # from openai import OpenAI

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_API_KEY
    )

    response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

    # response = hf_client.chat.completions.create(
    #     model=HF_MODEL,
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": prompt
    #         }
    #     ],
    #     max_tokens=500
    # )

    return response.choices[0].message.content


def enhance_content(context, platform):

    # your existing code
    if platform.lower() == "linkedin":
        prompt_file = "app/prompts/linkedin_prompt.txt"
    else:
        prompt_file = "app/prompts/instagram_prompt.txt"

    with open(prompt_file, encoding="utf-8") as f:
        system_prompt = f.read()

    prompt = system_prompt.format(context=context)

    # NEW CODE STARTS HERE
    for provider in AI_PROVIDERS:

        try:

            print(f"Trying {provider}")

            if provider == "gemini":
                return call_gemini(prompt)
            
            elif provider == "huggingface":
                return call_huggingface(prompt)
            
            elif provider == "grok":
                return call_grok(prompt)

            elif provider == "openai":
                return call_openai(prompt)

        except Exception as e:

            print(e)

            continue

    raise Exception("All AI providers failed.")


# def enhance_content(context: str, platform: str):

#     # Select prompt file
#     if platform.lower() == "linkedin":
#         prompt_file = "app/prompts/linkedin_prompt.txt"
#     else:
#         prompt_file = "app/prompts/instagram_prompt.txt"

#     # Read prompt
#     with open(prompt_file, encoding="utf-8") as f:
#         system_prompt = f.read()

#     # Replace placeholder
#     prompt = system_prompt.format(context=context)

#     # Call provider
#     if PROVIDER.lower() == "openai":

#         response = openai_client.chat.completions.create(
#             model=OPENAI_MODEL,
#             messages=[
#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ]
#         )

#         return response.choices[0].message.content

#     elif PROVIDER.lower() == "gemini":

#         response = gemini_model.generate_content(prompt)

#         return response.text

#     else:
#         raise Exception(
#             f"Unsupported provider: {PROVIDER}"
#         )