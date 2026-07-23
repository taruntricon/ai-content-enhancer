import os
from pathlib import Path
from openai import OpenAI
from google import genai
from huggingface_hub import InferenceClient
from app.services.guardrails import guardrail

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent

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
        prompt_file = BASE_DIR / "prompts" / "linkedin_prompt.txt"
    else:
        prompt_file = BASE_DIR / "prompts" / "instagram_prompt.txt"

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
    prompt_file = BASE_DIR / "prompts" / "outreach_draft_prompt.txt"
    with open(prompt_file, encoding="utf-8") as f:
        system_prompt = f.read()

    variation_hints = {
        1: "Direct & Actionable (focus on immediate value & demo/solution)",
        2: "Consultative & Helpful (ask an insightful question and share relevant insight)",
        3: "Short & Concise (keep it under 60 words with a clear low-friction question)",
    }
    clean_name = (lead_name or "").strip()
    first_name = clean_name.split()[0] if clean_name else "there"
    full_name = clean_name or "Prospect"
    v_hint = variation_hints.get((variation - 1) % 3 + 1, "Direct & Actionable")

    formatted_prompt = system_prompt.format(
        full_name=full_name,
        first_name=first_name,
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
        if channel.lower() == "email":
            raw_output = (
                f"Subject: Connecting regarding your interest\n\n"
                f"Hi {full_name},\n\n"
                f"Thanks for reaching out! We'd love to connect with you regarding your interest in our recent post.\n\n"
                f"Would you be open to a brief 10-minute chat later this week?\n\n"
                f"Thanks & Regards,\n"
                f"[Your Name]"
            )
        else:
            raw_output = (
                f"Hi {first_name}, thanks for your note on my post! "
                f"I'd love to share how we're helping teams address key challenges in this space. "
                f"Are you open to a quick chat this week?"
            )

    raw_output = guardrail.sanitize(raw_output)

    # Strip any preamble like "If channel is message:", "Here is the draft:", etc.
    import re
    raw_output = re.sub(r"^(if channel is [\"']?\w+[\"']?:?|here is (the|your) draft:?)\s*", "", raw_output, flags=re.IGNORECASE).strip()

    subject = None
    body = raw_output

    if channel.lower() == "email":
        if "Subject:" in raw_output:
            parts = raw_output.split("Subject:", 1)[1].strip()
            if "Body:" in parts:
                sub_parts = parts.split("Body:", 1)
                subject = sub_parts[0].strip()
                body = sub_parts[1].strip()
            elif "\n" in parts and parts.split("\n", 1)[1].strip():
                lines = parts.split("\n", 1)
                subject = lines[0].strip()
                body = lines[1].strip()
            else:
                # If LLM put everything on one line without Body label or newline, split on greeting (Hi/Hello/Dear)
                import re
                greeting_match = re.search(r"\b(Hi|Hello|Dear)\b", parts, re.IGNORECASE)
                if greeting_match:
                    split_pos = greeting_match.start()
                    subject = parts[:split_pos].strip()
                    body = parts[split_pos:].strip()
                else:
                    subject = parts[:60].rstrip(" ,")
                    body = parts[60:].strip()
            
            # Clean "Body:" prefix if left in body
            body = re.sub(r"^Body:\s*", "", body, flags=re.IGNORECASE).strip()
    else:
        # For DM / message channel, ensure no Subject line or Body label
        if "Subject:" in raw_output:
            if "\n" in raw_output:
                body = raw_output.split("\n", 1)[1].strip()
            else:
                body = raw_output
        body = re.sub(r"^(Subject:[^\n]*\n?|Body:\s*)", "", body, flags=re.IGNORECASE).strip()

    return {
        "subject": subject,
        "body": body,
        "channel": channel,
        "variation": variation,
    }

