import traceback
import datetime
import psycopg2
import psycopg2.extras
from configuration_reader import *

'''
Playground limitations:
SET statement_timeout TO 5000;
'''

'''
LogTable Structure:
CREATE TABLE log (
	id bigserial primary key,
	username varchar(50) NOT NULL,
	commandtext varchar(150) NOT NULL,
	time timestamp default NULL,
	sel boolean NOT NULL default '0',
	upd boolean NOT NULL default '0',
	del boolean NOT NULL default '0',
	ins boolean NOT NULL default '0',
	drp boolean NOT NULL default '0',
	crt boolean NOT NULL default '0'
);
Maybe create an index on username for some time limiting

ErrorTable Structure:
CREATE TABLE Errors (
	id bigserial primary key,
	username varchar(50) NOT NULL,
	commandText varchar(150) NULL,
	exception TEXT NOT NULL,
	time timestamp NOT NULL
);
'''

class DatabaseInteractions:
	def __init__(self, config_location):
		config = getConfiguration(config_location);
		self.dbConnStr = config['db']['PlaygroundConnectionString'];
		self.logConnStr = config['db']['LogConnectionString'];
		self.rateLimit = int(config['settings']['RateLimit']);
	
	def checkRateLimit(self, user):
		try:
			now = datetime.datetime.now();
			logConn = psycopg2.connect(self.logConnStr);
			logConn.autocommit = True;
		except:
			return False;
		try:
			cur = logConn.cursor();
			checkCommand = "SELECT time FROM Log WHERE username = %s ORDER BY time DESC LIMIT 1";
			result = True;
			
			cur.execute(checkCommand, (user,));

			if cur.rowcount < 1:
				result = True;
			else:
				log = cur.fetchone();
				checktime = log[0] + datetime.timedelta(milliseconds=self.rateLimit);
				
				if checktime > now:
					result = False;
				else:
					result = True;

			logConn.close();
			return result;
		except:
			self.logError(traceback.format_exc(), user, "RATE CHECK", logConn);
			return False;

	def runCommand(self, text, user):
		try:
			commandConn = psycopg2.connect(self.dbConnStr);
			commandConn.autocommit = True;
		except:
			print(traceback.format_exc());
			return "Unable to connect to database!";

		try:
			logConn = psycopg2.connect(self.logConnStr);
			logConn.autocommit = True;
		except:
			commandConn.close();
			return "Unable to connect to logging db.  Sorry, no SQL!  (I suck, I know)";
		
		keyword = self.__getSqlKeyword(text);
		result = "";
		if keyword.lower() == "select":
			result = self.__runSelect(text, user, commandConn, logConn);
		else:
			result = self.__runOther(text, user, keyword, commandConn, logConn);
		
		commandConn.close();
		logConn.close();
		return result;
	
	def __getSqlKeyword(self, commandText):
		split = commandText.split(' ');
		return split[0];

	def __runSelect(self, commandText, user, conn, logConn):
		cur = conn.cursor();
		try:
			cur.execute(commandText);
			self.__logCommand(commandText, user, "select", logConn);
		except psycopg2.Error as e:
			self.__logCommand(commandText, user, "select", logConn);
			return e.pgerror;
		except:
			self.logError(traceback.format_exc(), user, commandText, logConn);
			return "Some non-SQL error occured.  It was logged.  Sorry!";
		
		if cur.rowcount == 0:
			results = "Select returned no results";
		else:
			results = "";
			for record in cur:
				results += self.__formatResult(record);
				if len(results) >= 140:
					break;
		
		cur.close();
		return results;
	
	def __formatResult(self, row):
		result="";
	
		for value in row:
			result = result + str(value) + ",";
		
		#remove trailing comma
		result = result[:-1];
		result = result + ";";
		return result;

	def __runOther(self, commandText, user, keyword, conn, logConn):
		cur = conn.cursor();
		try:
			cur.execute(commandText);
			self.__logCommand(commandText, user, keyword, logConn);
		except psycopg2.Error as e:
			self.__logCommand(commandText, user, keyword, logConn);
			return e.pgerror;
		except:
			cur.close();
			self.__logCommand(commandText, user, keyword, logConn);
			self.logError(traceback.format_exc(), user, commandText, logConn);
			return "Some non-SQL error occurred.  It was logged.  Sorry!";
		
		cur.close();
		return "Success!";

	def __logCommand(self, commandText, user, keyword, logConn):
		insertText = "INSERT INTO Log (username, commandtext, time, sel, upd, del, ins, drp, crt, exc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);";
		isSel = True if keyword.lower() == "select" else False;
		isUpd = True if keyword.lower() == "update" else False;
		isDel = True if keyword.lower() == "delete" else False;
		isIns = True if keyword.lower() == "insert" else False;
		isDrp = True if keyword.lower() == "drop" else False;
		isCrt = True if keyword.lower() == "create" else False;
		isExc = True if keyword.lower() == "execute" else False;
		cur = logConn.cursor();
		
		try:
			cur.execute(insertText, (user, commandText, datetime.datetime.now(), isSel, isUpd, isDel, isIns, isDrp, isCrt, isExc));
		except:
			self.logError(traceback.format_exc(), user, commandText, logConn);
			return;
		cur.close();
	
	def logError(self, errorText, user, commandText, logConn):
		insertText = "INSERT INTO Errors (username, commandtext, exception, time) VALUES (%s, %s, %s, %s);"	
		cur = logConn.cursor();
		try:
			cur.execute(insertText, (user, commandText, errorText, datetime.datetime.now()));
		except:
			return;
		cur.close();

def make_database_interactions(config_location):
	return DatabaseInteractions(config_location);
