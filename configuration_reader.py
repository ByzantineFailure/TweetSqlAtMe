import os
from xml.etree.ElementTree import ElementTree

def getConfiguration(configurationPath):
	tree = ElementTree();
	tree.parse(configurationPath);
	root = tree.getroot();

	authData = root.find('TwitterAuthDetails');
	dbCredentials = root.find('DatabaseCredentials');
	settingsData = root.find('AppSettings');

	authOutput = dict();
	dbOutput = dict();
	settingsOutput = dict();

	for child in authData:
		authOutput[child.tag] = child.text;
	
	for child in dbCredentials:
		dbOutput[child.tag] = child.text;
	
	for child in settingsData:
		settingsOutput[child.tag] = child.text;

	return dict(auth=authOutput, db=dbOutput, settings=settingsOutput);

def writeOAuthDanceValues(configurationPath, OAuth_Token, OAuth_Secret):
	tree = ElementTree();
	tree.parse(configurationPath);
	root = tree.getroot();

	authData = root.find('TwitterAuthDetails');
	authData.find('OAuthToken').text = OAuth_Token;
	authData.find('OAuthSecret').text = OAuth_Secret;
	tree.write(configurationPath);
