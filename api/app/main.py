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
import time
### For product descriptions ###
import asyncio
from lxml import html
from aiohttp import ClientSession
import aiohttp
import asyncio
import asyncpraw

import concurrent.futures
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import time
from asyncio import run
from queue import Queue





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
    "host": "dbranki.c39jpvgy5agc.us-east-2.rds.amazonaws.com",
    "user": "admin",
    "password": "Phxntom10$!",
    "database": "rankidb",
    'pool_size': 1
}

def init_pool():
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**dbconfig)
    return connection_pool

@app.middleware("http")
def create_pool(request: Request, call_next):
    request.state.connection_pool = init_pool()
    reponse = call_next(request)
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
    cursor.execute(f"""SELECT * FROM rankidb.product WHERE id={product_id};""")
    data = cursor.fetchone()
    # cursor.close()
    if data is None:
        cursor.close()
        return "PRODUCT NOT AVAILABLE"
    else: 
        cursor.execute(f"""UPDATE rankidb.product SET request_count = request_count + 1 WHERE id={product_id}""")
        connection.commit()
        cursor.close()
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
    cursor.execute(f"""SELECT id, entity, product_img FROM rankidb.product WHERE entity LIKE '%{input}%';""")
    product_data = cursor.fetchall()
    cursor.execute(f"""SELECT query FROM rankidb.query WHERE query LIKE '%{input}%'""")
    query_data = list(chain(*cursor.fetchall()))
    cursor.close()
    return product_data + query_data


### TRENDING PRODUCTS ###
@app.get("/blackwidow/trending/products/")
async def get_trending_products(request: Request):
    connection = request.state.connection_pool.get_connection()
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM rankidb.product ORDER BY request_count DESC LIMIT 10")
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
    cursor.execute("SELECT * FROM rankidb.query ORDER BY request_count DESC LIMIT 10")
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

from timeit import default_timer as timer

