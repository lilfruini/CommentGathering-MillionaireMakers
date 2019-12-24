import json
from praw.models import Comment
import praw
from webbrowser import open as webopen


def init_reddit():
    with open('auth.json', 'r') as f:
        auth = json.load(f)

    return praw.Reddit(
        client_id=auth['client_id'],
        client_secret=auth['client_secret'],
        username=auth['username'],
        password=auth['password'],
        user_agent=auth['user_agent'])


def find_winner_thread(meta, winner_no):
    for thread in meta['threads']:
        winner_no -= thread['trunc_length']
        if winner_no <= 0:
            return thread['link']


def get_winner_name(reddit=None, url=None, cid=None):
    return Comment(reddit, id=cid).author.name


def main():
    with open('meta.json', 'r') as f:
        meta = json.load(f)

    file_name = meta['CID_Filename']
    win_hash = meta['Win_Hash']

    with open(file_name.rstrip('.txt') + '_Truncated.txt', 'r') as f:
        comment_ids = [line.strip() for line in f]

    if win_hash == '':
        x = input("Winning hash has not been entered into JSON!")
        exit(1)

    total = (len(comment_ids))
    winner_no = (1 + (int(win_hash, 16) % total))
    winner_id = comment_ids[winner_no - 1]
    winner_link = ''.join((find_winner_thread(meta, winner_no), winner_id))
    winner = get_winner_name(reddit=init_reddit(), cid=winner_id)

    print("Total Participants: {}\nWinner: {}\nHash: {}".format(total, winner_no, win_hash))
    print("Winner Comment ID: {}".format(winner_id))
    print("Winning Comment URL: {}".format(winner_link))
    print("Winner: {}".format(winner))

    meta['Total Participants'] = total
    meta['Winner_Number'] = winner_no
    meta['Winner_ID'] = winner_id
    meta['Winner_Link'] = winner_link
    meta['Winner'] = winner
    with open('meta.json', 'w') as outfile:
        json.dump(meta, outfile, indent=4)

    x = input("Enter Y to open winning comment...")
    if x.upper() == "Y":
        webopen(winner_link)


if __name__ == "__main__":
    main()
