
""" modPH a library of functions used by PumpCalc

0.00    20161229    Chris Janes     original Devemopment
0.01    20160105    Chris Janes     Update

"""



#################################################
#
#   Modules to import are listed here
#
#################################################

import sqlite3
import _winreg
import calendar
import time



class modPC:
	#################################################
	#
	#	A collection of functions to be used with the self.
	#
	#################################################



	#################################################
	#
	#   Library Scoped var go here
	#
	#################################################
	dbname = ''
	user = ''
	host = ''
	password = ''
	connectstring = ''
	REG_PATH = r"SOFTWARE\ChrisJanes\PumpCalc"
	strVersion = ''
	intSeries = ''
	intCycle = ''
	MinWeight = ''
	MaxWeight = ''

	Debug = True

	#################################################
	#
	# Module functions go here
	#
	#################################################

	def __init__(self):
		""" This gets various variables from the config file

		Arguments:
		None
		Returns:
		None
		"""
	#############################################################
	#
	#   Registry Functions
	#
	#############################################################
	# todo Check why this does seemto work
	#@staticmethod
	def set_reg(self, name, value):
		try:
			_winreg.CreateKey(_winreg.HKEY_LOCAL_MACHINE, modPC.REG_PATH)
			registry_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, modPC.REG_PATH, 0,
			                               _winreg.KEY_WRITE)
			_winreg.SetValueEx(registry_key, name, 0, _winreg.REG_SZ, value)
			_winreg.CloseKey(registry_key)
			return True
		except WindowsError:
			return False

	#@staticmethod
	def get_reg(self, name):
		try:
			registry_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, modPC.REG_PATH, 0,
			                               _winreg.KEY_READ)
			value, regtype = _winreg.QueryValueEx(registry_key, name)
			_winreg.CloseKey(registry_key)
			return value
		except WindowsError:
			return None

	def get_all_reg(self):
		self.strVersion = self.get_reg('Version')
		self.intSeries = self.get_reg('Current Series')
		self.intCycle = self.get_reg('Current Cycle')
		self.MinWeight = self.get_reg('MinWeight')
		self.MaxWeight = self.get_reg('MaxWeight')
		return True


	#############################################################
	#
	#   Database Functions
	#
	#############################################################

	def getconn(self):
		""" This makes a connection to the relevent DB"""
		self.Debug = True

		try:
			connectstring = 'C:\Users\chris\PycharmProjects\PumpCalc.py\Dev\PumpCalc.db3'
			conn = sqlite3.connect(connectstring)
			if self.Debug:
				print "DEBUG connection Made"
			return conn
		except:
			raise self.ConnectFailed('connection to sqlite db failed')
			return 99

	def ConnectFailed(self, errortext):
		print errortext

	def buildTables(self):
		connection = self.getconn()

		cur = connection.cursor()

		# todo Add in try::except
		try:
			cur.execute('drop table DataPoints')
		except:
			print("drop table DataPoints Failed")
		try:
			cur.execute('drop table DataCalc')
		except:
			print("drop table DataCalc Failed")
		try:
			cur.execute('drop table Log')
		except:
			print("drop table Log Failed")
		connection.commit()
		# Create datapoints Table
		cur.execute('CREATE TABLE [DataPoints]([Series], [Cycle], [Timestamp], [Weight], PRIMARY KEY([Series] ASC, [Cycle] ASC, [Timestamp] DESC));')
		cur.execute('CREATE TABLE [DataCalc]([Series] INT, [Cycle] INT, [Timestamp] INT, [Weight] INT, [rate1] INT, [rate12] INT, [rateall] INT, [End1] INT, [End12] INT, [endall] INT, PRIMARY KEY([Series] ASC, [Cycle] ASC, [Timestamp] DESC));')
		cur.execute('CREATE TABLE [Log]([LogNumber] INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL UNIQUE, [Timestamp], [LogLine]);')
		# Save (commit) the changes
		connection.commit()
		connection.close()


	def insertdatapoint(self, Series, Cycle, Timestamp, Weight):
		#print "into insertdatapoint"
		checkvalue = self.checklatestinsert(Series, Cycle, Timestamp, Weight)
		print "checkvalue = " + str(checkvalue)
		if(checkvalue):
			#print "past checklatestinsert as True"
			connection = self.getconn()
			cur = connection.cursor()
			strsql = "INSERT INTO DataPoints (Series, Cycle, Timestamp, Weight) VALUES (" + str(Series) + ", " + str(Cycle) + ", " + str(Timestamp) + ", " + str(Weight) + ");"
			if self.Debug:
				print strsql
			#print "checkvalue  " + str(strsql)
			cur.execute(strsql)
			connection.commit()
			connection.close()
			return True
		else:
			print "past checklatestinsert as False"
			return False

	def checklatestinsert(self, Series, Cycle, Timestamp, Weight):
		if self.Debug:
			print "into ChechLatestInsert"
		connection = self.getconn()
		cur = connection.cursor()
		strsql = "select count (*) from DataPoints where Series = " + str(Series) + " and Cycle = " + str(Cycle) + " and Timestamp = " + str(Timestamp) + ";"
		if self.Debug:
			print "checklatestinsert strsql = " + str(strsql)
		cur.execute(strsql)
		array = cur.fetchall()
		cur.close()
		# todo check to see if thefollowing line can go
		#lenArray = len(array)

		if array[0][0] == 0:
			connection.close()
			if self.Debug:
				print "No Values so return True"
			return True
		else:
			if self.Debug:
				print "Datapoints found"
			cur = connection.cursor()
			strsql = "select min (Weight) from DataPoints where Series = 2 and Cycle = 3;"
			if self.Debug:
				print "strsql = " + str(strsql)
			cur.execute(strsql)
			array = cur.fetchall()
			cur.close()
			if int(Weight) >= int(array[0][0]):
				if self.Debug:
					print "Weight (" + str(Weight) + ") >= array[0][0] (" + str(array[0][0]) + ")  so return False"
				connection.close()
				return False
			# cur = connection.cursor()
			cur = connection.cursor()
			strsql = "select max (Timestamp) from DataPoints where Series = 2 and Cycle = 3;"
			if self.Debug:
				print "strsql = " + str(strsql)
			cur.execute(strsql)
			array = cur.fetchall()
			cur.close()
			if self.Debug:
				print "array[0][0]  = " + str(array[0][0])
			if (Timestamp <= array[0][0]):
				if self.Debug:
					print "Timestamp >= array[0][0]   So return False"
				connection.close()
				return False
			connection.close()
			if self.Debug:
				print "all good so return True"
			return True


	def autodatapoint(self, Weight):
		#print "into Auto data Point"
		Timestamp = self.now()
		#print str(self.intSeries) + "  " + str(self.intCycle) + "  " + str(Timestamp) + "  " + str(Weight)
		self.insertdatapoint(self.intSeries, self.intCycle, Timestamp, Weight)

	def displaycalc(self, Series, Cycle):
		if self.Debug:
			print "into displaycalc"

		connection = self.getconn()
		cur = connection.cursor()
		strsql = "select * from DataCalc where Series = " + str(Series) + " and Cycle = " + str(
			Cycle) + " order by Timestamp;"
		self.Debug = False
		if self.Debug:
			print "strsql = " + str(strsql)

		cur.execute(strsql)
		array = cur.fetchall()
		cur.close()
		lenArray = len(array)

		print "PumpCalc    Series " + str(array[0][0]) + "  Cycle " + str(array[0][1])
		print "MaxWeight = " + str(self.MaxWeight)
		print "MinWeight = " + str(self.MinWeight)
		print ""
		print "DataPoint\tWeight\tRate All\tRate 1\tEnd All\t\tEnd 1"
		for line in array:
			lenLine = len(line)
			# print str(lenLine) + ", " + str(line)
			line6mod = str(line[6]) + ".000"
			line6mod = line6mod[:5]
			line4mod = str(line[4]) + ".000"
			line4mod = line4mod[:5]
			# print "line6mod = " + line6mod
			strText = self.epoch2time(line[2]) + "\t" + str(
				line[3]) + "\t\t" + line6mod + "\t\t" + line4mod + "\t" + self.epoch2time(
				line[7]) + "\t" + self.epoch2time(line[9])
			print strText

		return None

	def displaycurrent(self):
		self.displaycalc(self.intSeries, self.intCycle)
		return None


