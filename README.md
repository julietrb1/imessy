# iMessy

> ## No longer under active development.
>
>  📚 This repository has been archived, as it served its purpose and is no longer under active development. Good to see you, though!

This is a simple Python application (for Mac) that makes use of numpy and matplotlib to produce four sets of graphs that give insights into a conversation held via iMessage.

It is far from complete at this stage, but provides a good starting point for the project to evolve.

![iMessy graphs screenshot](https://github.com/dylanjboyd/imessy/raw/master/screenshot.png)

## Why the weird name?
Great question! Since this has everything to do with messaging, I figured a name with the first syllable of that word would be a stellar choice, and since this was done far past late, that name turned out to be more weird than not. Enticing story, innit?

## How do I run iMessy?
1. Ensure you're running the latest Python 3.x, and the dependencies are installed: `pip3 install pandas numpy matplotlib`
2. Run the script in Terminal, passing your chat ID as the only argument; e.g. `python3 messy.py 123`

## How do I find my chat ID?
Chats are stored in a SQLite database in your *~/Library/Messages* folder. The way I prefer to look for chats is using [DB Browser for SQLite](http://sqlitebrowser.org). 

1. Install and fire up DB Browser
2. Navigate to *~/Library/Messages*
3. Open up *chat.db*
4. Click *Browse Data*
5. Select the *chat* table
6. Choose your chat using the phone numbers (or other identifier) from the *guid* or *chat_identifier* columns
7. Use the value in the *ROW_ID* column as the argument to iMessy

## I'm technically curious
Pretty much all I've learned about this database in order to start coding iMessy came from [Steven Morse's "Analyzing iMessage conversations"](https://stmorse.github.io/journal/iMessage.html). Thanks to Steven for the great educational read.

## Why did you choose to make this?
Genuine curiosity, and far too much spare time.

## FAQs
### python3 and pip3 aren't found
Those commands are what I type to allow macOS to distinguish between the (in-built) version of Python 2, and the (wonderfully) newer v3. You may well not need to do so, and simply using `python` or `pip` may work wonders for you. Ensure you check the version using `python --version`. Python 2.x may well work, but I haven't tested it.
