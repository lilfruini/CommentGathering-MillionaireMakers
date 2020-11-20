from praw.models import Comment
import json
import time
import threading
import CGCommons

class AuthorThread(threading.Thread):
    def __init__(self, reddit=None, cids=None, dateline=None):
        super().__init__()
        self.reddit = reddit
        self.cids = cids
        self.dateline = dateline
        self.authors = []
        self.dq_age = set()

    def run(self):
        for cid in self.cids:
            author = Comment(self.reddit, id=cid).author
            try:
                if author is None:  # Deleted comment
                    self.authors.append("Null")
                    continue

                if author.created_utc > self.dateline:  # New user
                    self.dq_age.add(author.name)

                self.authors.append(author.name)
            except:  # thread CANNOT crash, typically means suspended user
                self.authors.append('NULL*')


def mt_author(t_no=10, reddit=None, cids=None, dateline=None):
    # Work splitter
    total_len = len(cids)
    chunk_len = total_len // t_no + 1
    cid_chunks = [cids[x:x + chunk_len] for x in range(0, len(cids), chunk_len)]

    # Assign work to threads
    threads = []
    for i in range(t_no):
        if i == len(cid_chunks):
            break
        threads.append(AuthorThread(reddit=reddit, cids=cid_chunks[i], dateline=dateline))

    # Start threads
    for thread in threads:
        thread.start()

    # Progress Reporter (Just a bunch of math to show progress) #
    pct_done = 0.0
    done = 1
    hang = 0
    while pct_done < 99.51:
        old_done = done
        done = 0
        for thread in threads:
            done += len(thread.authors)
        pct_done = done / total_len * 100
        rate = (done - old_done) / 3
        etd = (1 / 60) * (total_len - done) / rate if rate != 0 else 999
        print("Progress: {}/{} ({:.2f}% - {:.2f}/s) ETD: {:.2f} minutes".format(done, total_len, pct_done, rate, etd))

        # if rate == 0 and (hang := hang + 1) > 3:
        #     break
        hang = hang + 1
        if rate == 0 and hang > 3:
            break
        elif rate != 0:
            hang = 0
        time.sleep(3)
    # (END) Progress Reporter #

    for thread in threads:
        thread.join()

    # Collect results & return
    a_list = []
    dq_age = set()
    for thread in threads:
        a_list += thread.authors
        dq_age.update(thread.dq_age)

    return a_list, dq_age


def main():
    with open('meta.json', 'r') as f:
        meta = json.load(f)

    file_name = meta['CID_Filename']

    with open(file_name, 'r') as f:
        comment_ids = [line.strip() for line in f]

    # Start getting authors
    b = time.time()
    authors, dq_age = mt_author(t_no=meta['Concurrent_Threads'], reddit=CGCommons.init_reddit(), cids=comment_ids, dateline=meta['Dateline'])
    a = time.time()

    print("Took {:.2f}s to retrieve {} comment authors".format(a - b, len(authors)))
    print("Number of young accounts: {}".format(len(dq_age)))

    # Write results to file
    with open(file_name.rstrip('.txt') + '_Authors.txt', 'w') as f:
        f.write('\n'.join(authors))

    with open(file_name.rstrip('.txt') + '_DQ-Age.txt', 'w') as f:
        f.write('\n'.join(sorted(dq_age, key=str.casefold)))

    # Calculate and write hashes to meta
    meta['AUID_SHA256'] = CGCommons.hash(file_name.rstrip('.txt') + '_Authors.txt')
    meta['DQAGE_SHA256'] = CGCommons.hash(file_name.rstrip('.txt') + '_DQ-Age.txt')
    print("\nAUID   SHA-256 Hash: {}\nDQ-Age SHA-256 Hash: {}".format(meta['AUID_SHA256'], meta['DQAGE_SHA256']))

    with open('meta.json', 'w') as outfile:
        json.dump(meta, outfile, indent=4)

    x = input("Done!")
    return


if __name__ == "__main__":
    main()
