# chatbot_functions
A repository of chatbot functions written in python using a postgres database.  This was developed for use with a matrix.org style server.

## How to use
This set of functions is meant to extend a chatbot.  It relies on a postgres database for long term memory  It is intened to be imported by a bot written in python, but you might have success with other languages.  I can't help you with that.

This was developed to augment a matrix.org style server.  The bot is expecting to be present in an UNENCRYPTED room (your mileage may vary with encrypted rooms) or rooms.

These functions almost universally expect to be called in response to a user in a room posting a message.  The function will be called with the username of the sender, the roomid, the contents of the message and handles to an already open database connection.

## Security Thougts
There are functions to save when a user last posted content in a room (to enable a '.seen @USERNAME' style command).  This means the bot is storing some user conversation data in the database.  

The bot has functions to log usage of keywords and counters in a wide array of topics.  This means as the bot 'listens' in a room it will build up a list of ALL users active in the room.  If the bot is in multiple rooms, it will build up lists of ALL users in EVERY room.  This bot is written in a way to prevent USER1 in ROOM_A from discovering the existance of USER2 in ROOM_B.  The bot should only be able to reveal information USER1 can glean elsewhere from ROOM_A.

## Test Suite
WIP.  This will demonstate calling the various bot methods and be used as a tool to validate the various functions work as intended.