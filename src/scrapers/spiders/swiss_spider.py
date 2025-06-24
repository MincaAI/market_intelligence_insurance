import scrapy
from bs4 import BeautifulSoup
from src.scrapers.items import InsuranceScraperItem
import re

SWISS_URLS = {
    "Car Insurance": "https://www.zurich.ch/de/privat/mobilitaet-reisen/autoversicherung",
    "Travel Insurance": "https://www.zurich.ch/de/privat/mobilitaet-reisen/reisen/reiseversicherung"
}

PRODUCT_KEYWORDS = {
    "Car Insurance": "motorfahrzeug",
    "Travel Insurance": "reiseversicherung"
}

class SwissSpider(scrapy.Spider):
    name = "swiss"
    allowed_domains = ["zurich.ch"]

    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product or "Car Insurance"
        self.keyword = PRODUCT_KEYWORDS[self.product].lower()
        self.start_urls = [SWISS_URLS[self.product]]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        found = False
        # Chercher tous les liens PDF de la page
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text().lower()
            href_lower = href.lower()
            # Prendre le premier PDF trouvé, sans filtrage par mot-clé
            if ".pdf" in href_lower:
                pdf_url = response.urljoin(href)
                # Nom de fichier propre
                file_name = re.sub(r"[^a-z0-9]+", "_", text)[:80] + ".pdf"
                yield InsuranceScraperItem(
                    product=self.product,
                    pdf_url=pdf_url,
                    file_name=file_name
                )
                found = True
                break  # Prendre le premier PDF seulement
        if not found:
            self.logger.error(f"No PDF found for {self.product} on Swiss Insurance Group (Zurich)") 