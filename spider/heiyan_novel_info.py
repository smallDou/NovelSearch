#!/usr/bin/env python
"""
 Created by howie.hu at 30/03/2018.
"""
import time

from pprint import pprint

from ruia import Spider, Item, TextField, AttrField
from ruia_ua import middleware as ua_middleware

import requests
from lxml import etree

import sys
sys.path.append('../../')
from NovelSearch.db.es import ElasticObj


class HYNovelInfoItem(Item):
    """
    定义继承自item的Item类
    """
    novel_title = AttrField(css_select="meta[property='og:title']", attr='content')
    novel_author = AttrField(css_select="meta[property='og:novel:author']", attr='content')
    novel_cover = AttrField(css_select="meta[property='og:image']", attr='content')
    novel_abstract = AttrField(css_select="meta[property='og:description']", attr='content')
    novel_status = AttrField(css_select="meta[property='og:novel:status']", attr='content')
    novel_type = AttrField(css_select="meta[property='og:novel:category']", attr='content')
    #novel_chapter_url = AttrField(css_select='div#voteList a.index', attr='href')
    #latest_chapter = AttrField(css_select="meta[property='og:novel:latest_chapter_name']", attr='content')
    #latest_chapter_url = AttrField(css_select="meta[property='og:novel:latest_chapter_url']", attr='content')
    novel_lastest_update = AttrField(css_select="meta[property='og:novel:update_time']", attr='content')

    # novel_name = TextField(css_select='div.c-left>div.mod>div.hd>h2')
    # author = TextField(css_select='div.author-zone div.right a.name strong')
    # cover = AttrField(css_select='img.book-cover', attr='src')
    # abstract = TextField(css_select='pre.note')
    # status = ''
    # novels_type = TextField(css_select='div.c-left>div.mod>div.hd>p.infos>span.cate>a')
    # latest_chapter = ''
    # novel_chapter_url = AttrField(css_select='div#voteList a.index', attr='href')
    async def clean_novel_url(self, novel_url):
        return novel_url.replace('/book/','/chapter/') 

    async def clean_cover(self, cover):
        if 'https' in cover:
            return cover
        else:
            return cover.replace('http', 'https')

    async def clean_novels_type(self, novels_type):
        types_dict = {
            '社会': '都市'
        }
        print(types_dict.get(str(novels_type).strip(), novels_type))
        return types_dict.get(str(novels_type).strip(), novels_type)

    async def clean_latest_chapter_time(self, latest_chapter_time):
        return latest_chapter_time.replace(u'今天', str(time.strftime("%Y-%m-%d ", time.localtime()))).replace(u'昨日', str(
            time.strftime("%Y-%m-%d ", time.localtime(time.time() - 24 * 60 * 60))))


class HYNovelInfoSpider(Spider):
    request_config = {
        'RETRIES': 8,
        'DELAY': 0,
        'TIMEOUT': 3
    }
    es = ElasticObj(ip='47.106.120.31')

    async def parse(self, res):
        item = await HYNovelInfoItem.get_item(html=res.html)

        item_data = {
            'novel_url': res.url,
            'novel_title': item.novel_title,
            'novel_author': item.novel_author,
            'novel_status': item.novel_status,
            'novel_cover': item.novel_cover,
            'novels_type': item.novel_type,
            'novel_cover': item.novel_cover,
            'novel_abstract': item.novel_abstract,
            'novel_lastest_update': item.novel_lastest_update,
            'source': '黑岩',
        }
        self.logger.info(item_data)
        # await self.save(item_data)

    async def save(self, res_dic):
        # 存进es
        try:
            await self.es.Index_Data(res_dic)
            #self.logger.info("插入成功")
            return True
        except Exception as e:
            self.logger.exception(e)
            return False

def get_urls():
    url = 'https://www.heiyan.com/web/all/-1/-1/-1/-1/0/1/10000'
    response = requests.get(url)
    html = etree.HTML(response.text)
    items = html.xpath('//tbody[@id="resultDiv"]/tr')
    for item in items:
        url = item.xpath('.//div[@class="range"]/a[1]/@href')[0]
        yield url

if __name__ == '__main__':
    HYNovelInfoSpider.start_urls = [url for url in get_urls()]
    HYNovelInfoSpider.start(middleware=ua_middleware)
