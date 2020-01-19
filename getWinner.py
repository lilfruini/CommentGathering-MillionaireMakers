import json
from praw.models import Comment
import praw
from webbrowser import open as webopen
import urllib.request
import time


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
        winner_no -= thread['trunc_length'] if meta['WinnerFromFile'] == "Truncated" else thread['length']
        if winner_no <= 0:
            return thread['link']


def get_winner_name(reddit=None, url=None, cid=None):
    return Comment(reddit, id=cid).author.name


def api_json(link):
    with urllib.request.urlopen(link) as url:
        try:
            return json.loads(url.read().decode())
        except ValueError:
            return None


def get_win_hash(meta=None):
    wait_time = meta['DrawTime'] - time.time() + 30 if (meta['DrawTime'] - time.time()) + 30 > 0 else 0
    print("Waiting {:.2f} seconds till draw!".format(wait_time))
    time.sleep(wait_time)

    resp = api_json('https://blockchain.info/blocks/{}000?format=json'.format(meta['DrawTime']))

    block0 = 0
    for block in resp['blocks']:
        if block['time'] < meta['DrawTime']:
            block0 = block['height']

    win_block = block0 + meta['WaitTillBlock']

    while not (block := api_json('https://blockchain.info/block-height/{}?format=json'.format(str(win_block)))):
        print("Awaiting Block {}.... Current Block: {}".format(win_block, api_json('https://blockchain.info/latestblock')['height']))
        time.sleep(10)

    print("Block Time: {} UTC".format(time.strftime('%b %d %Y %H:%M:%S',  time.gmtime(block['blocks'][0]['time']))))
    return block['blocks'][0]['hash']


def main():
    with open('meta.json', 'r') as f:
        meta = json.load(f)

    file_name = meta['CID_Filename']
    if meta['WinnerFromFile'] == "Truncated":
        file_name = file_name.rstrip('.txt') + '_Truncated.txt'

    with open(file_name, 'r') as f:
        comment_ids = [line.strip() for line in f]

    win_hash = get_win_hash(meta)
    meta['Win_Hash'] = win_hash

    total = (len(comment_ids))
    winner_no = (1 + (int(win_hash, 16) % total))
    winner_id = comment_ids[winner_no - 1]
    winner_link = ''.join((find_winner_thread(meta, winner_no), winner_id))
    winner = get_winner_name(reddit=init_reddit(), cid=winner_id)

    print("Using {} comment list!".format(meta['WinnerFromFile']))
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
