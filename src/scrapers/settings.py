BOT_NAME = 'insurance_docs_processor'

SPIDER_MODULES = ['src.scrapers.spiders']
NEWSPIDER_MODULE = 'src.scrapers.spiders'

ITEM_PIPELINES = {
    'src.scrapers.pipelines.InsuranceScraperPipeline': 300,
}

ROBOTSTXT_OBEY = True 