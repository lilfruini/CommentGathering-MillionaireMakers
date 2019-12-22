import praw

reddit = praw.Reddit(
    client_id='XXX',
    client_secret='XXX',
    username='XXX',
    password='XXX',
    user_agent='Comment Extraction')

submission = reddit.submission(url='https://old.reddit.com/r/millionairemakers/comments/edq7ov/apparently_users_came_by_so_fast_that_reddits_hug/')

submission.comment_sort = 'old'
submission.comments.replace_more(limit=None)
from praw.models import MoreComments
li = []
for top_level_comment in submission.comments:
    if isinstance(top_level_comment, MoreComments):
        continue
    li.append(str(top_level_comment.id))

with open("5UTCFortyNinePart2.txt", "w") as f:
    f.write("\n".join(li))