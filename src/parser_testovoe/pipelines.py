from .settings import DOWNLOAD_DIR, PATH
from scrapy.exporters import JsonItemExporter


class ParserTestovoePipeline:
    def __init__(self):
        self.exporter = None
        DOWNLOAD_DIR.mkdir(exist_ok=True)

    def open_spider(self, spider):
        self.exporter = JsonItemExporter(
            open(f'{DOWNLOAD_DIR}/{spider.name}.json', 'wb'),
            ensure_ascii=False,
            indent=4
        )
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
