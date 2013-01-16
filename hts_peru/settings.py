# Scrapy settings for hts_peru project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'hts_peru'

SPIDER_MODULES = ['hts_peru.spiders']
NEWSPIDER_MODULE = 'hts_peru.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11'
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS = 1

#CONCURRENT_REQUESTS_PER_DOMAIN = 1
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'hts_peru (+http://www.yourdomain.com)'
