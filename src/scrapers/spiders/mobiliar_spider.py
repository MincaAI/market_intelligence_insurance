import scrapy
from bs4 import BeautifulSoup
from src.scrapers.items import InsuranceScraperItem
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import tempfile
import shutil
import os

MOBILIAR_URLS = {
    "travel": "https://oiv.mobiliar.ch/avb/TRP-01-2025/homepage",
    "car": "https://www.mobiliar.ch/rechtliches/allgemeine-versicherungsbedingungen"
}

class MobiliarSpider(scrapy.Spider):
    name = "die_mobiliar"
    allowed_domains = ["mobiliar.ch"]

    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force product to be 'car' or 'travel' only
        if product and product.lower().startswith('car'):
            self.product = 'car'
        elif product and product.lower().startswith('travel'):
            self.product = 'travel'
        else:
            self.product = 'travel'  # Default
        self.start_urls = [MOBILIAR_URLS[self.product]]

    def parse(self, response):
        if self.product == "Travel Insurance":
            # Prépare un dossier temporaire pour le téléchargement
            download_dir = tempfile.mkdtemp()
            self.logger.info(f"[DEBUG] Dossier temporaire de téléchargement : {download_dir}")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,
                "profile.default_content_setting_values.automatic_downloads": 1
            }
            chrome_options.add_experimental_option("prefs", prefs)
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(self.start_urls[0])
            self.logger.info("[DEBUG] Page chargée dans Selenium")
            try:
                wait = WebDriverWait(driver, 10)
                self.logger.info("[DEBUG] Recherche du bouton 'PDF herunterladen'")
                btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'PDF herunterladen')]")))
                self.logger.info("[DEBUG] Bouton trouvé, clic en cours...")
                btn.click()
                self.logger.info("[DEBUG] Clic effectué, attente du téléchargement du PDF...")
                # Attend que le PDF soit téléchargé (max 20s)
                pdf_file = None
                for i in range(40):
                    files = [f for f in os.listdir(download_dir) if f.lower().endswith('.pdf')]
                    self.logger.info(f"[DEBUG] Fichiers trouvés à l'itération {i}: {files}")
                    if files:
                        pdf_file = files[0]
                        break
                    time.sleep(0.5)
                if pdf_file:
                    self.logger.info(f"[DEBUG] PDF téléchargé : {pdf_file}")
                    # Déplace le PDF dans le dossier data/documents/die_mobiliar/
                    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    documents_dir = os.path.join(base_dir, 'data', 'documents', 'die_mobiliar')
                    os.makedirs(documents_dir, exist_ok=True)
                    src_path = os.path.join(download_dir, pdf_file)
                    dest_path = os.path.join(documents_dir, pdf_file)
                    shutil.move(src_path, dest_path)
                    self.logger.info(f"[DEBUG] PDF déplacé vers : {dest_path}")
                    yield InsuranceScraperItem(
                        product=self.product,
                        pdf_url="(downloaded by Selenium)",
                        file_name=pdf_file,
                        local_path=dest_path
                    )
                else:
                    self.logger.error("[DEBUG] PDF not downloaded après clic sur le bouton Die Mobiliar (travel)")
            except Exception as e:
                self.logger.error(f"[DEBUG] Selenium error for Die Mobiliar (travel): {e}")
            finally:
                driver.quit()
                self.logger.info(f"[DEBUG] Contenu final du dossier temporaire : {os.listdir(download_dir)}")
                shutil.rmtree(download_dir)
            return
        elif self.product == "Car Insurance":
            # Cherche les liens PDF dans la page AVB générale
            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text().lower()
                if href.endswith(".pdf") or "download?inline" in href:
                    if "vehicle" in text or "fahrzeug" in text or "auto" in text:
                        pdf_url = response.urljoin(href)
                        file_name = re.sub(r"[^a-z0-9]+", "_", text)[:80] + ".pdf"
                        yield InsuranceScraperItem(
                            product=self.product,
                            pdf_url=pdf_url,
                            file_name=file_name
                        )
                        return
            self.logger.error(f"No PDF found for {self.product} on Die Mobiliar (car)") 