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
    def __init__(self, reddit=None, cids=None, dateline=None):
        super().__init__()
        self.reddit = reddit
        self.cids = cids
        self.dateline = dateline
        self.authors = []
        self.author_fullnames = {}
        self.dq_age = set()
        self.checked_len = 0

    def run(self):
        self.get_authors_fullnames(self.cids)
        self.check_authors()

    def get_authors_fullnames(self, ids: Iterable[str]):
        iterable = iter(ids)
        while True:
            last = time.time()
            chunk = list(islice(iterable, 100))
            if not chunk:
                break

            params = {"id": ",".join(chunk)}
            try:
                results = self.reddit.get(API_PATH["info"], params=params)
            except prawcore.exceptions.NotFound:
                # None of the given IDs matched any Redditor.
                continue

            for comment in results.children:
                if hasattr(comment, 'author_fullname'):
                    self.author_fullnames[comment.author_fullname] = None
                    self.authors.append(comment.author_fullname)
                else:
                    self.authors.append('Null')

            sleeptime = last + 1 - time.time()  # Avoid murdering the API
            if sleeptime < 0:
                continue
            time.sleep(sleeptime)

    def check_authors(self):
        redditors = Redditors(reddit=self.reddit, _data=None)
        last = time.time()
        for user in redditors.partial_redditors(self.author_fullnames.keys()):
            self.checked_len += 1
            if hasattr(user, 'created_utc'):
                if user.created_utc > self.dateline:
                    self.dq_age.add(user.name)
                self.author_fullnames[user.fullname] = user.name
            else:
                self.author_fullnames[user.fullname] = 'NULL*'

            sleeptime = last + 1 - time.time()  # Avoid murdering the API
            if sleeptime < 0 or self.checked_len % 100 != 0:
                continue
            time.sleep(sleeptime)
            last = time.time()

        for i in range(len(self.authors)):
            if self.authors[i] == 'Null':
                continue
            self.authors[i] = self.author_fullnames[self.authors[i]]


def pbar_loop(pbar, thread, mode):
    time.sleep(0.1)
    while True:
        n = len(thread.authors) if mode == 1 else thread.checked_len
        pbar.n = n
        pbar.last_print_n = n
        pbar.refresh()
        if n >= pbar.total:
            if n > pbar.total:
                for i in range(5):
                    print("WARNING: Number of iterations ({:d}) exceeds expected value ({:d})".format(n, pbar.total))
            return
        time.sleep(0.2)


def author_driver(reddit=None, cids=None, dateline=None):
    # Work splitter
    total_len = len(cids)

    # Assign work to thread & start
    athread = AuthorThread(reddit=reddit, cids=cids, dateline=dateline)
    athread.start()

    print("Collecting comment authors' UIDs....")

    # Progress bar 1, for comment-fullname translation
    pbar = tqdm(total=total_len, desc='Progress', unit=' Comments')
    p1 = threading.Thread(target=pbar_loop, args=(pbar, athread, 1,))
    p1.start()
    p1.join()
    pbar.close()

    print("\nAll comment authors' UIDs have been found. Now checking account creation times...")

    # Progress bar 2, for creation time checks
    pbar = tqdm(total=len(athread.author_fullnames), desc='Progress', unit=' Authors')
    p1 = threading.Thread(target=pbar_loop, args=(pbar, athread, 2,))
    p1.start()
    p1.join()
    pbar.close()

    # Collect results & return
    athread.join()

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
            comment_author_pairs = []
            comment_ids = []
            for line in f:
                l = line.strip().split(':')
                if len(l) == 1:
                    comment_author_pairs.append(('t1_' + l[0], None))
                    comment_ids.append('t1_' + l[0])
                else:
                    comment_author_pairs.append(('t1_' + l[0], l[1]))

    # Start getting authors
    b = time.time()
    authors, dq_age = author_driver(reddit=CGCommons.init_reddit(), cids=comment_ids, dateline=meta['Dateline'])
    a = time.time()

    print("Took {:.2f}s to retrieve {} comment authors".format(a - b, len(authors)))
    print("Number of young accounts: {}".format(len(dq_age)))

    # Write results to file

    with open(file_name, 'w') as f:
        if not update:
            f.write('\n'.join('{}:{}'.format(x[0][3:], x[1]) for x in zip(comment_ids, authors)))
        else:
            new_pairs = dict(zip(comment_ids, authors))
            f.write('\n'.join('{}:{}'.format(x[0][3:], x[1] if x[1] else new_pairs[x[0]]) for x in comment_author_pairs))

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
    main()
