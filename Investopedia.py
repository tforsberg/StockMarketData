#from StockMarketData import StockMarketData

import v3

import zlib
#from BeautifulSoup import BeautifulSoup, Comment
#from urllib import urlopen
import binascii
import datetime

from v3 import StockMarketData

class Investopedia(StockMarketData):
    '''
    This is a class for collecting stock market data from investopepia.com
    '''
    version = 0

    def saveRow(self, row):
        debug = 1
        q = self.conn.cursor()
        statement = ("""
            INSERT INTO OptionDetail (OptionHeader_ID, StockPrice, OptionSymbol, StrikePrice, TradeTime, Last, Change,
                                      Bid, BidNum, Ask, AskNum, Volume, OpenInterest, Type, AppVersion, Created_DTS )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """)

        # Save Call Option Info
        dtn = datetime.datetime.now()
        self.call = [self.guid, self.LastTrade, row[0],  row[9], self.TradeTime, row[1],  row[2], row[3],
                     row[4],  row[5],  row[6],  row[7],  row[8],  "C", self.smd_version, dtn]
        q.execute(statement, self.call)

        # Save Call Option Info
        self.put  = [self.guid, self.LastTrade, row[10], row[9], self.TradeTime, row[11], row[12], row[13],
                     row[14], row[15], row[16], row[17], row[18], "P", self.smd_version, dtn]
        q.execute(statement, self.put)

        if debug: print(row)


    def updateHeaderRow(self):
        # Update the OptionHeader row to show that it has been retrieved
        qc2 = self.conn.cursor()
        dtn = datetime.datetime.now()
        if self.call:
            statement = ("""UPDATE OptionHeader SET LastRetrieved = ?,
                              CallOptionSymbol = ?, PutOptionSymbol = ?
                            WHERE id = ? """)
            qc2.execute(statement, [str(dtn),  self.call[0],  self.put[0], self.guid])
        else:
            statement = ("UPDATE OptionHeader SET LastRetrieved = ? WHERE id = ? ")
            print ("no options: ")
            self.logError("No Option Data")
            qc2.execute(statement, [str(dtn), self.guid])
        print ("Header Row Saved: ", self.guid)

    def logMessage(self, msg, url):
        print ("TODO:", msg, url)

    def updateOptionChainLink(self, url):
        print ("TODO: " + url)
        qc3 = self.conn.cursor()
        gotone = 0

        statement = ("SELECT id FROM OptionHeader WHERE url = ? ")
        print (url)
        qc3.execute(statement, [url])

#        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

        for i in qc3:
            print ("updateOptionChainLink: pass", i)
            gotone = 1

        if (gotone == 0) :
            statement = ("INSERT INTO OptionHeader (url) VALUES (?) ")
#            qc3.execute(statement, [url])
            self.logMessage("New Option Link Found but not added!", url)

#        print "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"

    def getPageTitle(self):
        pass

    def getOptionChainDates(self, html):

        mysoup = BeautifulSoup(html)
#        print "getOptionChainDates: ", mysoup
        trs = mysoup.findAll('tr')
        row = []

#        print "============="
        for tr in trs:

            for td in tr.findAll('td'):
                for a in td.findAll('a'):
                    self.updateOptionChainLink(a['href'])

                text = td.findAll(text=True)
                text = ''.join(text).strip().encode('utf8')
#                print td
                row.append(text)

#        print "============="
#['Last Trade:', '5.39', 'Trade Time:', '2/17/2012 4:30 PM EST', 'Change:', '-0.04\r\n                  ( -0.74 %)', 'Prev Close:', '5.43', "Day's High:", '5.47', "Day's Low:", '5.35']
        print (row)


    def getLastTradeTime(self, html):
        mysoup = BeautifulSoup(html)
#        print "getMoreInfo: ", mysoup

        trs = mysoup.findAll('tr')
        row = []

#        print "============="
        for tr in trs:

            for td in tr.findAll('td'):
                text = td.findAll(text=True)
                text = ''.join(text).strip().encode('utf8')
#                print text
                row.append(text)

