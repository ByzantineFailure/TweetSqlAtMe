from twitter import *
from configuration_reader import *

class TwitterHandler(object):
	def __init__(self, config, oauth_location, config_location):
		auth = config['auth']

		if(not auth['OAuthToken'] or not auth['OAuthSecret']):
			oauth_dance(auth['AppName'], auth['API_Key'], auth['API_Secret'], oauth_location);
			auth['OAuthToken'], auth['OAuthSecret'] = read_token_file(oauth_location);
			writeOAuthDanceValues(config_location, auth['OAuthToken'], auth['OAuthSecret']);
			#Clean up after ourselves
			os.remove(oauth_location);

		self.twitter_object = Twitter(auth=OAuth(auth['OAuthToken'], auth['OAuthSecret'],
                               auth['API_Key'], auth['API_Secret']));
		self.twitter_stream = TwitterStream(auth=OAuth(auth['OAuthToken'], auth['OAuthSecret'],
                               auth['API_Key'], auth['API_Secret']), domain='userstream.twitter.com');
	
	def getStreamIterator(self):
		return self.twitter_stream.user();

	def sendReply(self, text, user, reply_to_id):
		self.twitter_object.statuses.update(status=text, in_reply_to_screen_name=user, in_reply_to_status_id=reply_to_id);
	
def get_twitter_message_user(message):
	return message['user']['screen_name'];

def get_twitter_message_message(message):
	return message['text'];

def make_twitter_handler(config, oauth_location, config_location):
	return TwitterHandler(config, oauth_location, config_location);