### BLACKWIDOW ###
@app.post('/blackwidow')
async def blackwidow(query_input: QueryInput, request: Request):
    from timeit import default_timer as timer
    import re
    connection = request.state.connection_pool.get_connection()
    cursor = connection.cursor(buffered=True)
    session = HTMLSession()
    query = query_input.query.lower()

    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "Accept-Language": "en-gb",
        "Accept-Encoding": "br,gzip,deflate",
        "Accept": "test/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    t1 = timer()

    if 'best' not in query:
        query = 'best ' + query

    domain = 'https://www.google.com/search?q='
    response = session.get(domain, params={'q': query}, headers=headers)
    div_element = response.html.find('a.gL9Hy', first=True)
    header_tags = response.html.find('.O3S9Rb')
    first_header_tags = [tag.text for tag in header_tags[:3]]

    if div_element is not None:
        correct_query = div_element.text
        query = correct_query
        print(f'CORRECTED QUERY: {query}')
        if 'Shopping' in first_header_tags:
            print("VALID QUERY")
        else:
            print("INVALID QUERY")
            query = 'INVALID'

    else:
        if 'Shopping' in first_header_tags:
            print("VALID QUERY")
        else:
            print("INVALID QUERY")
            query = 'INVALID'

    cursor.execute(f"""SELECT * FROM rankidb.query WHERE query = '{query}' """)
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
    elif query == 'INVALID':
        return 'INVALID QUERY, PLEASE TRY SOMETHING ELSE'
    else:
        keywords = [word for word in query.replace('best ','').replace(' 2023','').split() if word not in set(stopwords.words('english'))] 
        match_query = """SELECT * FROM rankidb.query WHERE """
        in_condition = "query LIKE "
        conditions = [f"{in_condition}'%{kw}%'" for kw in keywords]
        match_query = match_query + " AND ".join(conditions) + ";" 
        cursor.execute(match_query)
        accurate_match = cursor.fetchone()
        if accurate_match is not None:
            cursor.execute(f"""UPDATE rankidb.query SET request_count = request_count + 1 WHERE query = '{accurate_match[1]}' """)
            connection.commit()
            cursor.close()
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
    domain = "http://google.com/search?q="
    google_query = query
    reddit_query = (query + ' reddit')
    youtube_query = (query + ' youtube') 
    queries = [google_query, reddit_query, youtube_query]
    urls = [domain + query for query in queries]
    serp_links = []

    t2 = timer()
    print(f'BEGINNINNG CHECKING -------> {t2 - t1}')

    serp_links = []
    def fetch_results(url):
        try:
            response = session.get(url)
        except requests.exceptions.RequestException as e:
            print(e)
            return []
        
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
            return [{'link':result.find(css_identifier_link, first=True).attrs['href'],
                    'title':result.find(css_identifier_title, first=True).text,
                    'favicon':result.find(css_favicon, first=True).attrs['src'] if result.find(css_favicon) else 'NA'}
                    for result in results[:8]]
        else:
            return [{'link':youtube_result.find(css_identifier_link_youtube, first=True).attrs['href'],
                    'title':youtube_result.find(css_identifier_title, first=True).text}
                    for youtube_result in youtube_results[:3]]

    # t0 = timer()
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(fetch_results, urls))

    serp_links = [result for sublist in results for result in sublist]
    # print(serp_links)


    t3 = timer()
    print(f'FINDING LINK TIME -------> {t3 - t2}')

    youtube_serps = [serp_link for serp_link in serp_links if 'youtube.com' in serp_link['link']]
    reddit_serps = [serp_link for serp_link in serp_links if 'reddit.com' in serp_link['link']]
    affiliate_serps = [serp_link for serp_link in serp_links if ('reddit.com' not in serp_link['link']) and ('youtube.com' not in serp_link['link'])]
    # reddit_links = [reddit_serp['link'] for reddit_serp in reddit_serps if reddit_serp['link'].count('/') == 8]
    # affiliate_links = [serp_link['link'] for serp_link in serp_links if ('reddit.com' not in serp_link['link']) and ('youtube.com' not in serp_link['link'])]
    # print(reddit_links)
    # print(affiliate_links)


    def add_youtube_data(serp_links):
        links = serp_links
        if len(serp_links) == 0:
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

    t4 = timer()
    print(f'YOUTUBE -------> {t4 - t3}')

    async def get_comments(serp_obj):
        async with asyncpraw.Reddit(client_id="6ziqexypJDMGiHf8tYfERA",
                                    client_secret="gBa1uvr2syOEbjxKbD8yzPsPo_fAbA",
                                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                                    check_for_async=True
        ) as reddit:
            try:
                submission = await reddit.submission(url=serp_obj['link'])
                comments = submission.comments[:10]
                serp_obj['comments'] = [comment.body for comment in comments]
                return serp_obj
            except:
                serp_obj['comments'] = []
                return serp_obj

    async def get_results(reddit_serps):
        inputs = reddit_serps
        tasks = [asyncio.create_task(get_comments(serp_obj)) for serp_obj in inputs]
        results = await asyncio.gather(*tasks)
        result_of_query['links']['reddit'] = results

    await get_results(reddit_serps=reddit_serps)

    t5 = timer()
    print(f'REDDIT -------> {t5 - t4}')

    async def get_affiliate_content(session, serp_obj):
        try:
            async with session.get(serp_obj['link']) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
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
                serp_obj['text'] = final_content
                return serp_obj
        except:
            serp_obj['text'] = ''
            return serp_obj

    async def google_main(affiliate_serps):
        inputs = affiliate_serps
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = [asyncio.create_task(get_affiliate_content(session=session, serp_obj=input)) for input in inputs]
            results = await asyncio.gather(*tasks)
            result_of_query['links']['affiliate'] = results
            # print(results)

    await google_main(affiliate_serps=affiliate_serps)

    t6 = timer()
    print(f'GOOGLE -------> {t6 - t5}')
    print(f'TOTAL TRANSCRIPT TIME -------> {t6 - t3}')
            
    final_text = []
    sources = list(result_of_query['links'].keys())
    for source in sources:
        if source == 'reddit':
            for link in result_of_query['links'][source]:
                # print(link)
                if link:
                    # print(link['comments'])
                    for comment in link['comments']:
                        final_text.append(comment)
                else:
                    continue
        else:
            for link in result_of_query['links'][source]:
                final_text.append(link['text'])
    
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

    t8 = timer()
    print(f'MODEL -------> {t8 - t7}')

    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
    domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
    domain_trunc = 'https://www.google.com'

    async def scrape(url):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                body = await resp.text()
                soup = BeautifulSoup(body, 'html.parser')
                card_link = soup.find("a", class_="Lq5OHe").attrs['href'] if soup.find("a", class_="Lq5OHe") else ''
                return card_link


    async def scrape_product(url):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                body = await resp.text()
                soup = BeautifulSoup(body, 'html.parser')
                img_div = soup.find('div', class_='Xkiaqc') if soup.find('div', class_='Xkiaqc') else ''
                prod_img = img_div.find_all('img')[0].attrs['src'] if img_div.find('img') else 'hello'
                product_rating = soup.find('div', class_='uYNZm').text if soup.find('div', class_='uYNZm') else ''
                product_title = soup.find('span', class_='BvQan').text if soup.find('span', class_='BvQan') else ''
                review_count = soup.find('span', class_='HiT7Id').text.replace('(', '').replace(')', '') if soup.find('span', class_='HiT7Id') else ''
                prod_desc = soup.find("span", class_="sh-ds__full-txt").text if soup.find("span", class_="sh-ds__full-txt") else ''
                final_card = {
                    'id': 0,
                    # 'rank': card_rank,
                    # 'entity': entity,
                    'product_url': url,
                    'product_title': product_title,
                    'product_description': prod_desc,
                    'product_rating': product_rating,
                    'review_count': review_count,
                    'product_img': prod_img,
                    'all_reviews_link': '---',
                    'product_purchasing': '---',
                    'mentions': {}
                } 
                # print(final_card)
                return final_card

    async def prod_desc_main():
        print('Saving the output of extracted information')
        tasks = []
        for entity in entities:
            url = f'https://www.google.com/search?tbm=shop&hl=en&q={entity}'
            task = asyncio.create_task(scrape(url))
            tasks.append(task)
        card_links = await asyncio.gather(*tasks)
        # print(card_links)
        taskers=[]
        shop_cards = [domain_trunc + card for card in card_links]
        # print(shop_cards)
        for card in shop_cards:
            task = asyncio.create_task(scrape_product(card))
            taskers.append(task)
        final_cards = await asyncio.gather(*taskers)
        result_of_query['cards'] = final_cards
        for card, entity in zip(result_of_query['cards'],entities):
            card['entity'] = entity
            card['rank'] = entities.index(entity)+1
        # print(final_cards)
        print('done')

    await prod_desc_main()


    t9 = timer()
    print(f'PRODUCT DESCRIPTION -------> {t9 - t8}')
    
    for card in result_of_query['cards']:
        reddit_mentions = [{'link':item['link'], 'favicon': item['favicon']} for item in result_of_query['links']['reddit'] if any(card['entity'] in comment for comment in item['comments'])]
        affiliate_mentions = [{'link':item['link'], 'favicon': item['favicon']} for item in result_of_query['links']['affiliate'] if card['entity'] in item['text']]
        youtube_mentions = [{'link':item['link']} for item in result_of_query['links']['youtube'] if card['entity'] in item['text']]
        card['mentions']['reddit'] = reddit_mentions
        card['mentions']['affiliate'] = affiliate_mentions
        card['mentions']['youtube'] = youtube_mentions
    
    t10 = timer()
    print(f'MENTIONS -------> {t10 - t9}')

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
                    # card['all_reviews_link'],
                    '',
                    '',
                    # card['product_purchasing'],
                    # json.dumps(card['buying_options']),
                    "[]",
                    "[]",
                    # json.dumps(card['review_data']),
                    json.dumps(card['mentions']),
                    0
                )
        cursor.execute(query,values)
        connection.commit()
        card['id'] = cursor.lastrowid

    t11 = timer()
    print(f'CARDS INTO DB -------> {t11 - t10}')

    scraped_data_insert_query = """
                                    INSERT INTO rankidb.query (query,links,cards,request_count) 
                                    VALUES (%s,%s,%s,%s);
                                """
    values = (result_of_query['query'],json.dumps(result_of_query['links']),json.dumps(result_of_query['cards']),1)
    cursor.execute(scraped_data_insert_query,values)
    connection.commit()
    cursor.close()
    t12 = timer()
    print(f'SCRAPED DATA INSERT QUERY -------> {t12 - t11}')
    print(f'TOTAL TIME -------> {t12 - t1}')
    return result_of_query
