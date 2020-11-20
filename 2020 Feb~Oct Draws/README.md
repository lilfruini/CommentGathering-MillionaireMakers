# DISCLAIMER
The draws in this folder were performed using an older version of the comment collection scripts. 
These old scripts(specifically `getAuthors`) were deprecated since they fail to respect Reddit's API rate limits. 
They are provided here for record keeping, please don't use `getAuthors` for the purpose of collecting author names.
Visit the repository head for updated scripts, which have new improvements as well!
 
To verify a draw in this folder, use the scripts in this folder; See [here](#Verifying-past-draws) for instructions

Also, the old `getAuthors` script could tell if a user was suspended, the new ones do not 
(the new endpoint used does not return this info), so you might see some `NULL*` authors in these files.

# CommentGathering-MillionaireMakers
Hello! If you're here you're probably looking to validate the results of a draw or perform the draw yourself. 

Before starting, make sure you have **[Python >=3.5][py-org]** and the **PRAW** package (`pip install praw`). 

## Configuration
#### `meta.json`
  - `threads`: Link to the drawing thread(s), if multiple, add a new set of `{}`!
  - `CID_Filename`: The filename of the comment ID file
  - `Dateline`: The maximum creation time of a user's account in [epoch time]. Everything younger will end up in `DQ-Age`
  - `Concurrent_Threads`: How many threads to use to request author names from Reddit. (In `getAuthors.py`)
                          I'd suggest keeping your rate to about 100 requests/s. Ping dependant.
  - `Duplicate Action`: **DQ**: Delete all duplicate authors' comments or **FirstOnly**: Delete all but first comment 
  - `WinnerFromFile`: Which comment list to draw from - **Truncated** or **Original**
  - `DrawTime`: Time the draw starts in [epoch time]. Starts counting blocks from this time
  - `WaitTillBlock`: The n-th block which will be the "winning block". Default: 3 
  - `Win_Hash`: Hash of the winning block. Auto-filled via API if blank. If present, will be used by `getWinner`.

Everything else should fill up automatically after running the scripts!

---  

#### `auth.json`
Obtain client id and secret from [here](https://www.reddit.com/prefs/apps/). User agent can be anything.

<br/><br/>

## Scripts
##### (In order of which they should be run)
`getComments` - Gets comments from threads specified and saves to `meta.json/CID_Filename` file

`dupeCmtCheck` - Checks comment IDs for duplicates

`getAuthors` - Gets author usernames based on the comments collected.Set more threads to speed things up!
<br/>Users who deleted their comments will show up as 'Null'. Suspended users show up as 'NULL*'.
<br/>Generates `DQ-Age.txt`, which contains usernames of accounts which were created after `meta.json/dateline`.

`removeInvalid` - Removes comments associated with 'Null', 'NULL*' or `DQ-Age.txt` users.
<br/>Users who double post either have all their comments deleted, or only have their first one remain

`getWinner` - Gets the winner of the draw. If run before draw, will wait until `meta.json/DrawTime` and then wait for the winning block to be mined. 
Once mined, the winner will be displayed and saved to `meta.json`. 

<br/><br/>

## Verifying past draws
Please do take note that the comments and/or user account statuses may have changed since the draw. This could be due to users deleting comments or their account.
<br/>As such, `getComments` and `getAuthors` will probably return a different list of IDs. Only the other scripts may be run with the provided ID, author and DQ lists; These should return the same results.
<br/>
<br/>Also, the files are (mostly) made in Linux, so if you're using another OS, the newline character may differ, resulting in a hashsum mismatch. 

[py-org]: <https://www.python.org/downloads/>
[epoch time]: <https://www.epochconverter.com/>
