import scrapy
import ast
import requests
from bs4 import BeautifulSoup

class mtgSpider(scrapy.Spider):
    name = "mtg"
    start_urls = [
        "https://www.cardmarket.com/en/Magic/Products/Singles/2005-Player-Cards?mode=list&idRarity=0&sortBy=price_asc&perSite=20",
    ]
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }
    
    
    def __init__(self):
        self.i=178

    def parse(self, response):
        table = response.css('div.table.table-striped.mb-3')
        table = table.css('div.table-body')
        for div in table.css('div.row.no-gutters'):
            nameDiv = div.css('div.col').css('div.row.no-gutters').css('div.col-10.col-md-8.px-2.flex-column.align-items-start.justify-content-center')
            expansionDiv = div.css('div.col-icon.small')
            rarityDiv = div.css('div.col').css('div.row.no-gutters').css('div.col-sm-2.d-none.d-sm-flex.has-content-centered').css('span.d-none.d-md-flex')
            availiabilityDiv = div.css('div.col-availability.px-2')
            yield {
                'name': nameDiv.css('a::text').get(),
                'expansion': expansionDiv.css('a.expansion-symbol.is-magic.icon.is-24x24::attr(title)').get(),
                'rarity': rarityDiv.css('span.icon::attr(title)').get(),
                'availiability': availiabilityDiv.css('span.d-none.d-md-inline::text').get(),
                'price': div.css('div.col-price.pr-sm-2::text').get(),
                'availiabilityFoil': div.css('div.col-availability.d-none.d-lg-flex::text').get(),
                'priceFoil': div.css('div.col-price.d-none.d-lg-flex.pr-lg-2::text').get()
            }
            
        next_page = response.css('a.btn.btn-primary.btn-sm.ml-3.pagination-control::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
        else:
            next_page = 'https://www.cardmarket.com/en/Magic/Products/Singles' + '/' + self.getExpansions()[self.i] + '?mode=list&idRarity=0&sortBy=price_asc&perSite=20'
            self.i=self.i+1
            yield response.follow(next_page, self.parse)


    def getExpansions(self):
        URL = "https://www.cardmarket.com/en/Magic/Products/Singles"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        options = soup.find("select", {"name":"idExpansion"})
        opts = []
        for option in options.find_all('option'):
            opts.append(option.get_text())

        for i in range(len(opts)):
            opts[i] = opts[i].replace("&", "")
            opts[i] = opts[i].replace("\'", "")
            opts[i] = opts[i].replace(" ", "-")
            opts[i] = opts[i].replace(":","")
            opts[i] = opts[i].replace(".","")
        return opts