import requests
import logging
from lxml import etree
import sys
sys.path.append('../')
from NovelSearch.fetcher.function import get_random_user_agent

import logging
logging.basicConfig(level=logging.INFO)

from db.es import ElasticObj

class DSGNovels():
    def __init__(self):
        self.es = ElasticObj(ip='47.106.120.31')
    
    def get_page(self,url):
        headers = {
            'user-agent': get_random_user_agent(),
        }
        response = requests.get(url,headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
        else:
            return ''

    def parse_details_page(self, response, url):
        html = etree.HTML(response)
        if html:
            try:
                res_dic = {}
                res_dic['novel_url'] = url
                res_dic['novel_title'] = html.xpath('//*[@id="info"]/h1/text()')[0]
                res_dic['novel_author'] = html.xpath('//*[@id="info"]/p[2]/text()')[0].replace('作者：','')
                res_dic['novel_type'] = html.xpath('//*[@id="container"]/div[1]/div[1]/a[2]/text()')[0]
                res_dic['novel_status'] = ''
                res_dic['source'] = '帝书阁'
                res_dic['novel_cover'] = html.xpath('//*[@id="fmimg"]/img/@src')[0]
                res_dic['novel_abstract'] = html.xpath('//*[@id="duction"]/text()')[0].strip().replace('\r','').replace('\u3000','')
                res_dic['novel_lastest_update'] = html.xpath('//div[@id="info"]/p[1]/text()')[0].replace('最后更新：','')
                logging.info(res_dic)
                self.save(res_dic)
            except Exception as e:
                logging.error(e)
        else:
            logging.error('解析详情页出错')    
    
    def save(self, res_dic):
        # 存进es
        try:
            self.es.Index_Data(res_dic)
            #self.logger.info("插入成功")
            return True
        except Exception as e:
            logging.error(e)
            return False

    def main(self):
        for i in range(1,40000):
            url = f'http://www.dishuge.com/book/{str(i)}/'
            self.parse_details_page(self.get_page(url), url)

if __name__ == "__main__":
    n = DSGNovels()
    n.main()