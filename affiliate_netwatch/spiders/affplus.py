import logging
import scrapy
import json
import datetime
from affiliate_netwatch.items import Network,Offer

class AffplusSpider(scrapy.Spider):
    """
    Spider to crawl AffPlus.com affiliate network aggregator site

    Crawl AffPlus' database of affiliate offers and networks to build a complete mapping of
    these entities for further analysis and research.
    """

    name = 'affplus'
    allowed_domains = ['affplus.com']

    # Spider-specific settings
    custom_settings = {
        'FEED_URI': name + '-' + datetime.date.today().strftime('%Y%m%d') + '.json',
        'FEED_FORMAT': 'jsonLines',
        'FEED_EXPORTERS': {
            'jsonLines': 'scrapy.exporters.JsonLinesItemExporter',
        },
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FILES_STORE' : name + '-images/'
    }

    # Custom headers to use with OfferVault.com
    # NOTE Order is relevant
    headers = {
        'authority': 'www.affplus.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'accept': 'application/json, text/plain, */*',
        'dnt': '1',
        'x-xsrf-token': 'eyJpdiI6Ik45dVhCSStTZjBlQWh5bzRydkdHWlE9PSIsInZhbHVlIjoiSzlNOWErYUlINUVibUpUZE5SNWV4U3ZxNU1mMDFteldRMW9rM2N3a2tyOWp6bUVOQURDSFNsVE9LanlrTjVNVCIsIm1hYyI6IjQ5NTk3ZDVhNmM2MzljZjhjYzljYjI1MzQyMWI4YTBlMDdkYjM0ODE5NGRkZjNiN2M2NTI5MjBjOWViYWNmNTIifQ==',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://www.affplus.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.affplus.com/',
        'accept-language': 'en-US,en;q=0.9',
    }

    # Start crawl operation using REST API endpoint
    def start_requests(self):
        """
        Start crawl from search  API
        """
        yield scrapy.http.Request(
            url="https://affplus.com/_search",
            method="POST",
            body='{"query":"","page":1,"networks":[],"countries":[],"verticals":[],"sort":"relevance"}',
            headers=self.headers,
            callback=self.parse_networks)

    def parse_networks(self,response):
        """
        Parse list of available affiliate networks

        Extract JSON body from /_search REST API call, search all identified networks

        Parameters
        ----------
        self : AffPlusSpider
            This spider
        response : scrapy.http.Response
            Crawl response data
        """

        results = json.loads(response.body)
        networks = results['networks']

        for network in networks:

            key = network['key']
            num_offers = network['doc_count']
            num_pages = int(num_offers / 20) + 1

            self.logger.debug(f'Found affiliate network {key} with {num_offers} offers on {num_pages} pages')

            network_item = Network()
            network_item['name'] = key

            for i in range(1, num_pages+1):

                yield scrapy.http.Request(
                    url="https://affplus.com/_search",
                    method="POST",
                    body='{"query":"","page":'+ i + ',"networks":["' + key + '"],"countries":[],"verticals":[],"sort":"relevance"}',
                    headers=self.headers,
                    callback=self.parse_offer,
                    meta=dict(network=network_item,pg=i,num_pages=num_pages,num_offers=num_offers))

                break # TODO Remove
            
            break # TODO Remove
        
        return
    
    def parse_offer(self,response):
        """
        Parse page of results from a single affiliate network

        Extract JSON body from /_search REST API call, generate offers

        Parameters
        ----------
        self : AffPlusSpider
            This spider
        response : scrapy.http.Response
            Crawl response data
        """
        metadata = response.meta
        network = metadata['network']
        page = metadata['pg']
        num_pages = metadata['num_pages']

        offers = json.loads(response.body)['hits']
        self.logger.debug(f'Found {len(offers)} offers on page {page} of {num_pages}')

        for offer in offers:

            offer_id = offer['id']
            offer_slug = offer['slug']
            thumbnail = offer['thumbnail_token']

            # Generate an offer object for each result
            offer_item = Offer()
            offer_item['id'] = offer_id
            offer_item['categories'] = offer['ocates']
            offer_item['created_at'] = offer['created_at']
            offer_item['description'] = offer['description']
            offer_item['payout'] = offer['price'] + offer['currency']
            offer_item['name'] = offer['title']
            offer_item['type'] = offer['payout_type']
            offer_item['last_updated'] = offer['updated_at']
            offer_item['countries'] = offer['ocountries']
            offer_item['landing_page_url'] = offer['preview_url']
            offer_item['file_urls'] = [f'https://apimg.net/offers/l/{thumbnail}.jpg']
            offer_item['offer_url'] = f'https://affplus.com/o/{offer_slug}'
            offer_item['network'] = network

            yield offer_item

        return