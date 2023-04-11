from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json 
import spacy
import requests
from bs4 import BeautifulSoup
import re
import datetime
from parsel import Selector
import requests
from requests_html import HTMLSession


app = FastAPI()
# nlp = spacy.load("en_core_web_sm")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/quotes")
def get_quotes(query:str):

    # today = datetime.date.today()
    # year = today.year
    # match = re.search(f'{year}', query)
    # if 'best' not in query.lower() and match is None:
    #     query = 'best+' + query + '+2023'
    # elif match is None:
    #     query = query + '+2023'
    # elif 'best' not in query.lower():
    #     query = 'best+' + query
    # else:
    #     pass
    # remove = re.sub('(\A|[^0-9])([0-9]{4,6})([^0-9]|$)', '', query)
    # domain = "http://google.com/search?q="
    # google_query = query
    # reddit_query = (remove + '+reddit')
    # youtube_query = (query + '+youtube') 
    # queries = [google_query, reddit_query, youtube_query]
    # urls = [domain + query for query in queries]
    # headers={
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    #     "Accept-Language": "en-gb",
    #     "Accept-Encoding": "br,gzip,deflate",
    #     "Accept": "test/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    # }
    for url in urls:
        html = requests.get(url, headers=headers)
        soup = BeautifulSoup(html.text, 'html.parser')
        print(html.status_code)
        serps = soup.select('.v7W49e')
        serp_results = soup.select('.yuRUbf')
        print(url, len(serp_results))
        print(soup.title.string)
        serp_link_list = []
        # if serp_results:
        #     for serp_result in serp_results[:1]:
        #         serp_link = serp_result.css('a').attrib['href']
        #         serp_title = serp_result.css('h3::text').getall()
        #         serp_favicon = serp_result.css('div.eqA2re img').attrib['src']
        #         serp_link_list.append({
        #             'link': serp_link,
        #             'favicon': serp_favicon,
        #             'title': serp_title
        #         })
        # else:
        #     serp_results = serps.css('div.DhN8Cf')
        #     for serp_result in serp_results[:1]:
        #         serp_link = serp_result.css('a').attrib['href']
        #         serp_title = serp_result.css('h3::text').getall()
        #         serp_favicon = serp_result.css('div.eqA2re img').attrib['src']
        #         serp_link_list.append({
        #             'link': serp_link,
        #             'favicon': serp_favicon,
        #             'title': serp_title
        #         })
        
    

    print(json.dumps(serp_link_list, indent=2, ensure_ascii=False))

    return {'urls': urls, "serps": serp_link_list}























### ----------------------------------------------- ###



# @app.post("/analyze_text")
# async def analyze_text(request: Request):
#     data = await request.json()
#     # text = data.get("text")
#     # doc = nlp(data)
#     # result = {"entities": []}
#     # for ent in doc.ents:
#     #     result["entities"].append({
#     #         "text": ent.text,
#     #         "label": ent.label_
#     #     })
#     return data

#  # def get_product_names(self,response,text):
#     # nlp = spacy.load('./output/model-best')
#     # doc = nlp(text)
#     # items = [x.text for x in doc.ents]
#     # Counter(items).most_common(10)
#     # docs.append(doc)
#     # return 