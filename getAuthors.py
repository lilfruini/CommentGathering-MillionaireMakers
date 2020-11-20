from typing import Iterable
from itertools import islice

import prawcore
from praw.models import Redditors
from praw.const import API_PATH
import json
import time
import threading
import CGCommons
from tqdm import tqdm


class AuthorThread(threading.Thread):
    def __init__(self, reddit=None, cids=None, dateline=None, stop: threading.Event = None):
        super().__init__(daemon=True)
        self.reddit = reddit
        self.cids = cids
        self.dateline = dateline if dateline < time.time() else -1
        self.stop = stop
        self.authors = []
        self.author_fullnames = {}
        self.dq_age = set()
        self.checked_len = 0

    def run(self):
        if self.dateline == -1:
            print("\nWARNING: User account creation time checking is disabled\n")
        self.get_authors_fullnames()
        if self.dateline != -1 and not self.stop.is_set():
            self.check_authors()

    def get_authors_fullnames(self):
        """
        Request comment infos from Reddit's info endpoint and extract author fullnames
        """
        # Pbar 1
        print("Collecting comment authors' UIDs....")
        params = {'total': len(self.cids), 'desc': 'Progress', 'unit': ' Comments'}
        threading.Thread(target=self.pbar_loop, args=(params, lambda x: len(x.authors),)).start()

        iterable = iter(self.cids)
        last = time.time()
        while not self.stop.is_set():
            # Split into chunks of 100 comment IDs, Reddit API's max object size
            chunk = list(islice(iterable, 100))
            if not chunk:
                break

            params = {"id": ",".join(chunk)}
            try:  # Ping the endpoint
                results = self.reddit.get(API_PATH["info"], params=params)
            except prawcore.exceptions.NotFound:
                # None of the given IDs matched any Redditor.
                continue

            # Parse the returned data
            for comment in results.children:
                if hasattr(comment, 'author_fullname'):
                    if self.dateline != -1:  # Supposed to only disable suspension check, but since that's not possible it'll just disable user checking outright
                        self.author_fullnames[comment.author_fullname] = None  # Store in author_fullnames to check author account creation time
                        self.authors.append(comment.author_fullname)  # Temporarily, to be replaced in check_authors
                    else:  # Don't check creation time, so just add name to the author list
                        self.authors.append(comment.author.name)
                else:  # Deleted accounts/comments
                    self.authors.append('Null')

            # Avoid murdering the API
            last += 1
            sleeptime = last - time.time()
            if sleeptime < 0:
                continue
            time.sleep(sleeptime)

        time.sleep(0.11)  # Let progress bar wake up and close itself

    def check_authors(self):
        """
        Request user infos and check account creation times
        """
        # Pbar 2
        print("\nAll comment authors' UIDs have been found. Now checking account creation times...")
        params = {'total': len(self.author_fullnames), 'desc': 'Progress', 'unit': ' Authors'}
        threading.Thread(target=self.pbar_loop, args=(params, lambda x: x.checked_len,)).start()

        redditors = Redditors(reddit=self.reddit, _data=None)
        last = time.time()
        for user in redditors.partial_redditors(self.author_fullnames.keys()):
            if self.stop.is_set():
                return

            self.checked_len += 1
            if hasattr(user, 'created_utc'):
                if user.created_utc > self.dateline:  # Young accounts
                    self.dq_age.add(user.name)
                self.author_fullnames[user.fullname] = user.name  # Associate fullname with name
            else:  # ??? accounts (Reddit still returns suspended users' account creation times on this endpoint...)
                self.author_fullnames[user.fullname] = 'NULL*'  # So this should be unused; They also dont mark suspended accounts on this endpoint either, so can't check it

            # Avoid murdering the API

            if self.checked_len % 100 == 0:
                last += 1
                sleeptime = last - time.time()
                if sleeptime < 0:
                    continue
                time.sleep(sleeptime)

        time.sleep(0.11)  # Let progress bar wake up and close itself

        # Fix up author list; Replace fullnames with names
        for i in range(len(self.authors)):
            if self.authors[i] == 'Null':
                continue
            self.authors[i] = self.author_fullnames[self.authors[i]]

    def pbar_loop(self, params, check):
        time.sleep(0.3)  # Let at least one response come through first
        if params['total'] == 0:
            return
        pbar = tqdm(**params)
        while True:
            if self.stop.is_set():
                pbar.close()
                return
            n = check(self)
            pbar.n = n
            pbar.last_print_n = n
            pbar.refresh()
            if n >= pbar.total:
                if n > pbar.total:
                    for i in range(5):
                        print("WARNING: Number of iterations ({:d}) exceeds expected value ({:d})".format(n, pbar.total))
                pbar.close()
                return
            time.sleep(0.1)