#        print "============="
#['Last Trade:', '5.39', 'Trade Time:', '2/17/2012 4:30 PM EST', 'Change:', '-0.04\r\n                  ( -0.74 %)', 'Prev Close:', '5.43', "Day's High:", '5.47', "Day's Low:", '5.35']
        print (row)

#        datetime.datetime.strptime("21/12/2008", "%d/%m/%Y").strftime("%Y-%m-%d")
        if row:
            self.LastTrade = row[1]
            self.TradeTime = datetime.datetime.strptime(row[3], "%m/%d/%Y %I:%M %p EST").strftime("%Y-%m-%d %H:%M:%S.000")
        else:
            print ("No data found for: ", self.symbol)
            self.logError("No data found.")


    def doSomeTesting(self, soup):

        #  <div id = "divOptionChainDates">
        test = soup.find("div", { "id" : "divOptionChainDates" })
        self.getOptionChainDates(str(test))

        info = soup.find("span", { "id" : "ctl00_ctl00_ctl00_MainContent_A2_A3_ctl00_contentService1" })
        self.getLastTradeTime(str(info))

        title = soup.find("title")
        print ("TODO:",  title)

        table = soup.tbody                         # The first table

        our_table = []
        if table:
            trs = table.findAll('tr')

            for tr in trs:
                our_row = []
                for td in tr.findAll('td'):
                    text = td.findAll(text=True)
                    text = ''.join(text).strip().encode('utf8')
    #                print text
                    our_row.append(text)
                our_table.append(our_row)
                self.saveRow(our_row)

        else:
            self.logError('doSomeTesting: No Table Data')



    def processPage(self, symbol, url):
        dts = Investopedia.dateTimeString(self)
#        print url
        webpage = urlopen('http://www.investopedia.com/' + url).read()
        soup = BeautifulSoup(webpage)

        # Remove Script Tags
        [s.extract() for s in soup('script')]
        [s.extract() for s in soup('noscript')]

        # Remove Comment Tags
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]

#        print soup

        self.doSomeTesting(soup)
        self.updateHeaderRow()

        data = soup.prettify()

#        print symbol, dts

        htmlfile = ("quotes\\" + symbol + "-" + dts + '.html')
        print (htmlfile)

        f = open(self.dbfolder + htmlfile, 'w')
        f.write(data)
        f.close()

        self.saveHtmlInDb(data)

    def processSymbols(self):
        qc = self.conn.cursor()

        print ('======================')
        self.backup_crsr.execute("SELECT Count(*) FROM html")
        for i in self.backup_crsr:
            print ('HTML backup records: ' + str(i[0]))

        statement = """SELECT ID, StockSymbol, url FROM OptionHeader
                       WHERE (Year = 2012 and Month >= 3) or (Year > 2012)
                       ORDER BY LastRetrieved
                       LIMIT 1"""
        qc.execute(statement)

        for i in qc:
            self.guid = i[0]
            self.symbol = i[1]
            self.url = i[2]
            print ('----------------------')
            print (self.symbol, self.url, self.guid)
            self.processPage(self.symbol, self.url)

    def compressUnprocessed(self):
        qc = self.conn.cursor()
        qc2 = self.conn.cursor()

        qc.execute("SELECT * FROM Unprocessed WHERE data is not null LIMIT 1" )

        for i in qc:
            data = i[1]
            compressed = binascii.b2a_hex(zlib.compress(data))
            print ('Compressed   :', len(compressed), compressed)
            qc2.execute("UPDATE unprocessed SET compressed=? WHERE data=?", [compressed, data])

        self.conn.commit()

    def testReadingCompressed(self):
        qc = self.conn.cursor()
#        qc2 = conn.cursor()

        qc.execute("SELECT hex FROM Unprocessed where format = 'hex' LIMIT 1 OFFSET 10" )

        for i in qc:
#            print i
            compressed = i[0]
#            s1 = s1.replace('\r\n', '\n')
            decompressed = zlib.decompress(binascii.a2b_hex(compressed))
#            decompressed = bz2.decompress(compressed)
            print ('Decompressed :', decompressed)
            print (compressed)
            print (self.printCompression(len(decompressed), len(compressed)))
#            qc2.execute("UPDATE unprocessed SET data=null, compressed=? WHERE data=?", [compressed, data])

