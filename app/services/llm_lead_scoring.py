import os
import json
from typing import Any
from openai import OpenAI
from app.config import (
    HF_API_KEY
)

from app.database.leads_repository import save_lead
from app.database.mongodb import engagements_collection

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

# with open(
#     "app/models/sample_data.json",
#     "r",
#     encoding="utf-8"
# ) as file:
#     sample_data = json.load(file)

# results = score_leads_llm(sample_data)


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
    # post_text = {e["message"]: e for e in engagements}
    leads = []
    for r in llm_results:
        original = by_id.get(r["engagementId"], {})
        actor = original.get("actor", {})
        leads.append({
            "postText": original.get("postText"),
            "engagementId": r["engagementId"],
            "name": actor.get("name"),
            # "designation": actor.get("designation"),
            # "company": actor.get("company"),
            # "industry": actor.get("industry",""),
            # "scores": r.get("scores", {}),
            "total_score": r.get("total_score"),
            "intent": r["tier"],
            "reasoning": r["reasoning"],
            # "confidence": r["confidence"],
            "message": original.get("message",""),
        })

    tier_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    sorted_leads = sorted(leads, key=lambda x: tier_order.get(x["intent"], 3))
    print(sorted_leads)
    save_lead(sorted_leads)

    engagement_ids = [
    lead["engagementId"]
    for lead in sorted_leads
    ]
    print(engagement_ids)
    engagements_collection.update_many(
        {
            "engagementId": {"$in": engagement_ids}
        },
        {
            "$set": {"leadProcessed": "True"}
        }
    )

    return sorted_leads


# if __name__ == "__main__":
#     sample_data = [
#         {
#             "engagementId": "eng_001", "action": "comment",
#             "message": "This is exactly what we need. Can we set up a 30-min call this week to see it live?",
#             "actor": {"name": "Priya Nandakumar", "designation": "Director of Legal Operations",
#                        "company": "Solstice Health Group", "industry": "Healthcare", "previousInteractions": 2},
#         },
#         {
#             "engagementId": "eng_002", "action": "comment",
#             "message": "What's the pricing for a team of ~25 reviewers?",
#             "actor": {"name": "Marcus Feld", "designation": "VP, Procurement",
#                        "company": "Nordwell Manufacturing", "industry": "Manufacturing", "previousInteractions": 0},
#         },
#         {
#             "engagementId": "eng_003", "action": "comment",
#             "message": "Can you send me a demo? We get hundreds of LinkedIn comments a week and it's brutal trying to spot the real buyers.",
#             "actor": {"name": "Ana Kovacevic", "designation": "CEO",
#                        "company": "Brightline Logistics", "industry": "Logistics", "previousInteractions": 1},
#         },
#         {
#             "engagementId": "eng_004", "action": "positive_comment",
#             "message": "Love this. We've been looking for something like this all year.",
#             "actor": {"name": "Devon Achebe", "designation": "Head of Contracts",
#                        "company": "Farro & Vance LLP", "industry": "Legal Services", "previousInteractions": 0},
#         },
#         {
#             "engagementId": "eng_005", "action": "share", "message": None,
#             "actor": {"name": "Renata Silva", "designation": "Operations Manager",
#                        "company": "Kestrel Freight Co.", "industry": "Logistics", "previousInteractions": 0},
#         },
#     ]


# results = score_leads_llm(sample_data, target_industries=["Healthcare", "Legal Services", "Logistics", "Manufacturing"])
# for r in results:
#     print(f"{r['tier']:6s} | {r['confidence']:6s} | {r['name']:20s} | {r['reasoning']}")