import json
from app.services.guardrails import guardrail

def run_guardrails_test():
    print("="*60)
    print("1. TESTING GUARDRAIL VALIDATION (DIRECT)")
    print("="*60)

    # Test case 1: Violation with banned phrase and percentage statistic
    test_text_invalid = (
        "According to research 95% of sales teams close deals faster with automation. "
        "Visit http://fake-link.com #sales #leads #ai #b2b #marketing #growth"
    )
    
    print("\n[Input Text]:")
    print(test_text_invalid)
    
    val_result = guardrail.validate(test_text_invalid)
    print("\n[Guardrail Validation Result]:")
    print(f"Valid: {val_result['valid']}")
    print("Detected Errors:")
    for err in val_result["errors"]:
        print(f" - {err}")

    # Test case 2: Sanitization
    sanitized_text = guardrail.sanitize(test_text_invalid)
    print("\n[Sanitized Output]:")
    print(sanitized_text)

    # Test case 3: Lead scoring validation
    print("\n" + "="*60)
    print("2. TESTING LEAD SCORING GUARDRAIL VALIDATION")
    print("="*60)

    mock_llm_leads = [
        {
            "engagementId": "eng_101",
            "scores": {
                "message_intent": 35, # Trigger high tier rule (>=31)
                "designation": 15,
                "industry": 10,
                "action": 10
            },
            "total_score": 70,
            "tier": "LOW",  # Mismatch: should be corrected to HIGH
            "confidence": "high",
            "reasoning": "High intent message from legal director"
        }
    ]

    score_val = guardrail.validate_lead_scoring(mock_llm_leads)
    print("\n[Lead Scoring Validation Result]:")
    print(f"Valid: {score_val['valid']}")
    print("Detected Errors:")
    for err in score_val["errors"]:
        print(f" - {err}")
    
    print("\n[Sanitized Leads Output]:")
    print(json.dumps(score_val["sanitized_leads"], indent=2))

if __name__ == "__main__":
    run_guardrails_test()
