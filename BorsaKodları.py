import requests
from bs4 import BeautifulSoup
import re

url ="https://www.kap.org.tr/en/bist-sirketler"
page = requests.get(url)

soup = BeautifulSoup(page.content,"html.parser")

#print(soup)

results = soup.findAll("div", {"class": "comp-cell _04 vtable"})

#print(results)

results = str(results)
results = results.replace(" "," ")
words = re.findall(r">\S+</a>",results)
list1=[]

for i in words:
    i = i.replace(">"," ")
    i = i.replace("</a"," ")
    i = i.replace(" ", "")
    i = i.split(",")
    list1.append(i)

#print(list1)
for i in list1:
    print(i)









