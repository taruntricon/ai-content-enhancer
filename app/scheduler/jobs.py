from datetime import datetime

from app.services.unipile_service import fetch_post_comments
from app.services.mapper import map_comments_to_engagements
# from app.utils.file_utils import write_json_file
# from app.services.unipile_service import fetch_post_content
from app.utils.file_utils import (
    write_json_file,
    read_json_file,
)

from app.database.engagement_repository import save_engagement
from app.database.post_repository import get_all_posts


# def save_engagement_data_to_db():
#     posts = read_json_file("app/models/sample_data.json")
#     for engagement in posts:
#                 # print(engagement)
#         save_engagement(engagement)

    # for post in posts:
    #     response = fetch_post_comments(post["postId"])

    #     if response:
    #         engagements = map_comments_to_engagements(
    #             response=response,
    #             post_text=post["postText"],
    #         )
    #         for engagement in engagements:
    #             print(engagement)
    #             save_engagement(engagement)

    #     print("Mapped Engagements")

    #     # for engagement in engagements:
    #     #     print(engagement)

    #     # write_json_file(
    #     # engagements,
    #     # "app/models/sample_data.json"
    #     # )

    # else:

    #     print("No data received")

def fetch_unipile_comments_job():
    

    print("=" * 60)
    print("Fetching LinkedIn comments")
    print(datetime.now())
    # post_text = fetch_post_content()

    # if(post_text):
    #     print(post_text)

    # posts = read_json_file("app/models/post_data.json")
    posts = get_all_posts()

    for post in posts:
        response = fetch_post_comments(post["postId"])

        if response:
            engagements = map_comments_to_engagements(
                response=response,
                post_text=post["postText"],
            )
            for engagement in engagements:
                print(engagement)
                save_engagement(engagement)

    
# )

        print("Mapped Engagements")

        # for engagement in engagements:
        #     print(engagement)

        # write_json_file(
        # engagements,
        # "app/models/sample_data.json"
        # )

    else:

        print("No data received")

    print("=" * 60)
