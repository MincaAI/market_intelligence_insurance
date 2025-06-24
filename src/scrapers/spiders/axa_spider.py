import scrapy
from bs4 import BeautifulSoup
from src.scrapers.items import InsuranceScraperItem
import re

AXA_URLS = {
    'Car Insurance': 'https://www.axa.ch/de/privatkunden/angebote/fahrzeug-reisen/autoversicherung.html',
    'Travel Insurance': 'https://www.axa.ch/de/privatkunden/angebote/fahrzeug-reisen/reiseversicherung.html',
}

def clean_filename(text):
    # Nettoie le texte pour en faire un nom de fichier valide
    text = text.strip().lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text[:80]  # Limite la longueur

class AXASpider(scrapy.Spider):
    name = 'axa'
    allowed_domains = ['axa.ch']

    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product or 'Car Insurance'
        self.start_urls = [AXA_URLS[self.product]]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a', class_='m-download-box__link', href=True):
            text = a.get_text().lower()
            if 'avb' in text or 'vertragsbedingungen' in text:
                pdf_url = response.urljoin(a['href'])
                file_name = clean_filename(a.get_text()) + '.pdf'
                yield InsuranceScraperItem(
                    product=self.product,
                    pdf_url=pdf_url,
                    file_name=file_name
                )
                return  # Prendre le premier PDF seulement
        self.logger.error(f'No AVB PDF found for {self.product}') 