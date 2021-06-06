import re
from goose3 import Goose
from goose3.text import StopWordsKorean
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.request import Request, urlopen
class Kukmin_crawling:
    def __init__(self): 
        self.categories = ['정치','경제','사회']
        self.article_url = ""
        self.urls = []
        self.articles = [] # 각 기사들의 정보들을 담을 리스트
        self.check_valid = True # 검색했을때 나오는 데이터가 나오는지 안나오는지를 비교
        self.choose_category=1
    def get_date(self, now):
        now = str(now)
        year = now[:4]
        month = now[5:7]
        day = now[8:10]
        return year+month+day

    def crawling(self):
        News_end = False
        while(not News_end):
            try:
                with urllib.request.urlopen(self.article_url) as response:
                    html = response.read()
                    soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
                    #기사의 url들을 파싱하는 부분
                    article_list = soup.find("div",{"id":"container"})
                    article_list = article_list.find("div",{"class":"nws_list"})
                    try:
                        article_list = article_list.find_all("div",{"class":"nws"})
                    except:
                        self.check_valid=False
                        print("리스트 읽어오기 실패")
                        return    
                    try:
                        for article in article_list:
                            link =  article.find("a")
                            link = "http://news.kmib.co.kr/article/"+link['href']
                            self.urls.append(link)
                    except:
                        print("url 찾기 실패")
                        return
                    next_url = ""
                    pages = soup.find("div",{"id":"container"})
                    pages = pages.find("div",{"class":"paging"})
                    current_page = pages.find("strong").string  # 현재 페이지 찾음
                    next_button = pages.find("a",{"class":"next"})
                    pages = pages.find_all("a")
                    try:
                        for page in pages:
                            if page.string!=None:
                                if(int(current_page)<int(page.string)):
                                    next_url = page['href']
                                    break
                        if(next_url!=""):
                            pass
                        else: #다음 화살표 누르기
                            try:
                                next_url = next_button['href']
                            except:
                                News_end = True
                        if(not News_end):
                            self.article_url = "http://news.kmib.co.kr/article/"+next_url
                    except:
                        print("페이지 이동 실패")
                        return
            except:
                return




    def category_crawling(self, choose_category):
        now = datetime.now()-relativedelta(days=1) # 실제엔 relative(days=1)을 빼자
        now = self.get_date(now)
        if choose_category==1: #정치
            self.article_url = "http://news.kmib.co.kr/article/list.asp?sid1=pol&sid2=&sdate="+now
            self.choose_category = 1
        elif choose_category==2: # 경제
            self.article_url="http://news.kmib.co.kr/article/list.asp?sid1=eco&sid2=&sdate="+now
            self.choose_category = 2
        else: #사회
            self.article_url = "http://news.kmib.co.kr/article/list.asp?sid1=soc&sid2=&sdate="+now
            self.choose_category = 3
        self.crawling()
        

    def read_article_contents(self,url):
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
                article_contents = soup.find("div",{"id":"articleBody"})
                text = ""
                try:
                    text = text + ' '+ article_contents.get_text(' ', strip=True)
                except:
                    print("error" , url)
                return text
        except:
            return ""
    
    def get_news(self):# 실제로 url에 들어가 기사들을 읽어온다 , 첫번째 카테고리만으로 검색했을때 데이터를 가져와준다
        print('기사 추출 시작')
        for url in self.urls:
            article_info = {"title":"","contents":"","url":"","category":""}
            category = self.categories[self.choose_category-1]
            try:
                g = Goose({'stopwords_class':StopWordsKorean})
                article = g.extract(url=url)
                title = article.title
            except:
                continue
            if title=="":
                continue
            contents = self.read_article_contents(url)
            find_email = re.compile('[a-zA-Z0-9_-]+@[a-z]+.[a-z]+').finditer(contents)
            for email in find_email:
                contents = contents[:email.start()]
            article_info["category"] = category
            article_info["contents"] = contents
            article_info["title"] = title
            article_info["url"] = url
            self.articles.append(article_info)
        return self.articles    
        

if __name__ == "__main__":

    A = Kukmin_crawling()
    A.category_crawling(3)
    ll = A.get_news()
    with open("aaaaaaaaa.txt","w",encoding='utf-8') as f:
        for i in ll:
            f.write(i['contents'])
            f.write('\n\n\n')

 