TweetSqlAtMe
============

A Python 3.x Application to run SQL over Twitter.

Configuration xml is forthcoming once I stop the small test I'm running (@TweetSQLAtMeTes) and feel comfortable sanitizing it.

##Twitter syntax
"@ACCOUNTNAME UNIQUEID SQL"
UNIQUEID is any string that the posting twitter account has not used in conjunction with the given SQL before.  This is to get around Twitter's requirement that all tweets be unique.

##Rate Limits
The minimum time limit between queries a user can post can be modified in the configuration XML.

##Commentary and Application Dependencies
The idea for this came when I spent 2 hours looking for a table a webservice in a legacy application used.  When I finally found it, it was called "v_BPDGR". I commented to my PM that "The only excuse for that is you plan on tweeting your SQL to your database."

It actually got written because I may also have been drunk later that night.

It is in Python because you can be inebriated to the point that you have difficulty forming words and still not screw up the syntax.  Also because I'd used the twitter library this uses [here](https://github.com/ByzantineFailure/PAX_Pinger).

It uses PostgreSQL because I already had an instance running locally and I'm familiar with administering it.  It uses psycopg2 because I'd used it before [here](https://github.com/ByzantineFailure/PretendYourXyzzyDbTools).


