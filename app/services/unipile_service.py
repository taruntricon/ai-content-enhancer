import requests
from app.config import (
    UNIPILE_BASE_URL,
    UNIPILE_API_KEY,
    UNIPILE_ACCOUNT_ID
)

# POST_ID = "7482344406616842241"

def fetch_post_content(post_id: str) -> str | None:

    url = f"{UNIPILE_BASE_URL}/api/v1/posts/{post_id}/"

    headers = {
        "X-API-KEY": UNIPILE_API_KEY,
        "accept": "application/json",
    }

    params = {
        "account_id": UNIPILE_ACCOUNT_ID
    }

    try:
        response = requests.get(
            url=url,
            headers=headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("text")

    except requests.exceptions.RequestException as ex:
        print(f"Failed to fetch post content: {ex}")
        return None

def fetch_post_comments(post_id: str):

    url = (
        f"{UNIPILE_BASE_URL}/api/v1/posts/urn:li:activity:"
        f"{post_id}/comments"
    )

    headers = {
        "X-API-KEY": UNIPILE_API_KEY,
        "accept": "application/json",
    }

    params = {
        "account_id": UNIPILE_ACCOUNT_ID
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        print("Successfully fetched comments")

        print(response.json())

        return response.json()

    except Exception as ex:
        print(f"Unipile Error : {ex}")

        return None


def publish_post(text: str):

    url = f"{UNIPILE_BASE_URL}/api/v1/posts"

    headers = {
        "X-API-KEY": UNIPILE_API_KEY,
        "accept": "application/json",
    }

    files = {
        "account_id": (None, UNIPILE_ACCOUNT_ID),
        "text": (None, text),
    }

    response = requests.post(
        url,
        headers=headers,
        files=files,
        timeout=30,
    )

    print("Status:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()

    return response.json()

def fetch_post_details(post_id: str) -> dict | None:
    """
    Fetch LinkedIn post details from Unipile.
    """

    url = f"{UNIPILE_BASE_URL}/api/v1/posts/{post_id}/"

    headers = {
        "X-API-KEY": UNIPILE_API_KEY,
        "accept": "application/json",
    }

    params = {
        "account_id": UNIPILE_ACCOUNT_ID,
    }

    try:
        response = requests.get(
            url=url,
            headers=headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as ex:
        print(f"Failed to fetch post details: {ex}")

        if ex.response is not None:
            print("Status Code:", ex.response.status_code)
            print("Response:", ex.response.text)

        return None