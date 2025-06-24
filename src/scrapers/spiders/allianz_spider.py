import scrapy
from bs4 import BeautifulSoup
from src.scrapers.items import InsuranceScraperItem
import re

ALLIANZ_URL = "https://www.allianz.ch/de/privatkunden/angebote/fahrzeuge-reisen/downloads.html"

PRODUCT_KEYWORDS = {
    "car": {
        "keyword": "fahrzeug",
        "url_pattern": "allianz-fahrzeug"
    },
    "travel": {
        "keyword": "reise",
        "url_pattern": "allianz-reise"
    }
}

class AllianzSpider(scrapy.Spider):
    name = "allianz"
    allowed_domains = ["allianz.ch"]
    start_urls = [ALLIANZ_URL]

    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force product to be 'car' or 'travel' only
        if product and product.lower().startswith('car'):
            self.product = 'car'
        elif product and product.lower().startswith('travel'):
            self.product = 'travel'
        else:
            self.product = 'car'  # Default
        self.product_info = PRODUCT_KEYWORDS[self.product]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", class_="c-file-download-link", href=True):
            text = a.get_text().lower()
            href = a["href"].lower()
            if ("allgemeine bedingungen" in text and 
                self.product_info["keyword"] in text and 
                self.product_info["url_pattern"] in href):
                pdf_url = response.urljoin(a["href"])
                file_name = re.sub(r"[^a-z0-9]+", "_", text)[:80] + ".pdf"
                yield InsuranceScraperItem(
                    product=self.product,
                    pdf_url=pdf_url,
                    file_name=file_name
                )
                return  # Only take the first matching PDF
        self.logger.error(f"No PDF found for {self.product} on Allianz") 