from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_enhance_guardrail():
    print("Testing /enhance endpoint with invalid text context...")
    response = client.post(
        "/enhance",
        json={
            "context": "AI Content Automation for B2B Teams",
            "platform": "linkedin"
        }
    )
    print("Status Code:", response.status_code)
    print("Response JSON:")
    print(response.json())

if __name__ == "__main__":
    test_api_enhance_guardrail()
