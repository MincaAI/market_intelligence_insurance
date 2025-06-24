import scrapy
from bs4 import BeautifulSoup
from src.scrapers.items import InsuranceScraperItem
import re
import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

PRODUCT_URLS = {
    'Car Insurance': 'https://www.generali.ch/de/privatpersonen/fahrzeuge-reisen/autoversicherung',
    'Travel Insurance': 'https://www.generali.ch/de/privatpersonen/fahrzeuge-reisen/reiseversicherung',
}

class GeneraliSpider(scrapy.Spider):
    name = 'generali'
    allowed_domains = ['generali.ch']

    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product or 'Car Insurance'
        self.start_urls = [PRODUCT_URLS[self.product]]
        self.documents_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'documents')

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        # Chercher les <tr> avec la classe et l'attribut onclick
        for tr in soup.find_all('tr', class_='article--download__files--row'):
            onclick = tr.get('onclick', '')
            match = re.search(r"downloadFile\('([^']+)'", onclick)
            if match:
                pdf_path = match.group(1)
                pdf_url = response.urljoin(pdf_path)
                file_name = pdf_url.split('/')[-1].split('?')[0]
                # Télécharger le PDF si besoin (pipeline peut le faire aussi)
                yield InsuranceScraperItem(
                    product=self.product,
                    pdf_url=pdf_url,
                    file_name=file_name
                )
                return  # Prendre le premier PDF seulement
        self.logger.error(f'No PDF with onclick found for {self.product}')

        # Use Selenium to find the PDF link
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(response.url)

        # Wait for the page to load (adjust if necessary)
        time.sleep(5)

        try:
            # Example: search for a visible text
            button = driver.find_element(By.XPATH, "//*[contains(text(), 'Conditions générales d'assurance')]")
            # Search for a link in the parent or a sibling button
            parent = button.find_element(By.XPATH, "./..")
            link = parent.find_element(By.TAG_NAME, "a")
            pdf_url = link.get_attribute("href")
            print("PDF link found:", pdf_url)
        except Exception as e:
            print("PDF not found automatically:", e)

        driver.quit() 