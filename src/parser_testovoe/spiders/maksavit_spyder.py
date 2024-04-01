import re
from datetime import datetime

import scrapy

from .. import utils
from .. import xpathes
from ..items import ParserTestovoeItem
from ..settings import FLARE_SOLVER_URL

URL = 'https://maksavit.ru'

CATEGORY_1 = (
    'https://maksavit.ru/novosibirsk/catalog/materinstvo_i_detstvo/detskaya_gigiena/'
)

CATEGORY_2 = (
    'https://maksavit.ru/novosibirsk/catalog/gigiena_polosti_rta/pribory_dlya_ukhoda_za_polostyu_rta/'
)

CATEGORY_3 = (
    'https://maksavit.ru/novosibirsk/catalog/dermatovenerologiya/antiseptiki/'
)

PARS_URLS = [
    utils.generate_url_list(CATEGORY_1, num_pages=4),
    utils.generate_url_list(CATEGORY_2, num_pages=4),
    utils.generate_url_list(CATEGORY_3, num_pages=4)
]


class MaksavitSpyder(scrapy.Spider):
    name = 'maksavit'

    def start_requests(self):
        for urls in PARS_URLS:
            for url in urls:
                yield scrapy.Request(
                    url=FLARE_SOLVER_URL,
                    body=utils.get_fs_body(url),
                    headers={"Content-Type": "application/json"},
                    callback=self.list_products_lincs,
                    method="POST",
                )

    def list_products_lincs(self, response):
        response, cookies, user_agent = utils.parse_fs_response(response)

        products = response.xpath(xpathes.list_products)

        products_hrefs = [
            product_href for product in products
            if (product_href := product.xpath(xpathes.href).get()) is not None
        ]

        for href in products_hrefs:
            yield scrapy.Request(
                url=URL + href,
                cookies=cookies,
                headers={"User-Agent": user_agent},
                callback=self.parse,
                method="GET",
            )

    def parse(self, response, **kwargs):
        timestamp = int(datetime.now().timestamp())
        url = response.url
        product_id = re.search(r'\/(\d+)\/$', url).group(1)
        title = response.xpath(xpathes.name).get()
        sections = [
            section.xpath(xpathes.section).get()
            for section in response.xpath(xpathes.sections)[2:-1]
        ]

        tags = (
            tags
            if (tags := response.xpath(xpathes.marketing_tags).getall())
            else None
        )
        marketing_tags = [
            tag.strip() for tag in tags if tag is not None
        ] if tags else []

        brand = (
            brand.strip().split(',')[0]
            if (brand := response.xpath(xpathes.brand).get()) else 'Не указан'
        )

        current = float(
            current.split('₽')[0].strip().replace(' ', '')
            if (current := response.xpath(xpathes.current).get()) else 0
        )
        original = float(
            original.split('₽')[0].replace(' ', '')
            if (original := response.xpath(xpathes.original).get())
            and original.strip()
            else current
        )
        sale_tag = ''

        if current != original:
            discount_percentage = round(100 - ((current / original) * 100))
            sale_tag = f"Скидка {discount_percentage}%"

        in_stock = True if not response.xpath(xpathes.in_stock).get() else False

        image = URL + response.xpath(xpathes.image).get()

        variants = (
            variants
            if (variants := len(response.xpath(xpathes.variants))) > 1 else 1
        )

        metadata = {}
        for div in response.xpath(xpathes.metadata):
            key = div.xpath(xpathes.meta_key).get()
            div_text = (
                text.replace('\\', '').strip().strip('"')
                if (text := div.xpath(xpathes.div_text).get()) else None
            )
            value = div.xpath(xpathes.meta_value).getall()
            value = (
                ''.join(value).replace('\\', '').strip('"')
                if value else div_text
            )
            metadata[key] = value

        yield ParserTestovoeItem(
            timestamp=timestamp,
            RPC=product_id,
            url=url,
            title=title,
            marketing_tags=marketing_tags,
            brand=brand,
            section=sections,
            price_data=dict(
                current=current,
                original=original,
                sale_tag=sale_tag,
            ),
            stock=dict(
                in_stock=in_stock,
                count=0
            ),
            assets=dict(
                main_image=image,
                set_images=[],
                view360=[],
                video=[],
            ),
            metadata=metadata,
            variants=variants
        )
