from fastapi import FastAPI, Depends, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import json 
import spacy
import requests
from bs4 import BeautifulSoup
import re
import datetime
from requests_html import HTMLSession
from youtube_transcript_api import YouTubeTranscriptApi
import praw
from praw.models import MoreComments
from tld import get_tld, get_fld
from collections import Counter
from pydantic import BaseModel
import mysql.connector.pooling
import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import mysql.connector
from itertools import chain
from urllib.parse import urlparse
import nltk
from nltk.corpus import stopwords
from timeit import default_timer as timer
import time
### For product descriptions ###
import asyncio
from lxml import html
from aiohttp import ClientSession
import aiohttp

import concurrent.futures
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from concurrent.futures import ThreadPoolExecutor
from functools import partial
import time




### CONFIGURATIONS ###
app = FastAPI()
nlp = spacy.load('./output/model-last')
nltk.download('stopwords')
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryInput(BaseModel):
    query: str

dbconfig = {
    "host": "rankidb.c39jpvgy5agc.us-east-2.rds.amazonaws.com",
    "user": "admin",
    "password": "Phxntom10$!",
    "database": "rankidb",
    'pool_size': 1
}

def init_pool():
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**dbconfig)
    return connection_pool

@app.middleware("http")
async def create_pool(request: Request, call_next):
    request.state.connection_pool = init_pool()
    reponse = await call_next(request)
    # request.state.connection_pool.close()
    return reponse

def get_models():
    output_path = os.getcwd() + '/output'
    models = {
        'product_ner': spacy.load(output_path+'/model-last')
    }
    return models


### PRODUCT SEARCH ###

@app.get('/blackwidow/products/product/{product_id}')
async def get_products(product_id: int, request: Request):
    connection = request.state.connection_pool.get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute(f"""SELECT * FROM rankidb.product_test WHERE id={product_id};""")
    data = cursor.fetchone()
    cursor.close()
    if data is None:
        return "PRODUCT NOT AVAILABLE"
    else: 
        return {
            "id": data[0],
            "url": data[1],
            "entity": data[2],
            "product_title": data[3],
            "product_description": data[4],
            "product_rating": data[5],
            "review_count": data[6],
            "product_img": data[7],
            "product_specs": json.loads(data[8]),
            "all_reviews_link": data[9],
            "buying_link": data[10],
            "buying_options": json.loads(data[11]),
            "reviews": json.loads(data[12]),
            "mentions": json.loads(data[13]),
            "request_count": data[14]
        }


### QUERY SEARCH ###
@app.get('/blackwidow/products/{input}')
async def get_products(input: str,request: Request):
    connection = request.state.connection_pool.get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute(f"""SELECT id, entity, product_img FROM rankidb.product_test WHERE entity LIKE '%{input}%';""")
    product_data = cursor.fetchall()
    cursor.execute(f"""SELECT query FROM rankidb.query_test WHERE query LIKE '%{input}%'""")
    query_data = list(chain(*cursor.fetchall()))
    cursor.close()
    return product_data + query_data


### TRENDING PRODUCTS ###
@app.get("/blackwidow/trending/products/")
async def get_trending_products(request: Request):
    connection = request.state.connection_pool.get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM rankidb.product ORDER BY request_count DESC")
    data = cursor.fetchall()
    cursor.close()
    order = []
    for row in data:
        structure = {
            "request_count": row[14],
            "id": row[0],
            "url": row[1],
            "entity": row[2],
            "product_title": row[3],
            "product_description": row[4],
            "product_rating": row[5],
            "review_count": row[6],
            "product_img": row[7],
            "product_specs": json.loads(row[8]),
            "all_reviews_link": row[9],
            "buying_link": row[10],
            "buying_options": json.loads(row[11]),
            "reviews": json.loads(row[12]),
            "mentions": json.loads(row[13]),
        }
        order.append(structure)
    return order

### TRENDINNG SEARCHES ###

