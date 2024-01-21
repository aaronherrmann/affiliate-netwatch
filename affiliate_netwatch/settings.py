# Scrapy settings for affiliate_netwatch project

BOT_NAME = 'affiliate_netwatch'

SPIDER_MODULES = ['affiliate_netwatch.spiders']
NEWSPIDER_MODULE = 'affiliate_netwatch.spiders'

# Crawl behavior
ROBOTSTXT_OBEY = True
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 1
COOKIES_ENABLED = False

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'affiliate_netwatch.middlewares.AffiliateNetwatchSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
     'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
     'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
#    'affiliate_netwatch.middlewares.AffiliateNetwatchDownloaderMiddleware': 543,
#    'scrapy_selenium.SeleniumMiddleware': 800
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
#    'scrapy.pipelines.images.FilesPipeline': 1
#    'affiliate_netwatch.pipelines.AffiliateNetwatchPipeline': 300,
}

# Selenium settings
SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = '/usr/local/bin/chromedriver'
SELENIUM_DRIVER_ARGUMENTS=['-headless']