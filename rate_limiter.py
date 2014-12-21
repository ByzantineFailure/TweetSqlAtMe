import threading
import time
import sys
from configuration_reader import *

#Python lists are thread-safe.  Their contents are not.
#Luckily, provded we don't manipulate the contents (Strings)
#This crazy-lazy implementation should work

class RateLimiter:
        def __init__(self, config):
                self.rateLimit = int(config['settings']['RateLimit']);
                self.limitedUsers = [];
        
        def checkRateLimit(self, user):
                return user in self.limitedUsers;

        def limitUser(self, user):
                self.limitedUsers.append(user);
                thread = RateLimiterThread(self.rateLimit, self.limitedUsers, user);
                thread.start();

class RateLimiterThread(threading.Thread):
        def __init__(self, rateLimit, items, item):
                threading.Thread.__init__(self);
                self.rateLimit = rateLimit;
                self.items = items;
                self.item = item;
        def run(self):
                time.sleep(self.rateLimit);
                try:
                        self.items.remove(self.item);
                except ValueError:
                        sys.stdout.write("Tried to remove " + self.item + " but it didn't exist!\n");

def make_rate_limiter(config):
        return RateLimiter(config);



