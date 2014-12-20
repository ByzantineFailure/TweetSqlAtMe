TweetSqlAtMe
============

A Python 3.x Application to run SQL over Twitter.

Configuration xml is forthcoming once I stop the small test I'm running (@TweetSQLAtMeTes) and feel comfortable sanitizing it.

##Twitter syntax
"@ACCOUNTNAME UNIQUEID SQL"

UNIQUEID is any string that the posting twitter account has not used in conjunction with the given SQL before.  This is to get around Twitter's requirement that all tweets be unique.

If table A is (id int, content varchar(50)) and has 3 records, running "SELECT * FROM A;" will return:

    @REQUESTER UNIQUEID 1,content1;2,content2;3,content3;

Successful non-SELECT requests will return "Success!"

Failed requests will return either the DB error message or an application error message.

##Rate Limits
The minimum time limit between queries a user can post can be modified in the configuration XML.

If a user performs a request before their request rate limit is up, no response will be returned.

##Logging
All SQL, the user who tweeted it, the time of the tweet, and what the primary keyword of the tweet was is stored in the "log" table of the logging database specified in the XML.

Errors are logged in the "errors" table of the same database.  The SQL, user, timestamp and stack trace are stored.

##Commentary and Application Dependencies
The idea for this came when I spent 2 hours looking for a table a webservice in a legacy application used.  When I finally found it, its name was just 5 random capital letters. I commented to my PM that "The only excuse for that is you plan on tweeting your SQL to your database."

It actually got written because I may also have been drunk later that night.

It is in Python because you can be inebriated to the point that you have difficulty speaking intelligibly and still not screw up the syntax.  Also because I'd used the [twitter library](https://pypi.python.org/pypi/twitter) it uses [here](https://github.com/ByzantineFailure/PAX_Pinger).

It uses PostgreSQL because I already had an instance running locally and I'm familiar with administering it.  It uses [psycopg2](https://pypi.python.org/pypi/psycopg2) because I'd used it before [here](https://github.com/ByzantineFailure/PretendYourXyzzyDbTools).

##To Do List
Fix results formatting.  When you're inebriated, you forget that things like EXECUTE can return results too, not just SELECT.  Do this by checking if the cursor has any results when formatting the output.

Multithread the SQL Execution

Multithread the Twitter responses and have them use more than one account (account for the 1000/day rate limit).


