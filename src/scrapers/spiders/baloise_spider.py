import scrapy
from bs4 import BeautifulSoup
from src.scrapers.items import InsuranceScraperItem
import re

BALOISE_URLS = {
    "Car Insurance": "https://www.baloise.ch/de/privatkunden/versichern/fahrzeuge/autoversicherung.html",
    # "Travel Insurance": "URL_A_COMPLETER"
}

class BaloiseSpider(scrapy.Spider):
    name = "baloise"
    allowed_domains = ["baloise.ch"]

    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product or "Car Insurance"
        self.start_urls = [BALOISE_URLS[self.product]]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        # Cherche le premier bal-list-item qui contient un PDF de conditions générales
        for item in soup.find_all("bal-list-item", href=True):
            href = item["href"]
            text = item.get_text().lower()
            if href.endswith(".pdf") and ("vertragsbedingungen" in href or "bedingungen" in text):
                pdf_url = response.urljoin(href)
                file_name = re.sub(r"[^a-z0-9]+", "_", text)[:80] + ".pdf"
                yield InsuranceScraperItem(
                    product=self.product,
                    pdf_url=pdf_url,
                    file_name=file_name
                )
                return  # Prend le premier PDF seulement
        self.logger.error(f"No PDF found for {self.product} on Baloise") 