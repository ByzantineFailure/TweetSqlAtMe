from twitter_handler import *
from db_interactions import *
from rate_limiter import *
from configuration_reader import *
import time
import traceback
import threading
import sys

CONFIG_LOCATION = "configuration.xml";
OAUTH_LOCATION = "oauth.dat";
USERNAME = "@TweetSQLAtMeTes";

configuration = getConfiguration(CONFIG_LOCATION);
twitter_handler = make_twitter_handler(configuration, OAUTH_LOCATION, CONFIG_LOCATION);
command_pool = get_command_pool(configuration);
log_pool = get_log_pool(configuration);
db_handler = make_database_interactions(log_pool, command_pool);
rate_limiter = make_rate_limiter(configuration);

def get_sql_from_message(text):
        return ' '.join(text.strip().split(' ')[2:]);

#Threading this is both completely necessary and not at all bug-prone
#WEBSCALE WEBSCALE WEBSCALE WEBSCALE WEBSCALE WEBSCALE WEBSCALE WEBSCALE
class MessageHandlerThread(threading.Thread):
        def __init__(self, msg, doTweet, command_pool, log_pool):
                threading.Thread.__init__(self);
                self.msg = msg;
                self.doTweet = doTweet;
                self.db_handler = make_database_interactions(log_pool, command_pool);
        
        def run(self):
               if 'hangup' in self.msg:
                        raise Exception("Stream Failed!");
               if 'text' in self.msg:
                        user = get_twitter_message_user(self.msg);
                        tweetid = self.msg['id'];
                        if user.lower() == USERNAME[1:].lower():
                                sys.stdout.flush();
                                return;
                        command = get_twitter_message_message(self.msg);
                        command = get_sql_from_message(command);
                        sys.stdout.write(command + '\n');
                        userLength = len(user);
                        if rate_limiter.checkRateLimit(user):
                                sys.stdout.write("Rate Limit\n");
                                sys.stdout.flush();
                        else:
                                rate_limiter.limitUser(user);
                                response = self.db_handler.runCommand(command, user);
                                response = "@" + user + " " + (str(datetime.datetime.now())[-5:]) + " " + response;
                                sys.stdout.write(response + '\n');
                                if self.doTweet:
                                        twitter_handler.sendReply(response[:140], user, tweetid);
                                sys.stdout.flush();


def handle_message(msg, doTweet):
        thread = MessageHandlerThread(msg, doTweet, command_pool, log_pool);
        thread.start();

def control_loop():
     for msg in twitter_handler.getStreamIterator():
        handle_message(msg, True);

def control_loop_test():
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
                        handle_message(testdata, False);
        sys.stdout.flush();

while(True):
        try:
                control_loop();
        except:
                sys.stdout.write(traceback.format_exc() + '\n');
                time.sleep(90);
                twitter_handler = make_twitter_handler(configuration, OAUTH_LOCATION);
                sys.stdout.write("Handler restarted\n");
                sys.stdout.flush();




