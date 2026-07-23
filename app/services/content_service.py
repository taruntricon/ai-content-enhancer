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
    model=HF_MODEL or "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
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


def generate_outreach_draft(
    lead_name: str,
    lead_message: str = "",
    post_text: str = "",
    intent: str = "HIGH",
    reasoning: str = "",
    channel: str = "email",
    variation: int = 1,
) -> dict:
    prompt_file = "app/prompts/outreach_draft_prompt.txt"
    with open(prompt_file, encoding="utf-8") as f:
        system_prompt = f.read()

    variation_hints = {
        1: "Direct & Actionable (focus on immediate value & demo/solution)",
        2: "Consultative & Helpful (ask an insightful question and share relevant insight)",
        3: "Short & Concise (keep it under 60 words with a clear low-friction question)",
    }
    v_hint = variation_hints.get((variation - 1) % 3 + 1, "Direct & Actionable")

    formatted_prompt = system_prompt.format(
        lead_name=lead_name or "Prospect",
        lead_message=lead_message or "Interested in your product",
        post_text=post_text or "Social post",
        intent=intent or "HIGH",
        reasoning=reasoning or "High buying signal",
        channel=channel or "email",
        variation_hint=v_hint,
    )

    raw_output = None
    for provider in AI_PROVIDERS:
        try:
            print(f"Drafting outreach with {provider} (variation {variation})...")
            if provider == "gemini":
                raw_output = call_gemini(formatted_prompt)
            elif provider == "huggingface":
                raw_output = call_huggingface(formatted_prompt)
            elif provider == "grok":
                raw_output = call_grok(formatted_prompt)
            elif provider == "openai":
                raw_output = call_openai(formatted_prompt)

            if raw_output:
                break
        except Exception as e:
            print(f"{provider} failed for outreach draft: {e}")
            continue

    if not raw_output:
        raw_output = f"Hi {lead_name},\n\nThanks for reaching out! We'd love to connect with you regarding your interest."

    raw_output = guardrail.sanitize(raw_output)

    subject = None
    body = raw_output

    if channel.lower() == "email" and "Subject:" in raw_output:
        parts = raw_output.split("Subject:", 1)[1].strip()
        lines = parts.split("\n", 1)
        subject_line = lines[0].strip()

        if len(lines) > 1 and lines[1].strip():
            # Normal case: body on next line(s)
            subject = subject_line
            body = lines[1].strip()
        else:
            # LLM put everything on one line — try to split on "Body:" marker
            if "Body:" in subject_line:
                sub_parts = subject_line.split("Body:", 1)
                subject = sub_parts[0].strip()
                body = sub_parts[1].strip()
            else:
                # Heuristic: take first sentence as subject, rest as body
                import re
                match = re.search(r"^(.{10,120}?[.!?])\s+(.+)$", subject_line, re.DOTALL)
                if match:
                    subject = match.group(1).strip()
                    body = match.group(2).strip()
                else:
                    # Fallback: first 80 chars as subject
                    subject = subject_line[:80].rstrip(" ,")
                    body = subject_line[80:].strip()

    return {
        "subject": subject,
        "body": body,
        "channel": channel,
        "variation": variation,
    }