#######################################################################
#
#   Calculation Functions
#
#######################################################################

	def checkexistsindatacalc(self, Series, Cycle, Timestamp):
		self.Debug = True
		if self.Debug == True:
			print "\n\n\n\n\ninto checkexistsindatacalc"
		connection = self.getconn()
		cur = connection.cursor()
		strsql = "select count(*) from DataCalc where Series = " + str(Series) + " and Cycle = " + str(
			Cycle) + " and Timestamp = " + str(Timestamp) + " ;"
		if self.Debug == True:
			print "checkexistsindatacalc strsql = " + str(strsql)
		cur.execute(strsql)
		array = cur.fetchall()
		cur.close()
		if (array[0][0] == 0):
			if self.Debug == True:
				print "Record Does not Exist"
			print "\n\n"
			return False
		else:
			if self.Debug == True:
				print "Record does exist"
			print "\n\n"
			return True

	def calculatecurrent(self):
		retValue = self.calculate(self.intSeries, self.intCycle)
		return retValue

	def calculate(self, Series, Cycle):
		#self.Debug = True

		if self.Debug == True :
			print "\n\n\n\ninto calculate"

#
# Drop existing DataCalc rows for this cycle
#


		connection = self.getconn()
		cur = connection.cursor()
		strsql = "DELETE from DataCalc where Series = " + str(Series) + " and Cycle = " + str(Cycle) + ";"
		if self.Debug == True :
			print "DELETE *  for cycle, strsql = " + str(strsql)
		cur.execute(strsql)
		cur.close()
