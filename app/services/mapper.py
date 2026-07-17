from typing import Any


def map_comments_to_engagements(
    response: dict[str, Any],
    post_text: str | None = None,
) -> list[dict[str, Any]]:

    engagements = []

    for comment in response.get("items", []):

        author_details = comment.get("author_details", {})

        engagement = {
            "engagementId": f"eng_{comment['id']}",
            "platform": "LinkedIn",
            "postId": comment.get("post_id"),
            "postText": post_text,
            "action": "comment",
            "message": comment.get("text"),
            "actor": {
                "name": comment.get("author"),
                "designation": author_details.get("headline"),
                "company": None,
                "industry": None,
                "profileUrl": author_details.get("profile_url"),
                "previousInteractions": 0,
            },
            "timestamp": comment.get("date"),
            "leadProcessed": False
        }

        engagements.append(engagement)

    return engagements