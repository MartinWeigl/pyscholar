import requests
from bs4 import BeautifulSoup
import pandas as pd

N_RESULT = 100

class Scholar():
    def __init__(self):
        self.session = requests.Session() # Start new session
        self.result = None
        self.keyword = None

    def _get_year(self,div):
        tmp = div.find('div',{'class' : 'gs_a'})
        
        if not tmp is None:
            content = tmp.text

            for char in range(0,len(content)):
                if content[char] == '-':
                    out = content[char-5:char-1]
            if not out.isdigit():
                out = 0
            return int(out)
        else:
            return -1

    def _get_author(self,div):
        tmp = div.find('div',{'class' : 'gs_a'})

        if not tmp is None:
            content = tmp.text
            for char in range(0,len(content)):
                if content[char] == '-':
                    out = content[2:char-1]
                    break
            return out
        else:
            return "Unknown"

    def _get_citations(self,content):
        out = 0
        for char in range(0,len(content)):
            if content[char:char+12] == 'Zitiert von:':
                init = char+12                          
                for end in range(init+1,init+7):
                    if content[end] == '<':
                        break
                out = content[init:end]
        return int(out)

    def save(self, path):
        if not self.result is None:
            self.result.to_csv(path, encoding='utf-8') # Change the path
        else:
            print("Nothing to save. Search for something first!")

    def find(self,keyword):
        self.keyword = keyword

        res = { "links":[],"title":[], "citations":[], "year":[], "rank":[0], "author":[]}

        # Get content from 1000 URLs
        for n in range(0, N_RESULT, 10):    
            url = 'https://scholar.google.com/scholar?start='+str(n)+'&q='+keyword.replace(' ','+')
            page = self.session.get(url)
            c = page.content
            
            soup = BeautifulSoup(c, 'html.parser')
            divs = soup.findAll("div", { "class" : "gs_r" })
            
            for div in divs:
                try:
                    res["links"].append(div.find('h3').find('a').get('href'))
                except:
                    res["links"].append('Look manually at: https://scholar.google.com/scholar?start='+str(n)+'&q=non+intrusive+load+monitoring')
                
                try:
                    res["title"].append(div.find('h3').find('a').text)
                except: 
                    res["title"].append('Could not catch title')

                res["citations"].append(self._get_citations(str(div.format_string)))
                res["year"].append(self._get_year(div))
                res["author"].append(self._get_author(div))
                res["rank"].append(res["rank"][-1]+1)

        # Create a dataset and sort by the number of citations
        self.result = pd.DataFrame(zip(res["author"], res["title"], res["citations"], res["year"], res["links"]), index = res["rank"][1:], 
                            columns=['Author', 'Title', 'Citations', 'Year', 'Source'])
        self.result.index.name = 'Rank'

        self.result.sort_values(by='Citations', ascending=False, inplace=True)
        self.result.reset_index(inplace=True)

        return self.result
    
        
            


