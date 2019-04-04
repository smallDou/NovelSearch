#!/usr/bin/env python3

import asyncio
import os
import time
import sys

from ruia import Spider, Item, TextField, AttrField
from ruia_ua import middleware as ua_middleware
import sys
sys.path.append('..')
from db.es import ElasticObj

class QidianNovelsItem(Item):
    target_item = TextField(css_select='div.book-img-text>ul>li')
    novel_url = AttrField(css_select='div.book-img-box>a', attr='href')
    novel_title = TextField(css_select='div.book-mid-info>h4')
    novel_author = TextField(css_select='div.book-mid-info>p.author>a.name')
    novel_type = TextField(css_select='div.book-mid-info > p.author > a:nth-child(4)')
    novel_status = TextField(css_select='div.book-mid-info>p.author>span')
    novel_cover = AttrField(css_select='div.book-img-box img', attr='src')
    novel_abstract = TextField(css_select='div.book-mid-info p.intro')
    novel_lastest_update = TextField(css_select='div.book-mid-info > p.update')
    novel_nums = TextField(css_select='div.book-right-info > div > p:nth-child(1) > span')

    async def clean_novel_url(self, novel_url):
        return 'https:' + novel_url

    async def clean_novel_author(self, novel_author):
        if isinstance(novel_author, list):
            novel_author = novel_author[0].text
        return novel_author

    async def clean_novel_cover(self, novel_cover):
        return 'https:' + novel_cover


class QidianNovelsSpider(Spider):
    #start_urls = ['http://search.zongheng.com/s?keyword=剑来']

    request_config = {
        'RETRIES': 15,
        'DELAY': 0,
        'TIMEOUT': 3
    }
    concurrency = 20
    es = ElasticObj(ip='47.106.120.31')

    async def parse(self, res):
        items_data = QidianNovelsItem.get_items(html=res.html)
        async for item in items_data:
            res_dic = {
                'novel_url': item.novel_url,
                'novel_title': item.novel_title,
                'novel_author': item.novel_author,
                'novel_type': item.novel_type,
                'novel_status': item.novel_status,
                'novel_cover': item.novel_cover,
                'novel_abstract': item.novel_abstract,
                'novel_lastest_update': item.novel_lastest_update,
                'novel_nums': item.novel_nums,
                'source': 'qidian',
            }
            self.logger.info(res_dic)
            #self.save(res_dic)

    def save(self, res_dic):
        # 存进es
        try:
            self.es.Index_Data(res_dic)
            #self.logger.info("插入成功")
            return True
        except Exception as e:
            self.logger.exception(e)
            return False

if __name__ == '__main__':
    keyword = sys.argv[1]
    QidianNovelsSpider.start_urls = [f'https://www.qidian.com/search?kw={keyword}']
    QidianNovelsSpider.start(middleware=[ua_middleware], close_event_loop=False)