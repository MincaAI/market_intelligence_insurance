import scrapy
 
class InsuranceScraperItem(scrapy.Item):
    product = scrapy.Field()
    pdf_url = scrapy.Field()
    file_name = scrapy.Field()
    local_path = scrapy.Field() 