import importlib.util
import sys

ver = sys.version_info
if ver < (3, 5):
    x = input("Currently running Python {:d}.{:d}.{:d}\nPlease use Python 3.5 or above. Enter Y to ignore. ".format(ver[0], ver[1], ver[2])).upper()
    if x != "Y":
        exit(1)

if importlib.util.find_spec('praw') is None:
    x = input("The PRAW package is required but not installed.\nPlease run 'pip3 install praw' in your terminal.\nEnd..")
    exit(2)

if importlib.util.find_spec('tqdm') is None:
    x = input("The tqdm package is required but not installed.\nPlease run 'pip3 install tqdm' in your terminal.\nEnd..")
    exit(3)

# Yes I'm violating Python style guide, sue me
import getWinner
import getAuthors
import getComments
import dupeCmtCheck
import removeInvalids
import praw

p = praw.__version__.split('.')
praw_ver = (int(p[0]), int(p[1]), int(p[2]))

if praw_ver < (7, 1, 0):
    x = input("Currently running PRAW {}\nThe PRAW package version is too low. Required version >= 7.1.0.\nPlease run 'pip3 install praw' in your terminal.\nEnd..".format(praw.__version__))
    exit(2)

while True:
    x = int(input("\nHello!\nWhat would you like to launch?\n0. Exit\n1. getComments\n2. getAuthors\n3. removeInvalids\n4. getWinner\n5. dupeCmtCheck\n\nOption: "))

    parts = {
        1: getComments,
        2: getAuthors,
        3: removeInvalids,
        4: getWinner,
        5: dupeCmtCheck,
    }

    if not isinstance(x, int) or not 0 <= x < 6:
        continue

    if x == 0:
        print("Goodbye")
        exit(0)

    if x == 1 or x == 2:
        y = True if input("Updating? Y/N: ").upper() == 'Y' else False
        parts.get(x).main(update=y)
    else:
        parts.get(x).main()
