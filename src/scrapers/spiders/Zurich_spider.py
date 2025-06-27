import scrapy
from bs4 import BeautifulSoup
from src.scrapers.items import InsuranceScraperItem
import re

ZURICH_URLS = {
    "car": "https://www.zurich.ch/de/privat/mobilitaet-reisen/autoversicherung",
    "travel": "https://www.zurich.ch/de/privat/mobilitaet-reisen/reisen/reiseversicherung"
}

PRODUCT_KEYWORDS = {
    "car": "motorfahrzeug",
    "travel": "reiseversicherung"
}

class ZurichSpider(scrapy.Spider):
    name = "zurich"
    allowed_domains = ["zurich.ch"]

    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force product to be 'car' or 'travel' only
        if product and product.lower().startswith('car'):
            self.product = 'car'
        elif product and product.lower().startswith('travel'):
            self.product = 'travel'
        else:
            self.product = 'car'  # Default
        self.keyword = PRODUCT_KEYWORDS[self.product].lower()
        self.start_urls = [ZURICH_URLS[self.product]]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        found = False
        # Chercher tous les liens PDF de la page
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text().lower()
            href_lower = href.lower()
            # Prendre le premier PDF qui contient 'avb' ou 'bedingungen' dans le lien ou le texte
            if ".pdf" in href_lower and ("avb" in href_lower or "bedingungen" in href_lower or "avb" in text or "bedingungen" in text):
                pdf_url = response.urljoin(href)
                # Nom de fichier propre
                file_name = re.sub(r"[^a-z0-9]+", "_", text)[:80] + ".pdf"
                yield InsuranceScraperItem(
                    product=self.product,
                    pdf_url=pdf_url,
                    file_name=file_name
                )
                found = True
                break  # Prendre le premier PDF correspondant seulement
        if not found:
            self.logger.error(f"No AVB/Bedingungen PDF found for {self.product} on Zurich Insurance Group (Zurich)") 