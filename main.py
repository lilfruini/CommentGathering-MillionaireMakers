import getWinner
import getAuthors
import getComments
import dupeCmtCheck
import removeInvalids
import sys
import importlib.util

if sys.version_info < (3, 5):
    x = input("Please use Python 3.5 or above. Enter Y to ignore. ").upper()
    if x != "Y":
        exit(1)


if importlib.util.find_spec('praw') is None:
    x = input("The PRAW package is required but not installed.\nPlease run 'pip install praw' in your terminal.\nEnd..")
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

    if x == 0:
        print("Goodbye")
        exit(0)

    parts.get(x).main()
