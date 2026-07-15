from datetime import datetime

from app.services.unipile_service import fetch_post_comments
from app.services.mapper import map_comments_to_engagements
from app.utils.file_utils import write_json_file
from app.services.unipile_service import fetch_post_content


def fetch_unipile_comments_job():

    print("=" * 60)
    print("Fetching LinkedIn comments")
    print(datetime.now())
    post_text = fetch_post_content()

    if(post_text):
        print(post_text)


    response = fetch_post_comments()

    if response:

        engagements = map_comments_to_engagements(
        response=response,
        post_text=post_text,
)

        print("Mapped Engagements")

        for engagement in engagements:
            print(engagement)

        write_json_file(
        engagements,
        "app/models/sample_data.json"
        )

    else:

        print("No data received")

    print("=" * 60)
