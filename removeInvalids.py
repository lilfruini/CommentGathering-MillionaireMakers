import json
import hashlib

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


def get_dupes(a):
    # Duplicate and sort list
    a = a.copy()
    a.sort()

    dupes = set()
    last_item = ""
    # Find any consecutive items in the list
    for item in a:
        if last_item == item:
            dupes.add(item)
        last_item = item
    return dupes


def remover(rm_list=None, target=None):
    # Removes elements from 'target' list based on the parallel truth-table list 'rm_list'
    removed = 0
    for i, truefalse in enumerate(rm_list):
        if truefalse:
            del target[i - removed]
            removed += 1


def remove_dupes(authors=None, dq_age=None, dq_mult=None, cids=None, meta=None):
    mode = meta['Duplicate Action']
    # if (mode := meta['Duplicate Action']) not in {"DQ", "FirstOnly"}:
    if mode not in {"DQ", "FirstOnly"}:
        x = input("Invalid duplicate action! Only DQ or FirstOnly is acceptable!")
        exit(1)
    print("Operating Mode: " + mode)

    dq_age.update({'Null', 'NULL*'})  # Everything in dq_age gets marked for removal
    rm_list = []
    rm_cache = set()
    # Mark true/false in a parallel list to indicate if the element should be deleted later
    for author in authors:
        if author in dq_age:
            rm_list.append(True)
        elif author in dq_mult:
            if mode == "DQ" or author in rm_cache:  # Being in rm_cache means author has appeared once
                rm_list.append(True)
            else:
                rm_cache.add(author)  # Remember that author has been seen once already
                rm_list.append(False)  # FirstOnly mode, so this comment is spared
        else:
            rm_list.append(False)

    # Split the full comment ID list into thread-specific sublists first before removing
    # This is to make it easy to calculate the truncated length of each thread's comment IDs
    sub_cids = []
    sub_rm = []
    prev = 0
    cur = 0
    for thread in meta['threads']:
        cur += thread['length']
        sub_cids.append(cids[prev:cur])
        sub_rm.append(rm_list[prev:cur])
        prev = cur

    # Remove marked elements from the sublists, and append new length of CIDs
    for i, (sub_cid, rm) in enumerate(zip(sub_cids, sub_rm)):
        remover(rm_list=rm, target=sub_cid)
        meta['threads'][i]['trunc_length'] = len(sub_cid)

    # Recombine the truncated sublists and return it
    ret_list = []
    for sub_cid in sub_cids:
        ret_list += sub_cid
    return ret_list


def main():
    # Load files
    with open('meta.json', 'r') as f:
        meta = json.load(f)

    file_name = meta['CID_Filename']

    with open(file_name, 'r') as f:
        comment_ids = [line.strip() for line in f]

    with open(file_name.rstrip('.txt') + '_Authors.txt', 'r') as f:
        authors = [line.strip() for line in f]

    with open(file_name.rstrip('.txt') + '_DQ-Age.txt', 'r') as f:
        dq_age = [line.strip() for line in f]

    # Find multiposters
    dq_mult = get_dupes(authors)
    print("{} users have young accounts!\n{} users have multiple posts!".format(len(dq_age), len(dq_mult)))

    # Remove all invalid comment IDs
    before = len(comment_ids)
    comment_ids = remove_dupes(authors=authors, dq_age=set(dq_age), dq_mult=set(dq_mult), cids=comment_ids, meta=meta)
    after = len(comment_ids)

    # Save multiposter usernames & the truncated comment ID list
    with open(file_name.rstrip('.txt') + '_DQ-MultiPost.txt', 'w') as f:
        f.write('\n'.join(sorted(dq_mult, key=str.casefold)))

    with open(file_name.rstrip('.txt') + '_Truncated.txt', 'w') as f:
        f.write('\n'.join(comment_ids))

    # Calculate file hashes and save
    meta['DQMULT_SHA256'] = hash_sha256(file_name.rstrip('.txt') + '_DQ-MultiPost.txt')
    meta['TRUNC_SHA256'] = hash_sha256(file_name.rstrip('.txt') + '_Truncated.txt')
    print("\nDQMult SHA-256 Hash: {}\nT_CID  SHA-256 Hash: {}".format(meta['DQMULT_SHA256'], meta['TRUNC_SHA256']))

    with open('meta.json', 'w') as outfile:
        json.dump(meta, outfile, indent=4)

    x = input("Removed {} comments!".format(before - after))
    return


if __name__ == "__main__":
    main()
