# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb as mdb
from techmicro.items import techmicroItem
from scrapy.exceptions import DropItem
from scrapy import log
import time
import pdb

class pagePipeline(object):
    def __init__(self):
        self.tables = False
        self.MySQL_connect()

    def process_item(self, item, spider):
        #log.msg("heloooooooooooooooo", level = log.DEBUG)
        #return item
        if not self.tables:
            self.create_table1(item)
            self.tables = True
        for i in item.items():
            if i[1] > 0:   
                self.fill_table1(item)
                return item
        raise DropItem("No keyword was found in %s" %item['url'])

    def fill_table1(self, item):
        count_fields = ""
        count_values = ""
        for p in item['keywords'].items():
            count_fields += ", %s" %p[0]
            count_values += ", \"%d\"" %p[1]
        self.cur.execute("INSERT INTO %s(Title, URL %s) VALUES (\"%s\", \"%s\" %s)" %(item['tableName'], count_fields, item['title'], item['url'], count_values)) 
        self.con.commit()

    def create_table1(self, item):
        log.msg("MySQL tables will now be overwritten with the new tables.", level = log.DEBUG)
        self.cur.execute("DROP TABLE IF EXISTS %s" %item['tableName'])
        wordFields = ""
        for keyword in item['keywords'].keys():
            wordFields += ", %s SMALLINT" %keyword
        self.cur.execute("CREATE TABLE %s(ID INT PRIMARY KEY AUTO_INCREMENT, Title VARCHAR(100), URL VARCHAR(100) %s)" %(item['tableName'], wordFields))
        log.msg("Table \'%s\' has been added to the MySQL database with the corresponding columns" %item['tableName'], level = log.INFO)
        self.con.commit()

    def MySQL_connect(self):
        try:
            log.msg("Connecting to MySQL database ...", level = log.INFO)
            self.con = mdb.connect('localhost', 'Behzad', '1234', 'vulnerabilities')
            self.cur = self.con.cursor()
            log.msg("Connection to MySQL has been established!", level = log.INFO)
        except mdb.Error, e:
            print "Error %d : %s" %(e.args[0], e.args[1])
            sys.exit(1)


    def MySQL_exit(self):
        if self.con:
            self.con.close()
            log.msg("Successfully closed connection to MySQL database!", level = log.INFO)

    def __del__(self):
        self.MySQL_exit()
