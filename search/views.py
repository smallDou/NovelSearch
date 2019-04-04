from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View

from db.es import ElasticObj
from spider.all_novels import NovelsSpider
from spider.qidian import QidianNovelsSpider
from ruia_ua import middleware as ua_middleware

class IndexView(View):
    #首页
    def get(self, request):
        return render(request, 'index.html')
    
class SearchSuggest(View):
    #django-haystack 实现搜索结果高亮等
    pass

class SearchView(View):
    def get(self,request):
        key_words = request.GET.get("wd","")
        # print(key_words)
        spider = NovelsSpider(key_words)
        spider.start()  #执行爬虫
        # QidianNovelsSpider.start_urls = [f'https://www.qidian.com/search?kw={key_words}']
        # QidianNovelsSpider.start(middleware=[ua_middleware],  close_event_loop=False)

        es = ElasticObj(ip ="47.106.120.31")
        res = es.Get_Data_By_Body(key_words) #es默认刷新时间为1s
        if key_words:
            return render(request, "results.html" , {'res':res})