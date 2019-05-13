#!/usr/bin/env python
"""
 Created by howie.hu at 14/03/2018.
 纵横小说信息提取：http://book.zongheng.com/store/c0/c0/b9/u0/p1/v9/s9/t0/ALL.html
"""
import asyncio
import os
import time

from ruia import Spider, Item, TextField, AttrField, Request
from ruia_ua import middleware as ua_middleware

import sys
sys.path.append('../')
from db.es import ElasticObj

class ZHNovelsItem(Item):
    target_item = TextField(css_select='div.store_collist div.bookbox')
    novel_url = AttrField(css_select='div.bookinfo div.bookname a', attr='href')
    novel_title = TextField(css_select='div.bookinfo div.bookname a')
    novel_author = TextField(css_select='div.bookilnk a:nth-child(1)')
    novel_type = TextField(css_select='div.bookilnk a:nth-child(2)')
    novel_cover = AttrField(css_select='div.bookimg img', attr='src')
    novel_abstract = TextField(css_select='div.bookintro')
    novel_lastest_update = TextField(css_select='div.bookupdate a')

    async def clean_novel_url(self, novel_url):
        return novel_url.replace('/book/','/showchapter/') 

    async def clean_novel_author(self, novel_author):
        if novel_author:
            if isinstance(novel_author, list):
                novel_author = novel_author[0].text
            return novel_author
        else:
            return ''

    async def clean_novel_url(self, novel_abstract):
        return novel_abstract.replace('\\r','').replace('\\n','').replace(r'\u3000','')

            # def tal_novel_author_home_url(self, novel_author_home_url):
            #     if isinstance(novel_author_home_url, list):
            #         novel_author_home_url = novel_author_home_url[0].get('href').strip()
            #     return 'http:' + novel_author_home_url

    async def save(self, res_dic):
        # 存进es
        try:
            await self.es.Index_Data(res_dic)
            #self.logger.info("插入成功")
            return True
        except Exception as e:
            self.logger.exception(e)
            return False

class ZHNovelsSpider(Spider):
    start_urls = ['http://book.zongheng.com/store/c0/c0/b9/u0/p1/v9/s9/t0/ALL.html']

    request_config = {
        'RETRIES': 8,
        'DELAY': 0,
        'TIMEOUT': 3
    }
    concurrency = 60
    es = ElasticObj(ip='47.106.120.31')

    async def parse(self, res):
        items_data = ZHNovelsItem.get_items(html=res.html)
        async for item in items_data:
            if item.novel_url:
                res_dic = {
                    'novel_url': item.novel_url,
                    'novel_title': item.novel_title,
                    'novel_author': item.novel_author,
                    'novel_status': '',
                    'novel_type': item.novel_type,
                    'novel_cover': item.novel_cover,
                    'novel_abstract': item.novel_abstract,
                    'novel_lastest_update': item.novel_lastest_update,
                    'source': '纵横',
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
    # 其他多item示例：https://gist.github.com/howie6879/3ef4168159e5047d42d86cb7fb706a2f
    # 51793
    ZHNovelsSpider.start_urls = ['http://book.zongheng.com/store/c0/c0/b9/u0/p{i}/v9/s9/t0/ALL.html'.format(i=i) for
                                    i in
                                    range(1, 20000)]
    # 其他多item示例：https://gist.github.com/howie6879/3ef4168159e5047d42d86cb7fb706a2f
    ZHNovelsSpider.start(middleware=[ua_middleware], close_event_loop=False)
