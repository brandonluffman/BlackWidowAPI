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
    cursor.execute(f"""SELECT * FROM rankidb.product WHERE id={product_id};""")
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
    header_tags = response.html.find(css_identifier_header_tag)
    if 'Shopping' in [result.text for result in header_tags[:3]]:
        pass
    else:
        return "INVALID PRODUCT QUERY"

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

    # for url in urls:
    #     try:
    #         session = HTMLSession()
    #         response = session.get(url)
    #         # print(url, response.status_code)
    #         css_identifier_result = ".tF2Cxc"
    #         css_identifier_result_youtube = ".dFd2Tb"
    #         css_identifier_result = ".tF2Cxc"
    #         css_identifier_title = "h3"
    #         css_identifier_link = ".yuRUbf a"
    #         css_identifier_link_youtube = '.DhN8Cf a'
    #         css_identifier_text = ".VwiC3b"
    #         css_favicon = '.eqA2re img'

    #         results = response.html.find(css_identifier_result)
    #         youtube_results = response.html.find(css_identifier_result_youtube)

            
    #         if results: 
    #             for result in results[:8]:
    #                 serp_link = result.find(css_identifier_link, first=True).attrs['href'] 
    #                 serp_title = result.find(css_identifier_title, first=True).text
    #                 if result.find(css_favicon):
    #                     serp_favicon = result.find(css_favicon, first=True).attrs['src']
    #                 else:
    #                     serp_favicon = 'NA'
    #                 serp_links.append({'link':serp_link,'title':serp_title,'favicon':serp_favicon})
    #         else:
    #             for youtube_result in youtube_results[:3]:
    #                 serp_link = youtube_result.find(css_identifier_link_youtube, first=True).attrs['href']
    #                 serp_title = result.find(css_identifier_title, first=True).text
    #                 serp_links.append({'link':serp_link,'title':serp_title})

    #     except requests.exceptions.RequestException as e:
    #         print(e)

    session = HTMLSession()
    visited_urls = set()

    try:
        for url in urls:
            if url in visited_urls:
                continue

            try:
                response = session.get(url)
                visited_urls.add(url)

                css_identifier_result = ".tF2Cxc"
                css_identifier_result_youtube = ".dFd2Tb"
                css_identifier_title = "h3"
                css_identifier_link = ".yuRUbf a"
                css_identifier_link_youtube = '.DhN8Cf a'
                css_identifier_text = ".VwiC3b"
                css_favicon = '.eqA2re img'

                results = response.html.find(css_identifier_result)
                youtube_results = response.html.find(css_identifier_result_youtube)

                for result in results[:8]:
                    serp_link = result.find(css_identifier_link, first=True).attrs['href'] 
                    serp_title = result.find(css_identifier_title, first=True).text
                    if result.find(css_favicon):
                        serp_favicon = result.find(css_favicon, first=True).attrs['src']
                    else:
                        serp_favicon = 'NA'
                    serp_links.append({'link':serp_link,'title':serp_title,'favicon':serp_favicon})

                for youtube_result in youtube_results[:3]:
                    serp_link = youtube_result.find(css_identifier_link_youtube, first=True).attrs['href']
                    serp_title = result.find(css_identifier_title, first=True).text
                    serp_links.append({'link':serp_link,'title':serp_title})

            except Exception as e:
                print(f"Error processing URL: {url}")
                print(e)

    finally:
        session.close()

    t1 = timer()
    print(f'FINDING LINK TIME -------> {t1 - t0}')

    t2 = timer()
    for serp_link in serp_links:

        if 'youtube.com' in serp_link['link']:
            API_KEY = 'AIzaSyC3ElvfankD9Hf6ujrk3MUH1WIm_cu87XI'
            VIDEO_ID = serp_link['link'].replace('https://www.youtube.com/watch?v=', '')
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
                
                serp_link['text'] = mod

            except HttpError as e:
                print('An error occurred: %s' % e)
            
            result_of_query['links']['youtube'].append(serp_link)
            # print(transcript[:100])

        elif 'reddit.com' in serp_link['link']:
            reddit_read_only = praw.Reddit(client_id="6ziqexypJDMGiHf8tYfERA",         # your client id
                    client_secret="gBa1uvr2syOEbjxKbD8yzPsPo_fAbA",      # your client secret
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") 
            try:
                submission = reddit_read_only.submission(url=serp_link['link'])
            except:
                continue
            post_comments = []

            for comment in submission.comments[:10]:
                if type(comment) == MoreComments:
                    continue
                elif comment.body == '[removed]' or comment.body == '[deleted]' or comment.body[:6] == "Thanks":
                    pass
                else:
                    post_comments.append(comment.body.replace('\n', '').replace('\r', ''))
            serp_link['comments'] = post_comments
            result_of_query['links']['reddit'].append(serp_link)
            # print(post_comments)

        else:
            try:
                headers = {
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                            "Accept-Language": "en",
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                } 
                r = requests.get(serp_link['link'], headers=headers, timeout=2)
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
                result_of_query['links']['affiliate'].append(serp_link)

            except requests.exceptions.RequestException as err:
                print ("OOps: Something Else",err)
            except requests.exceptions.HTTPError as errh:
                print ("Http Error:",errh)
            except requests.exceptions.ConnectionError as errc:
                print ("Error Connecting:",errc)
            except requests.exceptions.Timeout as errt:
                print ("Timeout Error:",errt)

    t3 = timer()
    print(f'Grabbing Transcripts -------> {t3 - t2}')

    t4 = timer()
            
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
    
    t5 = timer()
    print(f'LOGIC BEFORE MODEL -------> {t5 - t4}')

    t6 = timer()
                
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
    # print("ENTITIES:",entities)

    t7 = timer()

    print(f'MODEL -------> {t7 - t6}')

    t8 = timer()

    # all_ents = [entity for entity in items]
    # entities = ['jabra elite 45h','apple airpods max', 'bose quietcomfort','ksc75','sony wh-1000xm5']
    domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
    entity_links = [(domain + entity.replace(' ', '+'),entity,entities.index(entity)+1) for entity in entities]
    final_card_links = []
    for entity_link in entity_links:
        try: 
            session = HTMLSession()
            response = session.get(entity_link)

            css_identifier_results = ".i0X6df" #card div
            product_results = response.html.find(css_identifier_results)
            output = []
            i = 0
            cards_store_count = []
            card_links = []
            for product_result in product_results[:3]:
                card_link = "span a"
                stores_count = ".Ldx8hd a span"
                # review_count = ".QIrs8"
                # product_review_count = product_result.find(review_count, first=True).text
                product_details_link = 'https://www.google.com' + product_result.find(card_link, first=True).attrs['href']
                card_links.append(product_details_link)
                store_count = product_result.find(stores_count, first=True)
                cards_store_count.append(int(store_count.text) if store_count else 0)
            
            max_card_index = cards_store_count.index(max(cards_store_count))
            print(f"MAX: {cards_store_count.index(max(cards_store_count))}")   
            final_store_link = card_links[max_card_index]
            print(f"MAX LINK: {final_store_link}")   
            final_card_links.append(final_store_link)

        except requests.exceptions.RequestException as e:
                print(e)

    t9 = timer()
    print(f'SHOPPINIG CARD LOGIC -------> {t9 - t8}')

    print(final_card_links)

    t10 = timer()

    # card_urls = [[card['Data'],card['entity'],card['rank']] for card in final_card_links]
    # print(card_urls)
    buying_links = []
    review_links = []
    for url in final_card_links:
        try:
            product_url = url[0]
            card_entity = url[1]
            card_rank = url[2]
            session = HTMLSession()
            response = session.get(url[0])
            # print(url, response.status_code)
            css_identifier_result = ".sg-product__dpdp-c"
            css_product_img = ".wTvWSc img"
            css_product_title = ".YVQvvd .BvQan"
            css_product_description = ".Zh8lCd p .sh-ds__full .sh-ds__full-txt"
            css_product_specs = ".lW5xPd .crbkUb"
            css_product_rating = ".QKs7ff .uYNZm"
            css_all_reviews_link = ".k0e9E a"
            css_product_reviews = "#-9110982622418926094-full"
            css_product_reviews_title = ".XBANlb .P3O8Ne"
            css_product_reviews_rating = ".nMkOOb div"
            css_product_review_count = ".QKs7ff .qIEPib"
            css_product_purchasing = ".kPMwsc"
            css_product_specifications = ".lW5xPd"
            css_buying_link = ".dOwBOc a"


            product_purchasing = ".dOwBOc tbody"
            product_purchase = "a"
            product_desc = "td:nth-of-type(1)"
            product_spec = "td:nth-of-type(2)"

            results = response.html.find(css_identifier_result)
            purchasing = response.html.find(css_product_purchasing)
            specifications = response.html.find(css_product_specifications)

            purchase_links = []
            for purchase in purchasing:
                link = (purchase.find(product_purchase, first=True).text).replace('Opens in a new window', '')
                purchase_links.append(link)

            product_specifications_list = []
            for specification in specifications:
                descs = specification.find(product_desc)
                specs = specification.find(product_spec)
                for spec, desc in zip(specs,descs[1:]):
                    specs_object = {
                        desc.text : spec.text,
                    }
                    product_specifications_list.append(specs_object)

            for result in results:
                reviews_link = 'https://google.com' + result.find(css_all_reviews_link, first=True).attrs['href']  
                buying_link = 'https://google.com' + result.find(css_buying_link, first=True).attrs['href'] if result.find(css_buying_link, first=True).attrs['href'] else ''
                product_title = result.find(css_product_title, first=True).text
                buying_links.append(buying_link)
                review_links.append(reviews_link)
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
                    'product_url': product_url,
                    'entity': card_entity,
                    'product_title' : result.find(css_product_title, first=True).text,
                    'product_description' : prod_desc,
                    'product_rating' : result.find(css_product_rating, first=True).text,
                    'review_count' : int(result.find(css_product_review_count, first=True).text.replace(',','').replace(' reviews','')),
                    'product_img' : prod_img,
                    'product_specs' : product_specifications_list,
                    'all_reviews_link': reviews_link,
                    'product_purchasing' : buying_link,
                    'mentions': {}
                } 

                result_of_query['cards'].append(output)
            
        except requests.exceptions.RequestException as e:
                print(e)

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
            session = HTMLSession()
            response = session.get(url)
            # print(url, response.status_code)

            css_identifier_result = ".sg-product__dpdp-c"
            result = response.html.find(css_identifier_result,first=True)
            rows = result.find("div.kPMwsc a.b5ycib")

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

        except requests.exceptions.RequestException as e:
                print(e)

    t15 = timer()
    print(f'BUYING LINKS -------> {t15 - t14}')

    t16 = timer()


