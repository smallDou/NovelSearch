import requests
import logging
from lxml import etree
import sys
sys.path.append('../')
from NovelSearch.fetcher.function import get_random_user_agent

import logging
logging.basicConfig(level=logging.INFO)

from db.es import ElasticObj

class KSZNovels():
    def __init__(self):
        self.es = ElasticObj(ip='47.106.120.31')
    
    def get_page(self,url):
        headers = {
            'user-agent': get_random_user_agent(),
        }
        response = requests.get(url,headers=headers)
        response.encoding = 'gbk'
        if response.status_code == 200:
            return response.text
        else:
            return ''

    def parse_details_page(self, response, url, book_number):
        html = etree.HTML(response)
        try:
            res_dic = {}
            res_dic['novel_url'] = url
            res_dic['novel_title'] = html.xpath('//div[@class="mu_h1"]/h1/text()')[0]
            res_dic['novel_author'] = html.xpath('//div[@class="infos"]/span[1]/h3/text()')[0].replace('作者：','')
            res_dic['novel_type'] = html.xpath('//div[@class="infos"]/span[2]/a/text()')[0]
            res_dic['novel_status'] = ''
            res_dic['source'] = '看书中'
            res_dic['novel_cover'] = f'https://www.kanshuzhong.com/image/{book_number[:3]}/{book_number}/{book_number}s.jpg'
            res_dic['novel_abstract'] = ('').join(html.xpath('//*[@id="header"]/div[3]/div[3]/ul/div/p/text()')).strip().replace('\xa0','')
            res_dic['novel_lastest_update'] = html.xpath('//div[@class="infos"]/span[3]/text()')[0].replace('更新时间：','')
            logging.info(res_dic)
            self.save(res_dic)
        except Exception as e:
            logging.error(e)  
    
    def save(self, res_dic):
        try:
            self.es.Index_Data(res_dic)
            return True
        except Exception as e:
            logging.error(e)
            return False

    def main(self):
        for i in range(100001,121000):
            url = f'https://www.kanshuzhong.com/book/{str(i)}/'
            self.parse_details_page(self.get_page(url), url, str(i))

if __name__ == "__main__":
    n = KSZNovels()
    n.main()