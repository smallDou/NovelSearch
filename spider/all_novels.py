from .qidian import QidianNovelsSpider
from ruia_ua import middleware as ua_middleware
import os
import subprocess

class NovelsSpider():
    def __init__(self,wd=''):
        self.wd = wd
        self.base_url = os.path.dirname(os.path.abspath(__file__))

    def start(self):
        QidianNovelsSpider.start_urls = [f'https://www.qidian.com/search?kw={self.wd}']
        QidianNovelsSpider.start(middleware=[ua_middleware],  close_event_loop=False)

    def start_by_tem(self):
        servers = [
        ["python3", os.path.join(self.base_url+'/qidian.py'), f"{self.wd}"],
        ]
        procs = []
        for server in servers:
            proc = subprocess.Popen(server)
            procs.append(proc)
        for proc in procs:
            proc.wait()
            if proc.poll():
                exit(0)

if __name__ == '__main__':
    s = NovelsSpider('剑来')
    s.start()
    # print(s.base_url)