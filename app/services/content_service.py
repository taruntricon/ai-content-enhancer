from openai import OpenAI
from google import genai
from huggingface_hub import InferenceClient
from app.services.guardrails import guardrail

from app.config import (
    AI_PROVIDERS,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROK_API_KEY,
    GROK_MODEL,
    HF_API_KEY,
    HF_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    GEMINI_MODELS
)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Gemini
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Grok
grok_client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1"
)

hf_client = InferenceClient(
    provider="hf-inference",
    api_key=HF_API_KEY
)

# def call_gemini(prompt):
#     print("gemini")
#     print(f"Using model: {GEMINI_MODEL}")
#     response = gemini_client.models.generate_content(
#     model=GEMINI_MODEL,
#     contents=prompt
#     )

#     return response.text

def call_gemini(prompt: str):
    last_error = None

    for model in GEMINI_MODELS:
        try:
            print(f"Trying Gemini model: {model}")

            response = gemini_client.models.generate_content(
                model=model,
                contents=prompt
            )

            print(f"Success with {model}")
            return response.text

        except Exception as e:
            print(f"{model} failed: {e}")
            last_error = e

    raise last_error

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
    print("huggingface")

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

    return response.choices[0].message.content


def enhance_content(context, platform):

    if platform.lower() == "linkedin":
        prompt_file = "app/prompts/linkedin_prompt.txt"
    else:
        prompt_file = "app/prompts/instagram_prompt.txt"

    with open(prompt_file, encoding="utf-8") as f:
        system_prompt = f.read()

    prompt = system_prompt.format(context=context)

    for provider in AI_PROVIDERS:

        try:

            print(f"Trying {provider}")

            if provider == "gemini":
                # return call_gemini(prompt)
                generated = call_gemini(prompt)
            
            elif provider == "huggingface":
                # return call_huggingface(prompt)
                generated = call_huggingface(prompt)
            
            elif provider == "grok":
                # return call_grok(prompt)
                generated = call_grok(prompt)

            elif provider == "openai":
                # return call_openai(prompt)
                generated = call_openai(prompt)
            
            else:
              raise Exception(f"Unknown provider: {provider}")
            
            validation = guardrail.validate(generated)

            # If validation passes, return immediately
            if validation["valid"]:
                return guardrail.sanitize(generated)

            print("Guardrail validation failed:")
            for error in validation["errors"]:
                print(f"- {error}")

            retry_prompt = guardrail.rewrite_prompt(prompt)

            print("Retrying with stricter prompt...")

            regenerated = call_huggingface(retry_prompt)

            # Validate regenerated content
            validation = guardrail.validate(regenerated)

            if validation["valid"]:
                return guardrail.sanitize(regenerated)

            print("Regenerated content also failed guardrails.")
            for error in validation["errors"]:
                print(f"- {error}")

            # Try the next AI provider
            continue

        except Exception as e:
            print(e)
            continue

    raise Exception("All AI providers failed.")
