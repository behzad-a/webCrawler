from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.spider import Spider
from scrapy import log
from techmicro.items import techmicroItem
import ConfigParser
import MySQLdb as mdb
import sys

class mysqlSpider(Spider):
    name = "mysql"
    
    def __init__(self, website = "website_1", read_table = "", write_table = "", *args, **kwargs):
        super(mysqlSpider, self).__init__(*args, **kwargs)
        self.website = website
        self.rTable = read_table
        self.wTable = write_table
        self.page = techmicroItem()
        self.ConfigSettings()
        if not self.keywords:
            #open("pages with keyword(s) - " + self.name, 'w').close()
            self.log('No keyword entered to search for!')
            sys.exit(0)
        self.counter = -1
        self.number = 0



    def ConfigSettings(self):
        config = ConfigParser.ConfigParser()
        config.read("./spider_settings.ini")
        if self.website not in config.sections():
            self.log('Website does not exist in spider_settings.ini')
            self.log('Program shutdown ...')
            sys.exit(0)
        self.name = config.get(self.website, 'name')
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

        try: 
            con = mdb.connect('localhost', 'Behzad', '1234', 'vulnerabilities')
            cur = con.cursor()
        except mdb.Error, e:
            print "Error %d : %s" %(e.args[0], e.args[1])
            sys.exit(1)
        cur.execute("SELECT * FROM %s" %self.rTable)
        rows = cur.fetchall()
        self.length = len(rows)
        self.start_urls = []
        for row in rows:
            self.start_urls.append(row[2])


    def parse(self, response):
        keywords_dict = {}
        flag = False
        self.sel = Selector(response)
        self.page['url'] = response.url
        self.page['tableName'] = self.wTable
        self.page['keywords'] = dict()
        for keyword in self.keywords:
            count = self.getCount(response, keyword)
            self.page['keywords'].update({keyword:count})
        self.page['title'] = self.getTitle()
        self.getBody()
        self.counter += 1
        print self.counter
        if self.counter <= self.length: 
            yield Request(self.start_urls[self.counter], callback = self.parse) 
            yield self.page
            return



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
        return count   



    def getBody(self):
        self.page['body'] = []
        for node in self.node_xpath:
           for p in self.sel.xpath(node).extract():
               self.page['body'].append(p.lower())



    def getDate(self):         
        self.page['date'] = self.sel.xpath(self.date_xpath).extract()
        date = self.page['date']
        if date:
            return date[0]
        return ''



    def getTitle(self):
        title = self.sel.xpath(self.title_xpath).extract()
        if title:
            title[0] = title[0].replace("'","")
            title[0] = title[0].replace("\"","")
            return title[0]
        return ''
