import getWinner
import getAuthors
import getComments
import dupeCmtCheck
import removeInvalids
import sys

if sys.version_info < (3, 5):
    x = input("Please use Python 3.5 or above. Enter Y to ignore. ").upper()
    if x != "Y":
        exit(1)

while True:
    x = int(input("\nHello!\nWhat would you like to launch?\n0. Exit\n1. getComments\n2. getAuthors\n3. removeInvalids\n4. getWinner\n5. dupeCmtCheck\n\nOption: "))

    parts = {
        1: getComments,
        2: getAuthors,
        3: removeInvalids,
        4: getWinner,
        5: dupeCmtCheck,
        0: 'QuickNDirty'
    }

    parts.get(x).main()