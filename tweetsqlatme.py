from twitter_handler import *
from db_interactions import *
from rate_limiter import *
from configuration_reader import *
import time
import traceback

CONFIG_LOCATION = "configuration.xml";
OAUTH_LOCATION = "oauth.dat";
USERNAME = "@TweetSQLAtMeTes";

configuration = getConfiguration(CONFIG_LOCATION);
twitter_handler = make_twitter_handler(configuration, OAUTH_LOCATION);
command_pool = get_command_pool(configuration);
log_pool = get_log_pool(configuration);
db_handler = make_database_interactions(log_pool, command_pool);
rate_limiter = make_rate_limiter(configuration);

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
                if rate_limiter.checkRateLimit(user):
                        print("Rate Limit");
                else:
                        rate_limiter.limitUser(user);
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
                testdata['id'] = "?";
                handle_message(testdata);
'''

