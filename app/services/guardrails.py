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


guardrail = GuardrailService()