#
#   Check that entries have been dropped
#
		cur = connection.cursor()
		strsql = "SELECT count (*) from DataCalc where Series = " + str(Series) + " and Cycle = " + str(Cycle) + " ;"
		if self.Debug == True :
			print "SELECT strsql = " + str(strsql)
		cur.execute(strsql)
		array = cur.fetchall()
		cur.close()
		connection.commit()
		lenArray = len(array)
		if self.Debug == True :
			print "lenArray = " + str(lenArray)
		if self.Debug == True :
			print "No of entries in DP for this cycle" + str(array[0][0])

#
# get datapoints for this Cycle
#

		cur = connection.cursor()
		strsql = "select * from DataPoints where Series = " + str(Series) + " and Cycle = " + str(
			Cycle) + " order by Weight desc;"
		if self.Debug == True :
			print "strsql = " + str(strsql)
		cur.execute(strsql)
		array = cur.fetchall()
		cur.close()
		lenArray = len(array)
		if self.Debug == True :
			print "lenArray = " + str(lenArray)
		count = 0

#
#	loop through datapoints
#

		while (int(count) < lenArray):
			if self.Debug == True :
				print "Into While "
				print "Count = " + str(count)
			line = array[count]
			str(line)
			print "Calculate DP line = " + str(line)
			weightleft = int(line[3]) - int(self.MinWeight)

			if self.Debug == True:
				print "weightleft = " + str(weightleft)

			connection = self.getconn()
			cur = connection.cursor()
			strsql = "insert into DataCalc(Series, Cycle, Timestamp, Weight) values (" + str(line[0]) + ", " + str(line[1]) + ", " + str(line[2]) + ", " + str(line[3]) + ");"
			if self.Debug == True :
				print "strsql DataCalc Insert = " + str(strsql)
			cur.execute(strsql)
			connection.commit()


			if  self.Debug == True :
				print "\nStart Calc's"
				print "count = " + str(count)
			if (count > 0):
				wtdeltaall = int(array[0][3]) - int(line[3])
				if  self.Debug == True :
					print "wtdeltaall (" + str(int(array[0][3])) + " - " + str(int(line[3])) + ") = " + str(wtdeltaall)
				tmdeltaall = int(line[2]) - int(array[0][2])
				if  self.Debug == True :
					print "tmdeltaall ( " + str(int(line[2])) + " - " + str(int(array[0][2])) + "  = " + str(tmdeltaall)
				rateall = float(wtdeltaall) / (float(tmdeltaall) / 3600)
				if  self.Debug == True :
					print "rateall (" + str(int(wtdeltaall)) + " - " + str((int(tmdeltaall) / 3600)) + ")= " + str(rateall)

				endall = int(line[2]) + (float(weightleft) / float(rateall) * float(3600))
				if  self.Debug == True :
					print "endall (" + str(line[2]) + str((float(weightleft) / float(rateall) * float(3600))) + "} = " + str(endall)

				# Rate01 Calcs
				wtdelta1 = int(array[int(count) - 1][3]) - int(line[3])
				if  self.Debug == True :
					print "wtdelta1(" + str(int(array[int(count) - 1][3])) + " - " + str(line[3]) + ") = " + str(wtdelta1)

				tmDelta1 = int(line[2]) - int(array[int(count) - 1][2])
				if  self.Debug == True :
					print "tmDelta1(" + str(line[2]) + " - " + str(array[int(count) - 1][2]) + ") = " + str(tmDelta1)
				rate1 = float(wtdelta1) / (float(tmDelta1) / 3600)
				if  self.Debug == True :
					print "rate1 = " + str(rate1)

				End1 = int(line[2]) + (float(weightleft) / float(rate1) * float(3600))
				if  self.Debug == True :
					print "End1 (" + str(line[2]) + str((float(weightleft) / float(rate1) * float(3600))) + "} = " + str(End1)

#
# Update DB
#

					strsql = "UPDATE DataCalc SET rate1 = " + str(rate1) + ", rateall = " + str(
					rateall) + ", endall = " + str(endall) + ", End1 = " + str(End1) + "  where Series = " + str(line[0]) + " and Cycle = " + str(line[1]) + " and Timestamp = " + str(line[2]) + " ;"
					if  self.Debug == True :
						print "strsql DataCalc Update = " + str(strsql)
					cur.execute(strsql)
					connection.commit()

			# end of while loop (almost)
			count = count + 1
			

	#############################################################
	#
	#   time Functions
	#
	#############################################################

	def now(self):
		epoch = calendar.timegm(time.gmtime())
		return epoch


	def time2epoch(self, year, month, day, hour, minute):
		# "Day.Month.year hours:Minutes
		date_time = str(day) + '.' + str(month) + '.' + str(year) + ' ' + str(hour) + ':' + str(minute) + ':00'
		if  self.Debug == True :
			print 'date_time  ' + str(date_time)
		pattern = '%d.%m.%Y %H:%M:%S'
		epoch = int(time.mktime(time.strptime(date_time, pattern)))
		return epoch

	def epoch2time(self,epoch):
		strtime = time.strftime('%a %H:%M', time.localtime(epoch))
		return strtime



