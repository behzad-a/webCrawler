from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.spider import Spider
from scrapy import log
from techmicro.items import techmicroItem
import ConfigParser
import MySQLdb as mdb
import sys
import time
import pdb

class technetSpider(Spider):
    name = "technet"
    
    def __init__(self, website = "website_1", *args, **kwargs):
        super(technetSpider, self).__init__(*args, **kwargs)
        self.website = website
        self.page = techmicroItem()
        self.ConfigSettings()
        if not self.keywords:
            #open("pages with keyword(s) - " + self.name, 'w').close()
            self.log('No keyword entered to search for!')
            sys.exit(0)
        self.totalCount = 0
        self.number = 0


    def ConfigSettings(self):
        self.start_urls = []
        config = ConfigParser.ConfigParser()
        config.read("./spider_settings.ini")
        if self.website not in config.sections():
            self.log('Website does not exist in spider_settings.ini')
            self.log('Program shutdown ...')
            sys.exit(0)
        self.name = config.get(self.website, 'name')
        self.start_urls.append(config.get(self.website, 'start_urls'))
        self.id_start = config.get(self.website, 'page_id_start')
        self.id_finish = config.get(self.website, 'page_id_finish')
        self.prefix_id = config.get(self.website, 'prefix_id')
        if self.id_start != '':
            self.id_exists = 1
            self.id_finish = int(self.id_finish)
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
        self.page['url'] = response.url
        self.page['tableName'] = self.name
        self.page['keywords'] = dict()
        for keyword in self.keywords:
            count = self.getCount(response, keyword)
            #self.page['keywords'] = dict(keyword = count)
            self.page['keywords'].update({keyword:count})
        self.page['title'] = self.getTitle()
        if self.id_exists:
            self.id_start = int(self.id_start)
            self.id_start += 1
            if self.id_start <= self.id_finish:
                self.id_start = str(self.id_start)
                yield Request(self.prefix_id+self.id_start, callback = self.parse, errback = self.http404)
        else:            
            for link in self.link_xpaths:
                for url in self.sel.xpath(link[1]).extract():
                    yield Request(link[0]+url, callback = self.parse) 
        yield self.page
        return


    def http404(self, result):
        self.id_start = int(self.id_start)
        self.id_start += 1
        if self.id_start <= self.id_finish:
            self.id_start = str(self.id_start)
            yield Request(self.prefix_id+self.id_start, callback = self.parse, errback = self.http404)


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
