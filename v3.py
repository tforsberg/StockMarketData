
import zlib
#from BeautifulSoup import BeautifulSoup, Comment

from bs4 import BeautifulSoup

#from urllib import urlopen
import binascii
import datetime

import sqlite3
import time
import datetime


class StockMarketData:
    '''
    This is a base class for collecting stock market data
    '''

    smd_version = 1.03
    smd_delay = 2
#    smd_limit = 100

    smd_dbfolder = "./"
    smd_dbfile = 'investopedia.db3'
    smd_dbfilepath = (smd_dbfolder + smd_dbfile)

    smd_dbhtml = (smd_dbfolder + "backup.db3")

    backup_conn = sqlite3.connect(smd_dbhtml)
    backup_crsr = backup_conn.cursor()

    # Constants
    dbfolder = "./"
    dbfile = (dbfolder + 'investopedia.db3')

    # Create a version of the database in RAM, this could also be a filename ending with .db
    conn = sqlite3.connect(dbfile)

    # Creates the SQLite cursor that is used to query the database
    qc = conn.cursor()

    # Class Properties # formerly in Investopedia class
    guid = ""
    symbol = ''
    url = ''
    call = []
    put = []
    TradeTime = ''
    LastTrade = 0.0


    def dateTimeStringWithMilliSec(self):
        utcnow = datetime.datetime.utcnow()
        strnow = str(utcnow)[0:23]
        st1 = strnow.replace("-", "")
        st1 = st1.replace(":", "")
        st1 = st1.replace(".", "-")
        st1 = st1.replace(" ", "-")
        return st1

    def dateTimeString(self):
        dts = self.dateTimeStringWithMilliSec()
        strnow = dts[0:15]
        return strnow

    def printCompression(self, lenUncompressed, lenCompressed):
        print ("compression:", lenUncompressed, lenCompressed,)
        print (float(lenCompressed) / float(lenUncompressed) * 100.0 ), "%"

    def doCommit(self):
        self.conn.commit()


    def onProcess(self, num):
        i = 0
        while i < num:
            self.processSymbols()
            self.doCommit()
            i = i+1

            # http://stackoverflow.com/questions/64468/leaving-a-time-delay-in-python
            time.sleep(self.smd_delay / 2.0) # give other processes a chance to commit
            print('process ' + str(i) + ' of ' + str(num) + ' completed.')
            time.sleep(self.smd_delay / 2.0) # don't pound the server

    def doProcess(self, num):
        self.onProcess(num)
#        print self

    def logError(self, msg):
        q = self.conn.cursor()
        dtn = datetime.datetime.now()
        print (dtn, msg)
        statement = ("INSERT INTO Error (msg, symbol, when1, url) VALUES (?,?,?,?) ")
        q.execute(statement, (msg, self.symbol, dtn, self.url))

    def saveHtmlInDb(self, data):
        compressed = binascii.b2a_hex(zlib.compress(data))
        self.printCompression(len(data), len(compressed))
        self.backup_crsr.execute("INSERT INTO html (hex, format) VALUES (?,?)", [compressed, 'hex'])
        self.backup_conn.commit()

    def generateGUID(self):
        #TODO: Need to make a function to generate GUID's
        print ("TODO: Need to make a function to generate GUID's")

    def deactivateOldOptions(self):
        pass


