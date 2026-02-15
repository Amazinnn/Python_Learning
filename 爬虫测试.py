import re
from urllib.request import urlopen
from bs4 import BeautifulSoup

html = urlopen("https://www.huanqiu.com").read().decode('utf-8')
all_matches = re.findall(r'<a.*?href="(.*?)".*?target="_blank">(.*?)</a>', html)
for href,title in all_matches:
    if len(href) < 70 and 10<len(title)<60 and href.startswith('http'):
        print(f"{href}    {title}")


#使用 BeautifulSoup爬取新闻标题与报道链接
soup = BeautifulSoup(html, features='lxml')
print("\n\n")
print("soup.h1:\n",soup.h1)
print("\n\n")
print("soup.p:\n",soup.p)
print("\n\n")
all_href = soup.find_all('a',{"target":"_blank","href":re.compile(r'.*?'),"title":re.compile(r'.*?')})
#print("all_href:\n",all_href)
print("\n\nh['href']:")
for h in all_href:
    if True or h['href'].startswith('http'):
        print(h,"\n",h['href'],"\n")

#使用 BeautifulSoup爬取新闻图片链接
print("\n\nimg_links:")
img_links = soup.find_all('img', {"src": re.compile(r'.*?\.jpg')})
for img in img_links:
    print(img['src'])