###ONLY NEED SOURCES FOR FIRST 10 ###
    #review_links = ['https://www.google.com/shopping/product/6222956906177139429/reviews?hl=en&q=bose+quietcomfort+45&prds=eto:3668158928628930488_0,pid:3011142393657177064,rate:5,rnum:10,rsk:PC_6093883722684573590&sa=X&ved=0ahUKEwiGjJrjr6D-AhWRFlkFHZ9SCFEQn08IWCgA', 'https://www.google.com/shopping/product/127770160929837065/reviews?hl=en&q=apple+airpods+max&prds=eto:487205171537148384_0,pid:1942015860405678420,rate:5,rnum:10,rsk:PC_7827190084446473420&sa=X&ved=0ahUKEwiUtcXjr6D-AhWSMlkFHeU-DzIQn08ITSgA']
    for url in review_links:
        metrics = {
            'rating_count': {},
            'sentiment': [],
            'reviews': [],
        }
        try:
            import re
            session = HTMLSession()
            response = session.get(url)
            # print(url, response.status_code)

            css_identifier_result = ".z6XoBf"
            results = response.html.find(css_identifier_result)
            reviews = []
            for result in results[:2]:    
                if result.find('.sPPcBf'):
                    source = result.find('.sPPcBf span')[1].text
                else:
                    source = ' ----- '
                
                output = {
                        'source' : source,
                } 
                metrics['reviews'].append(output)
            metrics['review_sources'] = list(set([item['source'] for item in metrics['reviews']]))
            css_identifier_result_two = '.aALHge'
            result_two = response.html.find(css_identifier_result_two)
            i = 5
            outerput = []
            for result in result_two:
                if result.find('.vL3wxf'):
                    rating_count = result.find('.vL3wxf', first=True).text
                    outerput.append(rating_count)

                    i = i - 1
                else:
                    rating_count = 'None'

            for i in range(len(outerput)):
                rating = f'{len(outerput) - i} stars' if len(outerput) - i > 1 else  f'{len(outerput) - i} star'
                review_count = int(outerput[i].replace(',','').replace(' reviews','').replace(' review', ''))
                metrics['rating_count'][rating] = review_count
            # reviews.append(outerput)

            sentimenter = []
            css_identifier_result_three = '.gKLqZc'
            result_three = response.html.find(css_identifier_result_three)
            count = 0
            for result in result_three[1:]:
                count+=1
                if result.find('.QIrs8'):
                    start_word = 'about '
                    end_word = '.'
                    start = 'are '
                    end = '.'
                    sentiment_text = result.find('.QIrs8', first=True).text
                    # print("TEXT", type(sentiment_text))
                    pattern = r"\d+%|\d+"
                    matches = re.findall(pattern, sentiment_text)
                    start_index = sentiment_text.find(start_word)
                    end_index = sentiment_text.find(end_word, start_index)
                    result = sentiment_text[start_index+len(start_word):end_index]
                    starter = sentiment_text.find(start)
                    ender = sentiment_text.find(end, starter)
                    resulter = sentiment_text[starter+len(start):ender]
                    metrics['sentiment'].append({'favor_vote_count':matches[0], 'desc': result, 'favor_rating': matches[1]+' '+resulter})
                    sentimenter.append([matches[0], result, matches[1]+' '+resulter])
                else:
                    sentiment_text = 'None'

            for card in result_of_query['cards']:
                if card['all_reviews_link'] == url:
                    card['review_data'] = metrics
                else:
                    continue
        except requests.exceptions.RequestException as e:
                        print(e)

    t17 = timer()
    print(f'REVIEWS -------> {t17 - t16}')

    t18 = timer()

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
                    json.dumps(card['product_specs']),
                    card['all_reviews_link'],
                    card['product_purchasing'],
                    json.dumps(card['buying_options']),
                    json.dumps(card['review_data']),
                    json.dumps(card['mentions']),
                    0
                )
        cursor.execute(query,values)
        connection.commit()
        card['id'] = cursor.lastrowid

    t19 = timer()
    print(f'CARDS INTO DB -------> {t19 - t18}')

    t20 = timer()


    scraped_data_insert_query = """
                                    INSERT INTO rankidb.query (query,links,cards,request_count) 
                                    VALUES (%s,%s,%s,%s);
                                """
    values = (result_of_query['query'],json.dumps(result_of_query['links']),json.dumps(result_of_query['cards']),1)
    cursor.execute(scraped_data_insert_query,values)
    connection.commit()
    cursor.close()
    t21 = timer()
    print(f'SCRAPED DATA INSERT QUERY -------> {t21 - t20}')
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
