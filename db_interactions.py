import traceback
import datetime
import sys
import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

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
	crt boolean NOT NULL default '0',
	exc boolean NOT NULL default '0',
	alt boolean NOT NULL default '0'
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
	def __init__(self, logPool, commandPool):
		self.logPool = logPool;
		self.commandPool = commandPool;

	def runCommand(self, commandText, user):
		try:
			commandConn = self.commandPool.getconn();
			commandConn.autocommit = True;
		except:
			print(traceback.format_exc());
			return "Unable to connect to database!";

		try:
			logConn = self.logPool.getconn();
			logConn.autocommit = True;
		except:
			commandPool.putconn(commandConn);
			return "Unable to connect to logging db.  Sorry, no SQL!  (I suck, I know)";
		
		keyword = self.__getSqlKeyword(commandText);
		result = "";
		cur = commandConn.cursor();

		try:
			cur.execute(commandText);
			self.__logCommand(commandText, user, keyword, logConn);
			
			if cur.description is not None:
				result = self.__formatRows(cur);
			else:
				result = self.__formatNonRows(cur);

		except psycopg2.Error as e:
			result = e.pgerror;
		except:
			self.logError(traceback.format_exc(), user, text, logConn);
			result = "Some non-SQL error occured.  It was logged.  Sorry!";
		
		cur.close();
		self.commandPool.putconn(commandConn);
		self.logPool.putconn(logConn);
		return result;
	
	def __getSqlKeyword(self, commandText):
		split = commandText.split(' ');
		return split[0];

	def __formatRows(self, cur):
		if cur.rowcount == 0:
			results = "No results returned";
		else:
			results = "";
			for record in cur:
				results += self.__formatResult(record);
				if len(results) >= 140:
					break;
		
		return results;
	
	def __formatResult(self, row):
		result="";
	
		for value in row:
			result = result + str(value) + ",";
		
		#remove trailing comma
		result = result[:-1];
		result = result + ";";
		return result;

	def __formatNonRows(self, cur):
		return cur.statusmessage;

	def __logCommand(self, commandText, user, keyword, logConn):
		insertText = "INSERT INTO Log (username, commandtext, time, sel, upd, del, ins, drp, crt, exc, alt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);";
		isSel = True if keyword.lower() == "select" else False;
		isUpd = True if keyword.lower() == "update" else False;
		isDel = True if keyword.lower() == "delete" else False;
		isIns = True if keyword.lower() == "insert" else False;
		isDrp = True if keyword.lower() == "drop" else False;
		isCrt = True if keyword.lower() == "create" else False;
		isExc = True if keyword.lower() == "execute" else False;
		isAlt = True if keyword.lower() == "alter" else False;
		cur = logConn.cursor();
		
		try:
			cur.execute(insertText, (user, commandText, datetime.datetime.now(), isSel, isUpd, isDel, isIns, isDrp, isCrt, isExc, isAlt));
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
			sys.stdout.write(traceback.format_exc() + '\n');
			return;
		cur.close();

def make_database_interactions(log_pool, command_pool):
	return DatabaseInteractions(log_pool, command_pool);

def get_log_pool(config):
	minConn = int(config['settings']['MinPoolConnections']);
	maxConn = int(config['settings']['MaxPoolConnections']);
	connStr = config['db']['LogConnectionString'];
	return psycopg2.pool.ThreadedConnectionPool(minConn, maxConn, connStr);

def get_command_pool(config):
	minConn = int(config['settings']['MinPoolConnections']);
	maxConn = int(config['settings']['MaxPoolConnections']);
	connStr = config['db']['PlaygroundConnectionString'];
	return psycopg2.pool.ThreadedConnectionPool(minConn, maxConn, connStr);
