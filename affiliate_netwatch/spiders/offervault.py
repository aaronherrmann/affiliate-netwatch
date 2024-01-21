import logging
import scrapy
import json
import datetime
from affiliate_netwatch.items import Network,Offer

class OffervaultSpider(scrapy.Spider):
    """
    Spider to crawl OfferVault.com affiliate network aggregator site
    
    Crawl OfferVault's database of affiliate offers and networks to build a complete mapping of
    these entities for further analysis and research.
    """

    name = 'offervault'
    allowed_domains = ["offervault.com"]

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
        'authority': 'offervault.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        #'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'accept': 'application/json, text/plain, */*',
        'dnt': '1',
        'site-identifier': 'offervault',
        'sec-ch-ua-mobile': '?0',
        #'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://offervault.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://offervault.com/?selectedTab=topOffers&search=&page=1',
        'accept-language': 'en-US,en;q=0.9',
    }

    # Start crawl operation using REST API /networks endpoint
    def start_requests(self):
        """"Start crawl from network list API"""
        yield scrapy.http.Request(
            url="https://offervault.com/api/networks?site=offervault",
            method="GET",
            headers=self.headers,
            callback=self.parse_networks
        )

    # Parse each affiliate network found
    # TODO Better error handling
    def parse_networks(self,response):
        """
        Parse all affiliate networks found
        
        Extract JSON body from /networks REST API call, then post-process the results and crawl
        each affiliate network found to find all of its associated offers.

        Parameters
        ----------
        self : OffervaultSpider
            This spider
        response : scrapy.http.Response
            Crawl response data
        
        """

        networks = json.loads(response.body)['networks']
        self.logger.debug(f'Found {len(networks)} affiliate networks')

        for network in networks:

            network_id = network['id']
            num_offers = network['offerCount']
            num_pages = int(num_offers / 20) + 1
            self.logger.debug(f'Found affiliate network {network_id} with {num_offers} offers on {num_pages} pages')

            # Assemble network item but yield it only after *ALL* offers have been added
            network_item = Network()
            network_item['id'] = network_id
            network_item['name'] = network['name']
            network_item['commission_type'] = network['commissionTypes']
            network_item['description'] = network['description']
            network_item['email'] = network['emailString']
            network_item['url'] = network['url']
            network_item['min_payout'] = network['minimumPayment']
            network_item['payment_method'] = network['paymentMethods']
            network_item['phone'] = network['phoneNumbersString']
            network_item['payment_frequency'] = network['paymentFrequencies']

            # Crawl each page of offers for this network via POST request
            for i in range(1, num_pages+1):

                yield scrapy.http.Request(
                    url="https://offervault.com/api/offers/search",
                    method="POST",
                    body='{"query":"","page":'+str(i)+',"sortBy":"","sortDesc":false,"networks":['+str(network_id)+'],"countries":[],"categories":[],"ppc":false,"mobile":false}',
                    headers=self.headers,
                    callback=self.parse_offer,
                    meta=dict(network=network_item,pg=i,num_pages=num_pages,num_offers=num_offers))

        return

    # Parse each offer found in a page of offers for a network
    # TODO Better error handling
    def parse_offer(self,response):
        """
        Parse affiliate offer under a selected network

        Extract JSON body from /offers/search REST API call, generate Offer object

        Parameters
        ----------
        self : OffervaultSpider
            This spider
        response : scrapy.http.Response
            Crawl response data
        
        """

        metadata = response.meta
        network = metadata['network']
        page = metadata['pg']
        num_pages = metadata['num_pages']

        offers = json.loads(response.body)['offers']
        self.logger.debug(f'Found {len(offers)} offers on page {page} of {num_pages}')

        for offer in offers:

            offer_id = offer['id']
            offer_slug = offer['slug']

            # Generate an offer object for each result
            offer_item = Offer()
            offer_item['id'] = offer_id
            offer_item['categories'] = offer['categories']
            offer_item['created_at'] = offer['created_at']
            offer_item['description'] = offer['description']
            offer_item['payout'] = offer['usdAmount']
            offer_item['name'] = offer['title']
            offer_item['type'] = offer['payoutType']
            offer_item['last_updated'] = offer['updated_at']
            offer_item['countries'] = offer['countries']
            offer_item['landing_page_url'] = offer['previewUrl']
            offer_item['file_urls'] = [f'https://d2m96w2vdeemru.cloudfront.net/{offer_id}/large.jpeg']
            offer_item['offer_url'] = f'https://offervault.com/offer/{offer_id}/{offer_slug}'
            offer_item['network'] = network

            yield offer_item

        return