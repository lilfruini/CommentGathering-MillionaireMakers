import json


def get_dupes(a):
    a = a.copy()
    a.sort()
    dupes = set()
    last_item = ""
    for item in a:
        if last_item == item:
            dupes.add(item)
        last_item = item
    return dupes


def remover(rm_list=None, target=None):
    removed = 0
    for i, tf in enumerate(rm_list):
        if tf:
            del target[i - removed]
            removed += 1


def remove_dupes(authors=None, dq_age=None, dq_mult=None, cids=None, mode="DQ", meta=None):
    if mode not in {"DQ", "FirstOnly"}:
        x = input("Invalid duplicate action! Only DQ or FirstOnly is acceptable!")
        exit(1)

    dq_age.update({'Null', 'NULL*'})  # Everything in dq_age gets marked for removal
    rm_list = []
    rm_cache = set()
    for author in authors:
        if author in dq_age:
            rm_list.append(True)
        elif author in dq_mult:
            if mode == "DQ" or author in rm_cache:
                rm_list.append(True)
            else:
                # Mode is "FirstOnly"
                rm_cache.add(author)
                rm_list.append(False)
        else:
            rm_list.append(False)

    sub_cids = []
    sub_rm = []
    prev = 0
    cur = 0
    for thread in meta['threads']:
        cur += thread['length']
        sub_cids.append(cids[prev:cur])
        sub_rm.append(rm_list[prev:cur])
        prev = cur

    for i, (sub_cid, rm) in enumerate(zip(sub_cids, sub_rm)):
        remover(rm_list=rm, target=sub_cid)
        meta['threads'][i]['trunc_length'] = len(sub_cid)

    ret_list = []
    for sub_cid in sub_cids:
        ret_list += sub_cid
    return ret_list


def main():
    with open('meta.json', 'r') as f:
        meta = json.load(f)

    file_name = meta['CID_Filename']
    mode = meta['Duplicate Action']

    with open(file_name, 'r') as f:
        comment_ids = [line.strip() for line in f]

    with open(file_name.rstrip('.txt') + '_Authors.txt', 'r') as f:
        authors = [line.strip() for line in f]

    with open(file_name.rstrip('.txt') + '_DQ-Age.txt', 'r') as f:
        dq_age = [line.strip() for line in f]

    dq_mult = get_dupes(authors)
    print("Operating Mode: " + mode)
    print("{} users have young accounts!\n{} users have multiple posts!".format(len(dq_age), len(dq_mult)))

    before = len(comment_ids)
    comment_ids = remove_dupes(authors=authors, dq_age=set(dq_age), dq_mult=set(dq_mult), cids=comment_ids, mode=mode, meta=meta)
    after = len(comment_ids)

    with open(file_name.rstrip('.txt') + '_DQ-MultiPost.txt', 'w') as f:
        f.write('\n'.join(sorted(dq_mult, key=str.casefold)))

    with open(file_name.rstrip('.txt') + '_Truncated.txt', 'w') as f:
        f.write('\n'.join(comment_ids))

    with open('meta.json', 'w') as outfile:
        json.dump(meta, outfile, indent=4)

    x = input("Removed {} comments!".format(before - after))


if __name__ == "__main__":
    main()
