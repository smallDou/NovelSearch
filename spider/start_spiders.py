from dishuge_all_novels import DSGNovels
from kanshuzhong_all_novels import KSZNovels
from zongheng_all_novels import ZHNovelsSpider

if __name__ == "__main__":
    dsn = DSGNovels()
    dsn.main()

    kszn = KSZNovels()
    kszn.main()
