import praw
from praw.models import MoreComments
import json
import hashlib


def init_reddit():
    with open('auth.json', 'r') as f:
        auth = json.load(f)

    return praw.Reddit(
        client_id=auth['client_id'],
        client_secret=auth['client_secret'],
        username=auth['username'],
        password=auth['password'],
        user_agent=auth['user_agent'])


def fetch_thread_ids(thread=None, reddit=None):
    submission = reddit.submission(url=thread)
    submission.comment_sort = 'old'
    sublist = []

    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            sublist += top_level_comment.children
        else:
            sublist.append(str(top_level_comment.id))

    return sublist


def fetch_all_ids(reddit=None, meta=None):
    all_id = []
    for thread in meta['threads']:
        thread_ids = fetch_thread_ids(thread=thread['link'], reddit=reddit)
        thread['length'] = len(thread_ids)
        all_id += thread_ids

    print(f"Found {len(all_id)} comments")
    return all_id


def hash_sha256(file):
    buf_size = 65536  # lets read stuff in 64kb chunks!
    sha256 = hashlib.sha256()
    with open(file, 'rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def main():
    with open('meta.json', 'r') as f:
        meta = json.load(f)

    file_name = meta['CID_Filename']

    all_id = fetch_all_ids(reddit=init_reddit(), meta=meta)

    with open(file_name, "w") as f:
        f.write("\n".join(sorted(all_id)))

    print(f"Comments saved in {file_name}")

    meta['CID_SHA256'] = hash_sha256(file_name)
    print(f"SHA-256 Hash: {meta['CID_SHA256']}")

    if 'Win_Hash' not in meta.keys():
        meta['Win_Hash'] = ''

    with open('meta.json', 'w') as outfile:
        json.dump(meta, outfile, indent=4)

    x = input("End..")


if __name__ == "__main__":
    main()
