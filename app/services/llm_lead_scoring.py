import os
import json
from typing import Any
from openai import OpenAI
from app.config import (
    HF_API_KEY
)


DEFAULT_TARGET_INDUSTRIES = [
    "Healthcare",
    "Legal Services",
    "Logistics",
    "Manufacturing",
]

MODEL = "meta-llama/Llama-3.1-8B-Instruct"

prompt_file = "app/prompts/lead_scoring_system_prompt.txt"

with open(prompt_file, encoding="utf-8") as f:
        SYSTEM_PROMPT_TEMPLATE = f.read()


def _build_system_prompt(target_industries):
    industries_str = ", ".join(target_industries) if target_industries else "none specified — treat all industries neutrally"
    return SYSTEM_PROMPT_TEMPLATE.replace("{TARGET_INDUSTRIES}", industries_str)


def _build_user_message(engagements):
    slim = []
    for e in engagements:
        actor = e.get("actor", {})
        slim.append({
            "engagementId": e.get("engagementId"),
            "action": e.get("action"),
            "message": e.get("message"),
            "designation": actor.get("designation"),
            "industry": actor.get("industry"),
            "previousInteractions": actor.get("previousInteractions", 0),
        })
    return json.dumps(slim, indent=2)


def _get_client():
    # hf_api_key = os.environ.get("HF_API_KEY")
    if not HF_API_KEY:
        raise EnvironmentError("Set HF_API_KEY environment variable with your Hugging Face token.")
    return OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_API_KEY,
    )


def score_leads_llm(
    engagements: list[dict[str, Any]],
    target_industries: list[str] | None = None,
) -> list[dict[str, Any]]:
# (engagements, target_industries=None):
    
    client = _get_client()
    if target_industries is None:
        target_industries = DEFAULT_TARGET_INDUSTRIES

    system_prompt = _build_system_prompt(target_industries or [])
    user_message = _build_user_message(engagements)

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )

    raw_text = response.choices[0].message.content.strip()

    # Defensive parsing: strip markdown fences if the model adds them anyway
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        llm_results = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse model output as JSON: {e}\nRaw output: {raw_text}")

    # Merge LLM tier/reasoning back with original actor info for readability
    by_id = {e["engagementId"]: e for e in engagements}
    merged = []
    for r in llm_results:
        original = by_id.get(r["engagementId"], {})
        actor = original.get("actor", {})
        merged.append({
            "engagementId": r["engagementId"],
            "name": actor.get("name"),
            "designation": actor.get("designation"),
            "company": actor.get("company"),
            "industry": actor.get("industry",""),
            "scores": r.get("scores", {}),
            "total_score": r.get("total_score"),
            "tier": r["tier"],
            "reasoning": r["reasoning"],
            "confidence": r["confidence"],
            "postText": original.get("postText"),
            "message": original.get("message",""),
            
        })

    tier_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    return sorted(merged, key=lambda x: tier_order.get(x["tier"], 3))
