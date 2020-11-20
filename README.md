# CommentGathering-MillionaireMakers
Hello! If you're here you're probably looking to validate the results of a draw or perform a draw yourself. 

<br/>

## Dependencies
- **[Python >=3.5][py-org]**
- The **`PRAW`** package (`pip3 install praw`)
- The **`tqdm`** package (`pip3 install tqdm`)

<br/>

## Configuration
#### `meta.json`
  - `threads`: Link to the drawing thread(s), if multiple, add a new set of `{}`!
  - `CID_Filename`: The filename of the comment ID file
  - `Dateline`: The maximum creation time of a user's account in [epoch time]. Everything younger will end up in `DQ-Age`. Set to `-1`, or the future to disable this check.
  - `Duplicate Action`: **DQ**: Delete all duplicate authors' comments or **FirstOnly**: Delete all but first comment 
  - `WinnerFromFile`: Which comment list to draw from - **Truncated** or **Original**
  - `DrawTime`: Time the draw starts in [epoch time]. Starts counting blocks from this time
  - `WaitTillBlock`: The n-th block which will be the "winning block". Default: 3 
  - `Win_Hash`: Hash of the winning block. Auto-filled via API if blank. If present, will be used by `getWinner`.

Everything else should fill up automatically after running the scripts!

---  

#### `auth.json`
Obtain client id and secret from [here](https://www.reddit.com/prefs/apps/). User agent can be anything.

<br/>

## Scripts
##### (In order of which they should be run)
- `main` - Launcher for the other scripts, also checks dependencies.
- `getComments` - Gets comments from threads specified and saves to `meta.json/CID_Filename` file.
- `dupeCmtCheck` - Checks comment IDs for duplicates.
- `getAuthors` - Gets author usernames based on the comments collected. Users who deleted their comments will show up as 'Null'.
Also generates `DQ-Age.txt`, which contains usernames of accounts which were created after `meta.json/dateline`.
- `removeInvalid` - Removes comments associated with 'Null', 'NULL*' or `DQ-Age.txt` users.
<br/>Users who double post either have all their comments deleted, or only have their first one remain
- `getWinner` - Gets the winner of the draw. If run before draw, will wait until `meta.json/DrawTime` and then wait for the winning block to be mined. 
Once mined, the winner will be displayed and saved to `meta.json`. 


As a time-saving measure (specifically for large threads), `getComments` and `getAuthors` 
will both ask if you are 'Updating' the existing comment list when launched:
 
- Responding `Y/y` will only update entries in the comment list that require updating, 
such as a new comment, or a comment without an associated author; 
- Otherwise, the scripts will start from scratch and overwrite any and all previous data.

<br/>

## Verifying past draws
Please do take note that the comments and/or user account statuses may have changed since the draw. This could be due to users deleting comments or their account.

As such, `getComments` and `getAuthors` will probably return a different list of IDs. Only the other scripts may be run with the provided ID, author and DQ lists; These should return the same results.

Also, the files are (mostly) made in Linux, so if you're using another OS, the newline character may differ, resulting in a hashsum mismatch. 

[py-org]: <https://www.python.org/downloads/>
[epoch time]: <https://www.epochconverter.com/>
