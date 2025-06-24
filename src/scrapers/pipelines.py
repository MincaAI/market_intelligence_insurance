import os
import requests
import scrapy
from bs4 import BeautifulSoup
from src.scrapers.items import InsuranceScraperItem

class InsuranceScraperPipeline:
    def process_item(self, item, spider):
        # Dossier par assureur et produit (car/travel)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        product = item.get('product', '').lower()
        # Map product names to folder names
        if 'car' in product:
            product_folder = 'car'
        elif 'travel' in product:
            product_folder = 'travel'
        else:
            product_folder = product.replace(' ', '_') if product else ''
        if product_folder:
            documents_dir = os.path.join(base_dir, 'data', 'documents', spider.name, product_folder)
        else:
            documents_dir = os.path.join(base_dir, 'data', 'documents', spider.name)
        os.makedirs(documents_dir, exist_ok=True)
        file_name = item['file_name']
        local_path = os.path.join(documents_dir, file_name)
        item['local_path'] = local_path
        if not os.path.exists(local_path):
            response = requests.get(item['pdf_url'])
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
            else:
                spider.logger.error(f"Failed to download {item['pdf_url']}")
        else:
            spider.logger.info(f"File already exists: {local_path}")
        return item 