from twitter_handler import *
from db_interactions import *
import time
import traceback

CONFIG_LOCATION = "configuration.xml";
OAUTH_LOCATION = "oauth.dat";
USERNAME = "@TweetSQLAtMeTes";

twitter_handler = make_twitter_handler(CONFIG_LOCATION, OAUTH_LOCATION);
db_handler = make_database_interactions(CONFIG_LOCATION);

def get_sql_from_message(text):
        return ' '.join(text.strip().split(' ')[2:]);


def handle_message(msg):
       if 'hangup' in msg:
                raise Exception("Stream Failed!");
       if 'text' in msg:
                user = get_twitter_message_user(msg);
                tweetid = msg['id'];
                if user.lower() == USERNAME[1:].lower():
                        return;
                command = get_twitter_message_message(msg);
                command = get_sql_from_message(command);
                print(command);
                userLength = len(user);
                if not db_handler.checkRateLimit(user):
                        print("Rate Limit");
                else:
                        response = db_handler.runCommand(command, user);
                        response = "@" + user + " " + (str(datetime.datetime.now())[-5:]) + " " + response;
                        print(response);
                        twitter_handler.sendReply(response[:140], user, tweetid);

def control_loop():
     for msg in twitter_handler.getStreamIterator():
        handle_message(msg);

while(True):
        try:
                control_loop();
        except:
                print(traceback.format_exc());
                time.sleep(90);
                twitter_handler = make_twitter_handler(CONFIG_LOCATION, OAUTH_LOCATION);
                print("Handler restarted");

#Testing stuff
'''
while(True):
        command = input("Feed me, Seymour: ");
        if command == "exit":
                break;
        else:
                testdata = dict();
                testdata['text'] = command;
                testdata['user'] = dict();
                testdata['user']['screen_name'] = "TESTUSER";
                testdata['id
                handle_message(testdata);
'''

