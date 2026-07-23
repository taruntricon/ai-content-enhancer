import re
from typing import Any


class GuardrailService:

    MAX_WORDS = 250
    MAX_HASHTAGS = 5

    # Unsupported sources (unless explicitly provided by user)
    BANNED_SOURCES = [
        "gartner",
        "mckinsey",
        "forrester",
        "harvard",
        "stanford",
        "mit",
    ]

    # Hallucination indicators
    BANNED_PHRASES = [
        "according to research",
        "research shows",
        "studies show",
        "research proves",
        "experts say",
        "statistics show",
        "survey found",
        "case study",
    ]

    URL_REGEX = r"https?://[^\s]+"
    HASHTAG_REGEX = r"#\w+"
    PERCENTAGE_REGEX = r"\b\d+%"
    YEAR_REGEX = r"\b(19|20)\d{2}\b"

    def validate(self, content: str) -> dict[str, Any]:

        errors = []

        word_count = len(content.split())

        if word_count > self.MAX_WORDS:
            errors.append(
                f"Post contains {word_count} words. Maximum allowed is {self.MAX_WORDS}."
            )

       
        # Hashtag Count
        
        hashtags = re.findall(self.HASHTAG_REGEX, content)

        if len(hashtags) > self.MAX_HASHTAGS:
            errors.append(
                f"Too many hashtags ({len(hashtags)}). Maximum allowed is {self.MAX_HASHTAGS}."
            )

        # ------------------------
        # Fake Statistics
        # ------------------------
        percentages = re.findall(self.PERCENTAGE_REGEX, content)

        if percentages:
            errors.append(
                f"Possible fabricated statistics detected: {', '.join(percentages)}"
            )

        # ------------------------
        # Unsupported Claims
        # ------------------------
        lower = content.lower()

        for phrase in self.BANNED_PHRASES:
            if phrase in lower:
                errors.append(
                    f"Unsupported claim detected: '{phrase}'"
                )

        # ------------------------
        # Unsupported Sources
        # ------------------------
        for source in self.BANNED_SOURCES:
            if source in lower:
                errors.append(
                    f"External source mentioned: '{source}'. Verify before publishing."
                )

        # ------------------------
        # URLs
        # ------------------------
        urls = re.findall(self.URL_REGEX, content)

        if urls:
            errors.append(
                "Generated content contains URL(s). Verify before publishing."
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def sanitize(self, content: str) -> str:

        # Remove URLs
        content = re.sub(self.URL_REGEX, "", content)

        # Remove duplicate spaces
        content = re.sub(r"\s+", " ", content)

        return content.strip()

    def rewrite_prompt(self, original_prompt: str) -> str:

        return f"""
{original_prompt}

IMPORTANT RULES

- Do NOT invent statistics.
- Do NOT invent percentages.
- Do NOT invent surveys.
- Do NOT invent research.
- Do NOT invent company names.
- Do NOT invent customer stories.
- Do NOT invent quotes.
- Use ONLY information supplied by the user.
- If information is unavailable, write generally.
- Never fabricate facts.
"""

    def should_regenerate(self, validation_result: dict) -> bool:

        return not validation_result["valid"]

    def validate_lead_scoring(self, llm_results: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Guardrail validation for LLM lead scoring outputs.
        Ensures score bounds, tier consistency, total score calculation, and valid confidence.
        """
        errors = []
        sanitized = []

        if not isinstance(llm_results, list):
            return {
                "valid": False,
                "errors": ["LLM lead scoring output must be a JSON array"],
                "sanitized_leads": []
            }

        for idx, item in enumerate(llm_results):
            if not isinstance(item, dict):
                errors.append(f"Item at index {idx} is not a valid object.")
                continue

            eng_id = item.get("engagementId", f"unknown_{idx}")
            scores = item.get("scores", {})
            if not isinstance(scores, dict):
                scores = {}

            # Signal score extraction & clamping
            msg_intent = max(0, min(40, int(scores.get("message_intent", 0))))
            designation = max(0, min(25, int(scores.get("designation", 0))))
            industry = max(0, min(20, int(scores.get("industry", 0))))
            action = max(0, min(15, int(scores.get("action", 0))))

            calculated_total = msg_intent + designation + industry + action
            given_total = item.get("total_score")

            if given_total is None or given_total != calculated_total:
                errors.append(
                    f"Lead {eng_id}: Given total score ({given_total}) does not match sum of signals ({calculated_total})."
                )

            total_score = max(0, min(100, calculated_total))

            # Tier determination & guardrail override rules
            given_tier = str(item.get("tier", "")).upper()

            if msg_intent >= 31:
                expected_tier = "HIGH"
            elif total_score >= 70:
                expected_tier = "HIGH"
            elif total_score >= 40:
                expected_tier = "MEDIUM"
            else:
                expected_tier = "LOW"

            if given_tier not in ["HIGH", "MEDIUM", "LOW"]:
                errors.append(f"Lead {eng_id}: Invalid tier '{given_tier}'. Expected '{expected_tier}'.")
                given_tier = expected_tier
            elif given_tier != expected_tier:
                errors.append(
                    f"Lead {eng_id}: Tier mismatch '{given_tier}' vs expected '{expected_tier}' based on scores."
                )
                given_tier = expected_tier

            # Confidence determination
            confidence = str(item.get("confidence", "medium")).lower()
            if confidence not in ["high", "medium", "low"]:
                confidence = "medium"

            reasoning = str(item.get("reasoning", "Score assigned based on engagement analysis.")).strip()

            sanitized.append({
                "engagementId": eng_id,
                "scores": {
                    "message_intent": msg_intent,
                    "designation": designation,
                    "industry": industry,
                    "action": action,
                },
                "total_score": total_score,
                "tier": given_tier,
                "reasoning": reasoning,
                "confidence": confidence,
            })

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "sanitized_leads": sanitized,
        }


guardrail = GuardrailService()