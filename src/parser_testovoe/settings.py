from pathlib import Path

BOT_NAME = "parser_testovoe"

NEWSPIDER_MODULE = f"{BOT_NAME}.spiders"
SPIDER_MODULES = [NEWSPIDER_MODULE]

ROBOTSTXT_OBEY = False

PATH = Path(__file__).parent.parent.resolve()
DOWNLOAD_DIR = PATH / "data"

ITEM_PIPELINES = {
   "parser_testovoe.pipelines.ParserTestovoePipeline": 300,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.6"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# DOCKER
FLARE_SOLVER_URL = 'http://flaresolver:8191/v1'
# LOCAL
# FLARE_SOLVER_URL = 'http://localhost:8191/v1'
