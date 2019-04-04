#coding:utf-8
import os
import time
from os import walk
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from utils.tools import singleton

@singleton
class ElasticObj(object):
    def __init__(self, index_name="novel",index_type="novel_type",ip ="127.0.0.1"):
        '''
        :param index_name: 索引名称
        :param index_type: 索引类型
        '''
        self.index_name =index_name
        self.index_type = index_type
        # 无用户名密码状态
        self.es = Elasticsearch([ip],port=9200)
        #用户名密码状态
        #self.es = Elasticsearch([ip],http_auth=('elastic', 'password'),port=9200)

    def create_index(self,index_name="novel",index_type="novel_type"):
        '''
        创建索引,创建索引名称为novel，类型为novel_type的索引
        :param ex: Elasticsearch对象
        :return:
        '''
        #创建映射
        _index_mappings = {
            "mappings": {
                self.index_type: {
                    "properties": {
                        "novel_title": {
                            "type": "text",
                            "index": True,
                            "analyzer": "ik_max_word", 
                            "search_analyzer": "ik_max_word" #设置中文分词插件
                        },
                        "novel_url": {
                            "type": "text",
                            "index": "not_analyzed"
                        },
                        "novel_autor": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "novel_type": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "novel_status": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "novel_cover": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "novel_abstract": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "novel_lastest_update": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "novel_nums": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "source": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                    }
                }

            }
        }
        if self.es.indices.exists(index=self.index_name) is not True:
            res = self.es.indices.create(index=self.index_name, body=_index_mappings)
            print(res)

    async def Index_Data(self,item):
        '''
        数据存储到es
        :return:
        '''
        res = self.es.index(index=self.index_name, doc_type=self.index_type, body=item, id=item.get('source')+item.get('novel_title'), refresh=True)
        #print("成功插入一条数据")

    def Delete_Index_Data(self,id):
        '''
        删除索引中的一条
        :param id:
        :return:
        '''
        res = self.es.delete(index=self.index_name, doc_type=self.index_type, id=id, refresh=True)
        print(res)

    def Delete_all(self):
        doc = {'query': {'match_all': {}}}
        res = self.es.delete_by_query(index=self.index_name, doc_type=self.index_type, body=doc)

    def Get_Data_Id(self,id):

        res = self.es.get(index=self.index_name, doc_type=self.index_type,id=id)
        print(res['_source'])

        print('------------------------------------------------------------------')
        #
        # # 输出查询到的结果
        for hit in res['hits']['hits']:
            # print hit['_source']
            print(hit['_source']['date'],hit['_source']['source'],hit['_source']['link'],hit['_source']['keyword'],hit['_source']['title'])

    def Get_Data_By_Body(self,word=''):
        # doc = {'query': {'match_all': {}}}
        doc = {
            "query": {
                "match": {
                    "novel_title": f"{word}"
                }
            }
        }
        _searched = self.es.search(index=self.index_name, doc_type=self.index_type, body=doc)
        return _searched

        # for hit in _searched['hits']['hits']:
        #     # print hit['_source']
        #     print(hit['_source'])

if __name__ == '__main__':
    obj =ElasticObj(ip ="47.106.120.31")
    # obj = ElasticObj("ott1", "ott_type1")
    # obj.create_index()
    # obj.Index_Data()
    # obj.bulk_Index_Data()
    # obj.IndexData()
    # obj.Delete_Index_Data('4')
    # csvfile = 'D:/work/ElasticSearch/exportExcels/2017-08-31_info.csv'
    # obj.Index_Data_FromCSV(csvfile)
    # obj.GetData(es)
    # obj.Delete_all()
    obj.Get_Data_By_Body('流浪地球')