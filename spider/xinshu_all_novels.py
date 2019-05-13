import requests
import logging
from lxml import etree
import sys
sys.path.append('../')
from NovelSearch.fetcher.function import get_random_user_agent

##有反爬，暂不可用
class XSNovels():
    def __init__(self):
        pass
    
    def get_page(self,url):
        headers = {
            #'user-agent': get_random_user_agent(),
        }
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return ''
    
    def parse_index_page(self,response):
        html = etree.HTML(response)
        items = html.xpath("//ul[@class='ul_m_list']/li")
        for item in items:
            res_dic = {}
            res_dic['novel_url'] = 'http://www.xinshuxs.com' + item.xpath('.//div[@class="t"]/a/@href')[0]
            res_dic['novel_title'] = item.xpath('.//div[@class="t"]/a/text()')[0]
            res_dic['novel_author'] = item.xpath('.//div[@class="author"]/a/text()')[0]
            res_dic['novel_status'] = item.xpath('.//div[@class="abover"]/span/text()')[0]
            res_dic['novel_type'] = item.xpath('.//div[@class="c"]/a/text()')[0]
            res_dic['source'] = '新书在线'
            logging.info(res_dic)
            res_dic = self.parse_details_page(self.get_page(res_dic['novel_url']), res_dic)
            logging.info(res_dic)

    def parse_details_page(self, response, res_dic):
        html = etree.HTML(response)
        if html:
            res_dic['novel_cover'] = 'http://www.xinshuxs.com' + html.xpath('//div[@class="pic"]/a/img/@src')[0]
            res_dic['novel_abstract'] = ''.join(html.xpath('//div[@class="words"]/p[2]/text()'))
            res_dic['novel_lastest_update'] = html.xpath('//div[@class="words"]/text()[2]')[0]
        else:
            pass    
            return res_dic
    
    def main(self):
        for i in range(1,511):
            url = f'http://www.xinshuxs.com/shuku_25490_{str(i)}.html'
            self.parse_index_page(self.get_page(url))

    def test(self):
        print(self.parse_details_page())

if __name__ == "__main__":
    n = XSNovels()
    n.main()