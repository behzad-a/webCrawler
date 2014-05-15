from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.spider import Spider
from scrapy import log
from techmicro.items import techmicroItem
import ConfigParser

class technetSpider(Spider):
    name = "technet"
    
    def __init__(self, keyword = None, *args, **kwargs):
        super(technetSpider, self).__init__(*args, **kwargs)
        self.search = techmicroItem()
        self.ConfigSettings()
        if self.keywords:
            open("pages with keyword(s)", 'w').close()
        else:
            self.log('No keyword entered to search for!')
        self.totalCount = 0
        self.number = 0


    def ConfigSettings(self):
        self.start_urls = []
        config = ConfigParser.ConfigParser()
        config.read("/home/behzad/scrapyproject/techmicro/spider_settings.ini")
        self.start_urls.append(config.get('website_1', 'start_urls'))
        self.link_xpaths = config.get('website_1', 'link_01')     
        keywords = [x for x in config.options('website_1') if x.startswith('keyword_')]
        self.keywords = []
        for keyword in keywords:
            s = config.get('website_1', keyword)
            self.keywords.append(s.lower())
        self.title_xpath = config.get('website_1', 'title')
        self.date_xpath = config.get('website_1', 'date')
        nodes = [x for x in config.options('website_1') if x.startswith('node_')]
        self.node_xpath = []
        for node in nodes:
            self.node_xpath.append(config.get('website_1', node)) 
       

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
            self.write_to_file(response, keywords_dict)
        for url in self.sel.xpath(self.link_xpaths).extract():
            yield Request(url, callback = self.parse) 


    def write_to_file(self, response, keywords_dict):
        with open("pages with keyword(s)", 'a') as f:
            f.write("%d)%s\n" %(self.number, self.getTitle()) + response.url + "\n")
            for p in keywords_dict.items():                
                f.write("%s : %s \n" %p)
            f.write("\n")
    

    def getCount(self, response, keyword):
        count = 0
        if not response.url.count("technet.microsoft.com/en-us/library/security/ms"):
            return count
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
