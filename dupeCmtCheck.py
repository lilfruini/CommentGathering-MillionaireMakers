import json

def dupe_exists(cids):
    dupes = []
    last_cid = ""
    # Check for consecutive duplicates
    for cid in cids:
        if last_cid == cid:
            dupes.append(cid)
        last_cid = cid

    # Check the total length of the list VS length of a set of the list
    if len(dupes) > 0 or len(cids) != len(set(cids)):
        print("Duplicates found!\nTotal Duplicates: {}\nConsecutive Duplicates: {}\nDupes: {}".format(len(cids) - len(set(cids)), len(dupes), dupes))
        return True
    return False


def main():
    with open('meta.json', 'r') as f:
        meta = json.load(f)

    with open(meta['CID_Filename'], 'r') as f:
        comment_ids = [line.strip() for line in f]

    if dupe_exists(comment_ids):
        x = input("ERROR!")
        exit(1)
    else:
        x = input("All Good!")
        return


if __name__ == "__main__":
    main()