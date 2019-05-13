#!/usr/bin/env python
"""
 Created by howie.hu at 25/02/2018.
 Target URI: https://www.qidian.com/all
        Param:?page=1
"""
import asyncio
import os
import time

from ruia import Spider, Item, TextField, AttrField
from ruia_ua import middleware as ua_middleware

import sys
sys.path.append('../../')
from NovelSearch.db.es import ElasticObj

class QidianNovelsItem(Item):
    target_item = TextField(css_select='ul.all-img-list>li')
    novel_url = AttrField(css_select='div.book-img-box>a', attr='href')
    novel_title = TextField(css_select='div.book-mid-info>h4')
    novel_author = TextField(css_select='div.book-mid-info>p.author>a.name')
    novel_type = TextField(css_select='div.book-mid-info > p.author > a:nth-child(4)')
    novel_status = TextField(css_select='div.book-mid-info>p.author>span')
    novel_cover = AttrField(css_select='div.book-img-box img', attr='src')
    novel_abstract = TextField(css_select='div.book-mid-info p.intro')
    novel_lastest_update = TextField(css_select='div.book-mid-info > p.update > b.red')

    # novel_latest_chapter = TextField(css_select='div.bookupdate a')

    async def clean_novel_url(self, novel_url):
        return 'https:' + novel_url

    async def clean_novel_author(self, novel_author):
        if isinstance(novel_author, list):
            novel_author = novel_author[0].text
        return novel_author

    async def clean_novel_cover(self, novel_cover):
        return 'https:' + novel_cover


class QidianNovelsSpider(Spider):
    # start_urls = ['https://www.qidian.com/all?page=1']

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
                'source': '起点中文网',
            }
            #self.logger.info(res_dic)
            await self.save(res_dic)

    async def save(self, res_dic):
        # 存进es
        try:
            await self.es.Index_Data(res_dic)
            #self.logger.info("插入成功")
            return True
        except Exception as e:
            self.logger.exception(e)
            return False


if __name__ == '__main__':
    # 51793
    QidianNovelsSpider.start_urls = ['https://www.qidian.com/all?orderId=5&page={i}'.format(i=i) for i in
                                        range(1, 3000)]
    # 其他多item示例：https://gist.github.com/howie6879/3ef4168159e5047d42d86cb7fb706a2f
    QidianNovelsSpider.start(middleware=[ua_middleware], close_event_loop=False)
