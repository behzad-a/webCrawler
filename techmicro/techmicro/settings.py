# Scrapy settings for techmicro project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'techmicro'

SPIDER_MODULES = ['techmicro.spiders']
NEWSPIDER_MODULE = 'techmicro.spiders'

ITEM_PIPELINES = {'techmicro.pipelines.pagePipeline':200}
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'techmicro (+http://www.yourdomain.com)'
