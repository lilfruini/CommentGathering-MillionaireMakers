import json
from praw.models import Comment
from webbrowser import open as webopen
import urllib.request
import time
import CGCommons

def find_winner_thread(meta, winner_no):
    # Get the thread link of the winner's comment
    for thread in meta['threads']:
        winner_no -= thread['trunc_length'] if meta['WinnerFromFile'] == "Truncated" else thread['length']
        if winner_no <= 0:
            return thread['link']


def get_winner_name(reddit=None, url=None, cid=None):
    # Get the winner's name
    return Comment(reddit, id=cid).author.name


def api_json(link):
    # Request data from API and load as a json-dict
    with urllib.request.urlopen(link) as url:
        try:
            return json.loads(url.read().decode())
        except ValueError:
            return None


def get_win_hash(meta=None):
    # Wait till 30 seconds after draw time first
    wait_time = meta['DrawTime'] - time.time() + 30 if (meta['DrawTime'] - time.time()) + 30 > 0 else 0
    print("Waiting {:.2f} seconds till draw!".format(wait_time))
    time.sleep(wait_time)

    # Request the blocks of the entire day
    resp = api_json('https://blockchain.info/blocks/{}000?format=json'.format(meta['DrawTime'] - 1))
    block0 = 0
    # Iterate through each block, and save the height of the last block mined BEFORE the draw time
    for block in resp['blocks']:
        if block['time'] < meta['DrawTime']:
            block0 = block['height']

    # Calculate the winning block height/number
    win_block = block0 + meta['WaitTillBlock']
    print("Winning Block Number: {}".format(win_block))

    # Keep requesting for the winner block's data till a valid reponse is received (i.e. it is mined)
    # while not (block := api_json('https://blockchain.info/block-height/{}?format=json'.format(str(win_block)))):
    block = api_json('https://blockchain.info/block-height/{}?format=json'.format(str(win_block)))
    while not block:
        height = api_json('https://blockchain.info/latestblock')['height']
        # print("Awaiting Block {}.... Current Block: {}".format(win_block, height := api_json('https://blockchain.info/latestblock')['height']))
        print("Awaiting Block {}.... Current Block: {}".format(win_block, height))
        if win_block - height <= 1:
            time.sleep(10)
        elif win_block - height == 2:  # Sometimes 2 are mined near simultaneously
            time.sleep(30)
        else:
            time.sleep(90)
        block = api_json('https://blockchain.info/block-height/{}?format=json'.format(str(win_block)))

    # Return the winning block's hash and print the time it was mined, as a double-check
    print("\nBlock Found!\nBlock Time: {} UTC\n".format(time.strftime('%b %d %Y %H:%M:%S',  time.gmtime(block['blocks'][0]['time']))))
    return block['blocks'][0]['hash']


def main():
    with open('meta.json', 'r') as f:
        meta = json.load(f)

    file_name = meta['CID_Filename']

    if meta['WinnerFromFile'] == "Truncated":  # Defaults to original file
        file_name = file_name.rstrip('.txt') + '_Truncated.txt'

    print("Drawing winner from {}\nAbort if this is not correct!\n".format(file_name))

    with open(file_name, 'r') as f:
        comment_ids = [line.strip() for line in f]

    # Set winning hash, obtains from API if it is not provided
    win_hash = get_win_hash(meta) if meta['Win_Hash'] == '' else meta['Win_Hash']
    meta['Win_Hash'] = win_hash

    # Get winner and his/her details
    total = (len(comment_ids))
    winner_no = (1 + (int(win_hash, 16) % total))
    winner_id = comment_ids[winner_no - 1]
    winner_link = ''.join((find_winner_thread(meta, winner_no), winner_id))
    winner = get_winner_name(reddit=CGCommons.init_reddit(), cid=winner_id)

    # Print winner details
    print("Using {} comment list!\n".format(meta['WinnerFromFile']))
    print("Total Participants: {}\nWinner: {}\nHash: {}\n".format(total, winner_no, win_hash))
    print("Winner Comment ID: {}".format(winner_id))
    print("Winning Comment URL: {}".format(winner_link))
    print("Winner: {}".format(winner))

    # Save winner details to meta
    meta['Total Participants'] = total
    meta['Winner_Number'] = winner_no
    meta['Winner_ID'] = winner_id
    meta['Winner_Link'] = winner_link
    meta['Winner'] = winner
    with open('meta.json', 'w') as outfile:
        json.dump(meta, outfile, indent=4)

    # Opens link to comment if user chooses so
    x = input("\nEnter Y/y to open winning comment...")
    if x.upper() == "Y":
        webopen(winner_link)
    x = input("Draw complete! Press Enter to exit...")
    return


if __name__ == "__main__":
    main()