def author_driver(reddit=None, cids=None, dateline=None):
    stop = threading.Event()
    try:
        # Assign work to thread & start
        athread = AuthorThread(reddit=reddit, cids=cids, dateline=dateline, stop=stop)
        athread.start()

        # Collect results & return
        while athread.is_alive():
            athread.join(1)
    except (KeyboardInterrupt, SystemExit):
        stop.set()
        raise

    return athread.authors, athread.dq_age


def main(update=False):
    with open('meta.json', 'r') as f:
        meta = json.load(f)

    file_name = meta['CID_Filename']

    print("{} comments from {}...".format('Updating' if update else 'Loading', file_name))
    with open(file_name, 'r') as f:
        if not update:
            comment_ids = ['t1_' + line.strip().split(':')[0] for line in f]
        else:
            comment_author_pairs = []  # Pre-existing pairs in the file
            comment_ids = []  # New comment ids to be checked
            for line in f:
                l = line.strip().split(':')
                if len(l) == 1:
                    comment_author_pairs.append(('t1_' + l[0], None))
                    comment_ids.append('t1_' + l[0])  # Only check those without an associated author already
                else:
                    comment_author_pairs.append(('t1_' + l[0], l[1]))

    # Start getting authors
    b = time.time()
    try:
        authors, dq_age = author_driver(reddit=CGCommons.init_reddit(), cids=comment_ids, dateline=meta['Dateline'])
    except (KeyboardInterrupt, SystemExit):
        time.sleep(0.3)
        print('\nWARNING: getAuthors is terminating early...')
        return
    except Exception as e:
        print(e)
        raise
    a = time.time()

    print("\nTook {:.2f}s to retrieve {} comment authors".format(a - b, len(authors)))
    print("Number of young accounts: {}".format(len(dq_age)))

    # Write results to file
    with open(file_name, 'w') as f:
        if not update:
            f.write('\n'.join('{}:{}'.format(x[0][3:], x[1]) for x in zip(comment_ids, authors)))
        else:
            new_pairs = dict(zip(comment_ids, authors))
            f.write('\n'.join('{}:{}'.format(x[0][3:], x[1] if x[1] else new_pairs[x[0]]) for x in comment_author_pairs))

    if update:  # Read in previous DQ-Age users and add to current list
        with open(file_name.rstrip('.txt') + '_DQ-Age.txt', 'r') as f:
            dq_age.update([line.strip() for line in f])

    with open(file_name.rstrip('.txt') + '_DQ-Age.txt', 'w') as f:
        f.write('\n'.join(sorted(dq_age, key=str.casefold)))

    # Calculate and write hashes to meta
    meta['CID_SHA256'] = CGCommons.hash(file_name)
    meta['DQAGE_SHA256'] = CGCommons.hash(file_name.rstrip('.txt') + '_DQ-Age.txt')
    print("\nComment ID SHA-256 Hash: {}\nDQ-Age SHA-256 Hash    : {}".format(meta['CID_SHA256'], meta['DQAGE_SHA256']))

    with open('meta.json', 'w') as outfile:
        json.dump(meta, outfile, indent=4)

    x = input("Done!")
    return


if __name__ == "__main__":
    y = True if input("Updating? Y/N: ").upper() == 'Y' else False
    main(update=y)
