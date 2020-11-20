from praw.models import MoreComments
import json
import CGCommons


def fetch_thread_cids(thread=None, reddit=None):
    submission = reddit.submission(url=thread)
    submission.comment_sort = 'old'
    sublist = []
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            sublist += top_level_comment.children
        else:
            sublist.append(str(top_level_comment.id))
    return sublist


def fetch_all_cids(reddit=None, meta=None):
    # Get each individual thread's comment IDs, then combine them into one list
    all_cid = []
    for thread in meta['threads']:
        thread_cids = fetch_thread_cids(thread=thread['link'], reddit=reddit)
        thread['length'] = len(thread_cids)
        all_cid += thread_cids

    return all_cid


def main(update=False):
    with open('meta.json', 'r') as f:
        meta = json.load(f)

    file_name = meta['CID_Filename']

    # Get comment IDs from all threads
    new_id = fetch_all_cids(reddit=CGCommons.init_reddit(), meta=meta)
    print("Found {} comments".format(len(new_id)))

    # Save IDs to file
    if not update:
        with open(file_name, "w") as f:
            f.write("\n".join(sorted(new_id)))
    else:  # Don't overwrite existing records
        new_id_set = set(new_id)
        comment_author_pairs = []
        pre_id_set = set()
        removed = 0
        with open(file_name, 'r') as f:
            for line in f:
                l = line.strip().split(':')
                if l[0] not in new_id_set:
                    removed += 1
                    continue
                pre_id_set.add(l[0])
                if len(l) == 1:
                    comment_author_pairs.append((l[0], None))
                else:
                    comment_author_pairs.append((l[0], l[1]))

        added = len(comment_author_pairs)
        comment_author_pairs += [(idx, None) for idx in new_id if idx not in pre_id_set]
        added = len(comment_author_pairs) - added

        print("\nRemoved {} comments\nAdded {} comments\n".format(removed, added))

        with open(file_name, 'w') as f:
            f.write('\n'.join('{}{}'.format(x[0], ':' + x[1] if x[1] else '') for x in sorted(comment_author_pairs, key=lambda x: x[0])))

    print("Comments saved in {}".format(file_name))

    # Calculate and save file's hash
    meta['CID_SHA256'] = CGCommons.hash(file_name)
    print("Comment ID SHA-256 Hash: {}".format(meta['CID_SHA256']))

    with open('meta.json', 'w') as outfile:
        json.dump(meta, outfile, indent=4)

    x = input("End..")
    return


if __name__ == "__main__":
    y = True if input("Updating? Y/N: ").upper() == 'Y' else False
    main(update=y)
