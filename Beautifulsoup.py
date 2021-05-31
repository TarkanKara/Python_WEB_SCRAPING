import  string
import requests         #HTTP isteği atama
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
from pprint import pprint


#MedlinePlus
#https://medlineplus.gov/druginformation.html

#İlk önce bir sınıf oluşturalım
class MedLineScraper:

    #init metotdu oluşturalım
    def __init__(self):
        self.base_url = "https://medlineplus.gov/druginfo"
        self.drug_links = set()

    #Alfabadeki harflere ihtiyacımız var
    def get_categories(self):
        letters = string.ascii_uppercase  # A-Z Bütün harfleri büyü olarak getirecektir.

        #Map fonksiyon ile alfabetik her bir harfi dolaşalım. Daha sonra base url sonuna metin ekleyeceğiz.
        result =  list(map(lambda letter: self.base_url + "/drug_{}a.html".format(letter),letters ))
        #https://medlineplus.gov/druginfo/drug_Aa.html
        #return letters
        result.append("https://medlineplus.gov/druginfo/drug_00.html")
        return result                                                   #Artık a dan z ve sıfırda dahil olmak üzere tüm linkler var

    #HTTP isteği atacak bir fonksiyon yazalım , import request kullanmalıyız
    def get_source(self, url):
        r = requests.get(url)
        if r.status_code == 200:    #Http isteği başarılı ise kaynağı al
            #Burada Beatifusoup modelü kullanır.
            return BeautifulSoup(r.content, "lxml")  #lxml kütüphanesi ile parse ettsin
        return False

    def get_drug_links(self, source):
        drug_elements = source.find("ul", attrs={"id": "index"}).find_all("li")
        #return all_drug_li
        #return list(map(lambda drug: drug.find("a").get("href"), drug_elements))  #Her bir ilacın linkini dönme işlemi
        #drug_links = list(map(lambda drug: drug.find("a").get("href").replace(".","",1), drug_elements))
        drug_links = list(map(lambda drug: self.base_url + drug.find("a").get("href").replace(".", "", 1), drug_elements))   #sel.base_url link yapısı ile birleştirelim
        #return  drug_links  #linklerdeki nokta işareti kalkmış oldu
        return set(drug_links)      #Aynı linkleri kümeliyor
        #return drug_links


    def find_all_drug_links(self):
        categories = self.get_categories()      #Tüm Kategoriler
        bar = tqdm(categories, unit=" category link")
        for category_link in bar:           #Her bir kategori linke http isteği atacak
            bar.set_description(category_link)
            category_source = self.get_source(category_link)        #Yukarıdaki kategori linkini parametre olarak gireceğiz
            result = self.get_drug_links(category_source)
            self.drug_links = self.drug_links.union(result)

        return self.drug_links


    def get_name(self, source):
        try:
            return source.find("h1", attrs={"class": "with-also"}).text
        except Exception:
            return None

    def get_section_info(self, source, id_element):
        try:
            title = source.find("div", attrs={"id": id_element}).find("h2").text
            content = source.find("div", attrs={"id": id_element}).find("div", attrs={"class": "section-body"}).text
            return dict(
                title=title,
                content=content
            )
        except Exception:
            return None



    def scrape_drugs(self):
        result = list()
        links = self.find_all_drug_links()
        bar = tqdm(links, unit=" drug link")
        i = 0
        for link in bar:
            if i == 10:
                break
            sections = list()                                   #Boş Bir liste Oluşturma
            bar.set_description(link)
            drug_source = self.get_source(link)
            name = self.get_name(drug_source)
            why = self.get_section_info(drug_source, "why")
            sections.append(why)
            how = self.get_section_info(drug_source, "how")
            sections.append(how)
            other_uses = self.get_section_info(drug_source, "other-uses")
            sections.append(other_uses)
            result.append(dict(
                name=name,
                url=link,
                sections=sections
            ))
            i += 1

        return result


    def write_as_json(self, data):
        with open("result.json", "w", encoding='utf-8') as f:           #Yeni bir dosya açıyoruz
            f.write(json.dumps(data, indent=2))




if __name__ == '__main__':
    scraper = MedLineScraper()
    data = scraper.scrape_drugs()
    scraper.write_as_json(data)
    #pprint(json.dumps(data))
    #drugs = scraper.find_all_drug_links()
    #print(*scraper.get_categories(), sep="\n")   #A-Z tüm harfleri yazdırma #Sep ile alt alta yazdırma
    #source = scraper.get_source("https://medlineplus.gov/druginfo/drug_Aa.html")
    #print(source)       #Sayfanın html kaynağını verir.
    #print(scraper.get_all_drug_links(source))
    #drugs = scraper.get_drug_links(source)
    #print(len(drugs))
    #print(drugs)