@app.get("/blackwidow/trending/searches/")
async def get_trending_products(request: Request):
    connection = request.state.connection_pool.get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM rankidb.query ORDER BY request_count DESC")
    data = cursor.fetchall()
    cursor.close()
    order = []
    for row in data:
        structure = {
                "request_count": row[4],
                "query": row[1],
                "links": json.loads(row[2]),
                "cards": json.loads(row[3])  
            }
        order.append(structure)
    return order

### BLACKWIDOW ###
@app.post('/blackwidow')
async def blackwidow(query_input: QueryInput, request: Request):
    t100 = timer()
    connection = request.state.connection_pool.get_connection()
    cursor = connection.cursor(buffered=True)
    import re

    query = query_input.query
   
    today = datetime.date.today()
    year = today.year
    match = re.search(f'{year}', query)
    
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "Accept-Language": "en-gb",
        "Accept-Encoding": "br,gzip,deflate",
        "Accept": "test/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    if 'best' not in query.lower() and match is None:
        query = 'best ' + query
    elif match is None:
        query = query
    elif 'best' not in query.lower():
        query = 'best ' + query
    else:
        pass
    
    # css_identifier_search_correction = '.p64x9c'
    # if response.html.find(css_identifier_search_correction, first=True) is not None:
    #     correction_p_tag = response.html.find(css_identifier_search_correction, first=True)
    #     corrections = correction_p_tag.find('a.gL9Hy', first=True)
    #     correction_text = corrections.text
    #     # print('Original Input:', query)
    #     query = correction_text
    #     # print("Correction:", query)

        
    cursor.execute(f"""SELECT * FROM rankidb.query WHERE query = '{query}';""")
    exact_match = cursor.fetchone()
    if exact_match is not None:
        cursor.execute(f"""UPDATE rankidb.query SET request_count = request_count + 1 WHERE query = '{query}' """)
        connection.commit()
        cursor.close()
        return {
                "query": exact_match[1],
                "links": json.loads(exact_match[2]),
                "cards": json.loads(exact_match[3])      
            }    
    else:
        keywords = [word for word in query.replace('best ','').replace(' 2023','').split() if word not in set(stopwords.words('english'))] 
        # print("KEYWORDS:",keywords)
        match_query = """SELECT * FROM rankidb.query WHERE """
        in_condition = "query LIKE "
        # for i in range(len(keywords)):
        #     if i == len(keywords) - 1:
        #         match_query = match_query + in_condition + f"'%{keywords[i]}%';"
        #     else:
        #         match_query = match_query + in_condition + f"'%{keywords[i]}%' AND "


        ### CODE TO MAKE ABOVE MORE EFFICIENT ###
        conditions = [f"{in_condition}'%{kw}%'" for kw in keywords]
        match_query = match_query + " AND ".join(conditions) + ";" 




        # print(match_query)
        cursor.execute(match_query)
        accurate_match = cursor.fetchone()
        if accurate_match is not None:
            return {
                "query": accurate_match[1],
                "links": json.loads(accurate_match[2]),
                "cards": json.loads(accurate_match[3])      
            }
        else:
            pass    
        result_of_query = {
            'query' : query,
            'links' : {
                'affiliate': [],
                'reddit': [],
                'youtube': [],
            },
            'cards': [],
        }

    domain =  "http://google.com/search?q="
    css_identifier_header_tag = '.O3S9Rb'
    session = HTMLSession()
    url = domain+query
    response = session.get(url)
    # header_tags = response.html.find(css_identifier_header_tag)
    # if 'Shopping' in [result.text for result in header_tags[:3]]:
    #     pass
    # else:
    #     return "INVALID PRODUCT QUERY"

    remove = re.sub('(\A|[^0-9])([0-9]{4,6})([^0-9]|$)', '', query)
    domain = "http://google.com/search?q="
    google_query = query
    reddit_query = (remove + '+reddit')
    youtube_query = (query + '+youtube') 
    queries = [google_query, reddit_query, youtube_query]
    urls = [domain + query for query in queries]
    serp_links = []

    t101 = timer()

    print(f'BEGINNINNG CHECKING -------> {t101 - t100}')

    t0 = timer()



    serp_links = []

    for url in urls:
        try:
            response = session.get(url)
        except requests.exceptions.RequestException as e:
            print(e)
            continue
        
        css_identifier_result = ".tF2Cxc"
        css_identifier_result_youtube = ".dFd2Tb"
        css_identifier_title = "h3"
        css_identifier_link = ".yuRUbf a"
        css_identifier_link_youtube = '.DhN8Cf a'
        css_identifier_text = ".VwiC3b"
        css_favicon = '.eqA2re img'

        results = response.html.find(css_identifier_result)
        youtube_results = response.html.find(css_identifier_result_youtube)

        if results: 
            serp_links += [{'link':result.find(css_identifier_link, first=True).attrs['href'],
                            'title':result.find(css_identifier_title, first=True).text,
                            'favicon':result.find(css_favicon, first=True).attrs['src'] if result.find(css_favicon) else 'NA'}
                        for result in results[:8]]
        else:
            serp_links += [{'link':youtube_result.find(css_identifier_link_youtube, first=True).attrs['href'],
                            'title':youtube_result.find(css_identifier_title, first=True).text}
                        for youtube_result in youtube_results[:3]]

    t1 = timer()
    print(f'FINDING LINK TIME -------> {t1 - t0}')

    t2 = timer()

    youtube_serps = [serp_link for serp_link in serp_links if 'youtube.com' in serp_link['link']]
    reddit_serps = [serp_link for serp_link in serp_links if 'reddit.com' in serp_link['link']]
    affiliate_serps = [serp_link for serp_link in serp_links if ('reddit.com' not in serp_link['link']) and ('youtube.com' not in serp_link['link'])]


    def add_youtube_data(serp_links):
        links = serp_links
        if len(serp_links) == 0:
            # print("YOUTUBE:", result_of_query['youtube'])
            pass
        else:
            serp_link_data = links[0]
            API_KEY = 'AIzaSyC3ElvfankD9Hf6ujrk3MUH1WIm_cu87XI'
            VIDEO_ID = serp_link_data['link'].replace('https://www.youtube.com/watch?v=', '')
            youtube = build('youtube', 'v3', developerKey=API_KEY)

            try:
                response = youtube.videos().list(
                    part='snippet',
                    id=VIDEO_ID
                ).execute()

                if response['items']:
                    description = response['items'][0]['snippet']['description']
                else:
                    description = 'Nothing found'

                disclaimer = 'disclaimer'
                desc = description.replace('\n', '. ')
                regex_pattern = r'http\S+|https\S+|#\w+|\d{1,2}:\d{2}|[^a-zA-Z0-9\s]+' # Matches timestamps, URLs, and hashtags
                new_string = re.sub(regex_pattern, '', desc)
                modified_string = re.sub(r'\s{2,}', '. ', new_string)
                try:
                    mod = modified_string[:modified_string.index(disclaimer)]
                except:
                    mod = modified_string
                
                serp_link_data['text'] = mod

            except HttpError as e:
                print('An error occurred: %s' % e)
            
            result_of_query['links']['youtube'].append(serp_link_data)
            return add_youtube_data(links[1:])

    add_youtube_data(youtube_serps)

    t3 = timer()
    print(f'YOUTUBE RECURSIVE MOTHERFUCKERRRRRR -------> {t3 - t2}')

    # def add_reddit_data(serp_links):
    #     reddit_read_only = praw.Reddit(client_id="6ziqexypJDMGiHf8tYfERA",         # your client id
    #                         client_secret="gBa1uvr2syOEbjxKbD8yzPsPo_fAbA",      # your client secret
    #                         user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") 
        
    #     for serp_link_data in serp_links:
    #         try:
    #             submission = reddit_read_only.submission(url=serp_link_data['link'])
    #         except:
    #             continue
            
    #         post_comments = []
    #         for comment in submission.comments:
    #             if isinstance(comment, MoreComments):
    #                 continue
    #             if comment.body in ('[removed]', '[deleted]') or comment.body.startswith('Thanks'):
    #                 continue
    #             post_comments.append(comment.body.replace('\n', '').replace('\r', ''))
    #             if len(post_comments) == 10:
    #                 break
            
    #         serp_link_data['comments'] = post_comments
    #         # print(serp_link_data)
    #         result_of_query['links']['reddit'].append(serp_link_data)

    # add_reddit_data(reddit_serps)


    # print("REDDIT", add_reddit_data(reddit_serps))

    t4 = timer()
    print(f'reddit RECURSIVE MOTHERFUCKERRRRRR -------> {t4 - t3}')


    def add_affiliate_data(serp_links):
        session = requests.Session()
        retries = Retry(total=1, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504 ])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        def process_link(serp_link):
            try:
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                }
                r = session.get(serp_link['link'], headers=headers, timeout=1)
                r.raise_for_status()

                soup = BeautifulSoup(r.text, 'html.parser')
                affiliate_content = []
                best = 'best'
                for heading in soup.find_all(["h2", "h3"]):
                    extract = heading.text.strip()
                    if len(extract) > 10 and len(extract) < 200 and extract[-1] != '?' and best not in extract:
                        affiliate_content.append(heading.text.strip().replace('\n', ''))
                    else:
                        pass

                lister = []

                for sentence in affiliate_content:
                    if sentence[-1] != '.' and sentence[-1] != '!' and sentence[-1] != '?':
                        new_sentence = sentence + '.'
                        lister.append(new_sentence)
                    else:
                        new_sentence = sentence
                        lister.append(new_sentence)

                final_content = " ".join(lister)
                serp_link['text'] = final_content
                # print(serp_link)
                result_of_query['links']['affiliate'].append(serp_link)

            except requests.exceptions.RequestException as err:
                print ("OOps: Something Else",err)
            except requests.exceptions.HTTPError as errh:
                print ("Http Error:",errh)
            except requests.exceptions.ConnectionError as errc:
                print ("Error Connecting:",errc)
            except requests.exceptions.Timeout as errt:
                print ("Timeout Error:",errt)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for serp_link in serp_links:
                futures.append(executor.submit(process_link, serp_link))
            concurrent.futures.wait(futures)

    add_affiliate_data(affiliate_serps)


    t5 = timer()
    print(f'GOOGLE RECURSIVE FUNCTION -------> {t5 - t4}')
    print(f'TOTAL TRANSCRIPT TIME -------> {t5 - t0}')

    t6 = timer()
            
    final_text = []
    sources = list(result_of_query['links'].keys())
    for source in sources:
        if source == 'reddit':
            for link in result_of_query['links'][source]:
                for comment in link['comments']:
                    final_text.append(comment)
        else:
            for link in result_of_query['links'][source]:
                final_text.append(link['text'])
    
    # print(final_text)
    
    t7 = timer()
    print(f'LOGIC BEFORE MODEL -------> {t7 - t6}')

                
    model_text = " ".join(final_text)
    json_object = json.dumps(model_text)
    doc = nlp(json_object)
    # model = get_models()['product_ner']
    # doc = model(json_object)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    cleaned_items = []
    items = [ent.text for ent in doc.ents if ent.label_ == "PRODUCT"]
    for item in items:
        cleaner_item = re.sub(r'\s{2,}|[^\w&\s]', '', item)
        cleaned_item = cleaner_item
        cleaned_items.append(cleaned_item)

    ello = Counter(cleaned_items).most_common(10)
    ellos = []
    for k,v in ello:
        ellos.append(k)

    entities = [entity for entity in ellos]
    print("ENTITIES:",entities)

    t8 = timer()

    print(f'MODEL -------> {t8 - t7}')

    domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
    entity_links = [(domain + entity.replace(' ', '+'),entity) for entity in entities]
    # print(entity_links)
    t10 = timer()
    session = HTMLSession()
    buying_links = []
    def generate_product_cards(entity_links,rank=1):
        local_entity_links = entity_links
        if len(local_entity_links) == 0:
            pass
        else:
            url = local_entity_links[0][0]
            entity = local_entity_links[0][1]
            response = session.get(url)
            card_link = 'https://www.google.com' + response.html.find(".C7Lkve a", first=True).attrs['href']
            card_rank = rank
            product_desc_response = session.get(card_link)
            css_identifier_result = ".sg-product__dpdp-c"
            css_product_img = ".wTvWSc img"
            css_product_title = ".YVQvvd .BvQan"
            css_product_description = ".Zh8lCd p .sh-ds__full .sh-ds__full-txt"
            css_product_rating = ".QKs7ff .uYNZm"
            css_all_reviews_link = ".k0e9E a"
            css_product_review_count = ".QKs7ff .qIEPib"
            css_buying_link = ".dOwBOc a"
            results = product_desc_response.html.find(css_identifier_result)
            def add_results(lis):
                if len(lis) == 0:
                    pass
                else:
                    result = lis[0]
                    reviews_link = 'https://google.com' + result.find(css_all_reviews_link, first=True).attrs['href'] if result.find(css_all_reviews_link, first=True) else ' -- '
                    buying_link = 'https://google.com' + result.find(css_buying_link, first=True).attrs['href'] if result.find(css_buying_link, first=True).attrs['href'] else ''
                    product_rating = result.find(css_product_rating, first=True).text if result.find(css_product_rating, first=True) else ''
                    product_title = result.find(css_product_title, first=True).text if result.find(css_product_title, first=True) else ''
                    review_count = int(result.find(css_product_review_count, first=True).text.replace(',','').replace(' reviews','').replace(' review', '')) if result.find(css_product_review_count, first=True) else ''

                    buying_links.append(buying_link)
                    
                    if result.find(css_product_img, first=True):
                        prod_img = result.find(css_product_img, first=True).attrs['src']
                    else:
                        prod_img = 'hello'
                    if result.find(css_product_description, first=True):
                        prod_desc = result.find(css_product_description, first=True).text
                    else:
                        prod_desc = ' ---- '
                        
                    output = {
                        'id': 0,
                        'rank': card_rank,
                        'entity': entity,
                        'product_url': url,
                        'product_title' : product_title,
                        'product_description' : prod_desc,
                        'product_rating' : product_rating,
                        'review_count' : review_count,
                        'product_img' : prod_img,
                        # 'product_specs' : product_specifications_list,
                        'all_reviews_link': reviews_link,
                        'product_purchasing' : buying_link,
                        'mentions': {}
                    } 
                    result_of_query['cards'].append(output)
                    return add_results(lis[1:])
            add_results(results)
            return generate_product_cards(entity_links=local_entity_links[1:],rank=card_rank+1)
    generate_product_cards(entity_links)


    t11 = timer()
    print(f'PRODUCT DESCRIPTION -------> {t11 - t10}')
    
    t12 = timer()
    
    for card in result_of_query['cards']:
        reddit_mentions = [{'link':item['link'], 'favicon': item['favicon']} for item in result_of_query['links']['reddit'] if any(card['entity'] in comment for comment in item['comments'])]
        affiliate_mentions = [{'link':item['link'], 'favicon': item['favicon']} for item in result_of_query['links']['affiliate'] if card['entity'] in item['text']]
        youtube_mentions = [{'link':item['link']} for item in result_of_query['links']['youtube'] if card['entity'] in item['text']]
        card['mentions']['reddit'] = reddit_mentions
        card['mentions']['affiliate'] = affiliate_mentions
        card['mentions']['youtube'] = youtube_mentions
    
    t13 = timer()
    print(f'MENTIONS -------> {t13 - t12}')

    t14 = timer()

    # buying_links = ['https://google.com/shopping/product/6222956906177139429/offers?hl=en&q=bose+quietcomfort+45&prds=eto:3668158928628930488_0,pid:3011142393657177064,rsk:PC_6093883722684573590,scoring:p&sa=X&ved=0ahUKEwjw2p6YsaD-AhWIFlkFHcQDCqkQtKsGCHQ', 'https://google.com/shopping/product/127770160929837065/offers?hl=en&q=apple+airpods+max&prds=eto:487205171537148384_0,pid:1942015860405678420,rsk:PC_7827190084446473420,scoring:p&sa=X&ved=0ahUKEwi1htCYsaD-AhWHGVkFHWXtARsQtKsGCGw']

    for url in buying_links:
        try:
            affiliate_domains = []
            # session = HTMLSession()
            response = session.get(url)
            # print(url, response.status_code)

            css_identifier_result = ".sg-product__dpdp-c"
            result = response.html.find(css_identifier_result,first=True)
            rows = result.find("div.kPMwsc a.b5ycib") if result.find("div.kPMwsc a.b5ycib") else ''
            if rows:
                for row in rows:
                    tlder = row.attrs['href'][7:]
                    if tlder[:1] == 'h':
                        res = get_fld(tlder)
                        if res not in affiliate_domains:
                            affiliate_domains.append(res)
                        else:
                            continue
                    else:
                        continue
                for card in result_of_query['cards']:
                    if card['product_purchasing'] == url:
                        card['buying_options'] = affiliate_domains
                    else:
                        continue
            else:
                continue

        except requests.exceptions.RequestException as e:
                print(e)

    t15 = timer()
    print(f'BUYING LINKS -------> {t15 - t14}')

    for card in result_of_query['cards']: 
        query ="""INSERT INTO rankidb.product
                    (
                        product_url,entity,product_title,product_description,
                        product_rating,review_count,product_img,product_specs,
                        all_reviews_link,product_purchasing,buying_options,reviews,mentions,request_count
                    ) 
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);    
                """
        values = (
                    card['product_url'],
                    card['entity'],
                    card['product_title'],
                    # '',
                    card['product_description'],
                    card['product_rating'],
                    card['review_count'],
                    card['product_img'],
                    "[]",
                    # json.dumps(card['product_specs']),
                    card['all_reviews_link'],
                    card['product_purchasing'],
                    json.dumps(card['buying_options']),
                    "[]",
                    # json.dumps(card['review_data']),
                    json.dumps(card['mentions']),
                    0
                )
        cursor.execute(query,values)
        connection.commit()
        card['id'] = cursor.lastrowid

    t17 = timer()
    print(f'CARDS INTO DB -------> {t17 - t15}')



    scraped_data_insert_query = """
                                    INSERT INTO rankidb.query (query,links,cards,request_count) 
                                    VALUES (%s,%s,%s,%s);
                                """
    values = (result_of_query['query'],json.dumps(result_of_query['links']),json.dumps(result_of_query['cards']),1)
    cursor.execute(scraped_data_insert_query,values)
    connection.commit()
    cursor.close()
    t18 = timer()
    print(f'SCRAPED DATA INSERT QUERY -------> {t18 - t17}')
    print(f'TOTAL TIME -------> {t18 - t0}')
    return result_of_query







# # # # if 'youtube.com' in serp_link['link']:
# # # #     # print('Youtube Link')
# # # #     id = serp_link['link'].replace('https://www.youtube.com/watch?v=', '')
# # # #     try:
# # # #         transcript = YouTubeTranscriptApi.get_transcript(id)
# # # #     except:
# # # #         continue
# # # #     text = ''
# # # #     for i in transcript:
# # # #         text = text + i['text'] + ' '
# # # #     transcript = text
# # # #     serp_link['text'] = transcript
