# Script Playwright pour capturer la partie basse de la page à partir d'une section spécifique (Baloise)

import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image, ImageDraw, ImageFont

def get_screenshot_path(product):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    screenshots_dir = os.path.join(base_dir, 'data', 'reviews_screenshots', 'baloise')
    os.makedirs(screenshots_dir, exist_ok=True)
    return os.path.join(screenshots_dir, f'{product}_insurance_note.png')

def add_title_banner(image_path, title):
    img = Image.open(image_path)
    banner_height = 60
    new_img = Image.new('RGB', (img.width, img.height + banner_height), (255, 255, 255))
    draw = ImageDraw.Draw(new_img)
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()
    # Draw banner background
    draw.rectangle([0, 0, img.width, banner_height], fill=(255, 255, 255))
    # Mesure la taille du texte avec compatibilité
    try:
        bbox = draw.textbbox((0, 0), title, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        # Fallback pour anciennes versions de Pillow
        text_w, text_h = draw.textsize(title, font=font)
    draw.text(((img.width - text_w) // 2, (banner_height - text_h) // 2), title, fill=(0, 0, 0), font=font)
    new_img.paste(img, (0, banner_height))
    new_img.save(image_path)

def get_config(product):
    if product == 'car':
        return {
            'url': 'https://www.baloise.ch/de/privatkunden/versichern/fahrzeuge/autoversicherung.html',
            'title': 'Baloise - Car Insurance - Bewertungen',
            'screenshot_path': get_screenshot_path('car')
        }
    else:
        return {
            'url': '',  # Pas de review pour travel
            'title': 'Baloise - Travel Insurance - No review section',
            'screenshot_path': get_screenshot_path('travel')
        }

async def capture_bottom_from_section(product='travel', hauteur_voulue=800):
    config = get_config(product)
    url = config['url']
    screenshot_path = config['screenshot_path']
    title = config['title']
    if not url:
        print(f"No review section for {product}.")
        return
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)
        element = await page.query_selector('text="Bewertungen"')
        if element:
            box = await element.bounding_box()
            await page.screenshot(path=screenshot_path, full_page=True)
            img = Image.open(screenshot_path)
            left = 0
            top = int(box['y'])
            right = img.width
            bottom = min(img.height, top + hauteur_voulue)
            cropped = img.crop((left, top, right, bottom))
            cropped.save(screenshot_path)
            print(f"Screenshot du bas de page à partir de 'Bewertungen' pour {product}, hauteur {hauteur_voulue}px.")
        else:
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Élément 'Bewertungen' non trouvé, screenshot complet pour {product}.")
        await browser.close()
    add_title_banner(screenshot_path, title)
    print(f"Screenshot enregistré : {screenshot_path}")

if __name__ == "__main__":
    import sys
    # Usage: python baloise_reviews.py [car|travel] [hauteur]
    product = 'travel'
    hauteur = 800
    if len(sys.argv) > 1 and sys.argv[1] in ['car', 'travel']:
        product = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            hauteur = int(sys.argv[2])
        except ValueError:
            pass
    asyncio.run(capture_bottom_from_section(product, hauteur)) 