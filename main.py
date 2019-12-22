import praw
from praw.models import MoreComments

reddit = praw.Reddit(
    client_id='',
    client_secret='',
    username='',
    password='',
    user_agent='Comment Extraction')

file_name = "5UTCFortyNine.txt"

threads = [
    'https://old.reddit.com/r/millionairemakers/comments/edhj2m/not_only_is_it_about_to_be_christmas_but_today/',
    'https://old.reddit.com/r/millionairemakers/comments/edq7ov/apparently_users_came_by_so_fast_that_reddits_hug/'
]

def fetch_ids(thread_url):
    submission = reddit.submission(url=thread_url)
    submission.comment_sort = 'old'
    li = []
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            li += top_level_comment.children
        li.append(str(top_level_comment.id))
    return li

tid = []
for thread in threads:
    tid += fetch_ids(thread)
print(f"Found {len(tid)} comments")

with open(file_name, "w") as f:
    f.write("\n".join(tid))
print(f"Comments saved in {file_name}")
