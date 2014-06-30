from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.spider import Spider
from scrapy import log
from techmicro.items import techmicroItem
import ConfigParser
import MySQLdb as mdb
import sys

class technetSpider(Spider):
    name = "technet"
    
    def __init__(self, website = "website_1", *args, **kwargs):
        super(technetSpider, self).__init__(*args, **kwargs)
        self.website = website
        self.search = techmicroItem()
        self.ConfigSettings()
        self.MySQL_connect()
        if self.keywords:
            open("pages with keyword(s) - " + self.name, 'w').close()
        else:
            self.log('No keyword entered to search for!')
            sys.exit(0)
        self.totalCount = 0
        self.number = 0


    def MySQL_connect(self):
        try:
            self.con = mdb.connect('localhost', 'Behzad', '1234', 'vulnerabilities')
            self.cur = self.con.cursor()
            self.cur.execute("DROP TABLE IF EXISTS %s" %self.name)
            wordFields = ""
            for keyword in self.keywords:
                wordFields += ", %s SMALLINT" %keyword
            print wordFields
            self.cur.execute("CREATE TABLE %s(ID INT PRIMARY KEY AUTO_INCREMENT, Title VARCHAR(100), URL VARCHAR(100) %s)" %(self.name, wordFields))
            #self.cur.execute("CREATE TABLE %s(ID INT PRIMARY KEY AUTO_INCREMENT, Title VARCHAR(100), URL VARCHAR(100), vulnerability SMALLINT)" %(self.name))
            self.cur.execute("SELECT VERSION()")
            ver = self.cur.fetchone()
            print "Database Version : %s" %ver
        except mdb.Error, e:
            print "Error %d : %s" %(e.args[0], e.args[1])
            sys.exit(1)


    def MySQL_exit(self):
        if self.con:
            self.con.close()


    def ConfigSettings(self):
        self.start_urls = []
        config = ConfigParser.ConfigParser()
        config.read("/home/behzad/scrapyproject/techmicro/spider_settings.ini")
        if self.website not in config.sections():
            self.log('Website does not exist in spider_settings.ini')
            self.log('Program shutdown ...')
            sys.exit(0)
        self.name = config.get(self.website, 'name')
        self.start_urls.append(config.get(self.website, 'start_urls'))
        self.id_start = config.get(self.website, 'page_id_start')
        self.id_finish = config.get(self.website, 'page_id_finish')
        self.id_finish = int(self.id_finish)
        self.prefix_id = config.get(self.website, 'prefix_id')
        if self.id_start:
            self.id_exists = 1
        else:
            self.id_exists = 0
        links = [x for x in config.options(self.website) if x.startswith('link_')]
        self.link_xpaths = []
        for link in links:
            prefix = "prefix_" + link
            if prefix in config.options(self.website):
                prefix = config.get(self.website, prefix)
            else:
                prefix = ""
            self.link_xpaths.append([prefix, config.get(self.website, link)]) 
        keywords = [x for x in config.options(self.website) if x.startswith('keyword_')]
        self.keywords = []
        for keyword in keywords:
            s = config.get(self.website, keyword)
            self.keywords.append(s.lower())
        self.title_xpath = config.get(self.website, 'title')
        self.date_xpath = config.get(self.website, 'date')
        nodes = [x for x in config.options(self.website) if x.startswith('node_')]
        self.node_xpath = []
        for node in nodes:
            self.node_xpath.append(config.get(self.website, node)) 
       

    def parse(self, response):
        keywords_dict = {}
        flag = False
        self.sel = Selector(response)
        for keyword in self.keywords:
            count = self.getCount(response, keyword)
            keywords_dict[keyword] = count
            if count:
                self.number += 1
                flag = True
        if flag:
            #self.write_to_file(response, keywords_dict)
            count_fields = ""
            count_values = ""
            for p in keywords_dict.items():
                count_fields += ", %s" %p[0]
                count_values += ", \"%d\"" %p[1]
            self.cur.execute("INSERT INTO %s(Title, URL %s) VALUES (\"%s\", \"%s\" %s)" %(self.name, count_fields, self.getTitle(), response.url, count_values))            
            self.con.commit()
        if not self.id_exists:
            self.parseID(response)
        else:
            self.parseLINK(response)
        self.id_start = int(self.id_start)
        self.id_start += 1
        if self.id_start <= self.id_finish:
            self.id_start = str(self.id_start)
            #print self.prefix_id+self.id_start
            yield Request(self.prefix_id+self.id_start, callback = self.parse)


    def parseID(self, response):
        self.id_start = int(self.id_start)
        self.id_start += 1
        if self.id_start <= self.id_finish:
            self.id_start = str(self.id_start)
            print self.prefix_id+self.id_start
            #yield Request(self.prefix_id+self.id_start, callback = self.parse)
            

    def parseLINK(self, response):
        for link in self.link_xpaths:
            for url in self.sel.xpath(link[1]).extract():
                yield Request(link[0]+url, callback = self.parse) 


    def write_to_file(self, response, keywords_dict):
        with open("pages with keyword(s) - " + self.name, 'a') as f:
            f.write("%d)%s\n" %(self.number, self.getTitle()) + response.url + "\n")
            for p in keywords_dict.items():                
                f.write("%s : %s \n" %p)
            f.write("\n")
    

    def getCount(self, response, keyword):
        count = 0
        for node in self.node_xpath:
            for p in self.sel.xpath(node).extract():
                lowerp = p.lower()
                count += lowerp.count(keyword)
        self.totalCount += count 
        return count   


    def getDate(self): 
        self.search['date'] = self.sel.xpath(self.date_xpath).extract()
        date = self.search['date']
        if date:
            return date[0]
        return ''


    def getTitle(self):
        self.search['title'] = self.sel.xpath(self.title_xpath).extract()
        title = self.search['title']
        if title:
            return title[0]
        return ''

    def __del__(self):
        self.MySQL_exit()
