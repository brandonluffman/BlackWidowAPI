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
from tld import get_tld
from collections import Counter
from pydantic import BaseModel
import mysql.connector.pooling
import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import mysql.connector


app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("requests.log")
logger.addHandler(handler)

# 


dbconfig = {
    "host": "rankidb.c39jpvgy5agc.us-east-2.rds.amazonaws.com",
    "user": "admin",
    "password": "Phxntom10$!",
    "database": "rankidb"
}
connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_size=20, **dbconfig)



def get_connection():
    return connection_pool.get_connection()

# def get_models():
#     output_path = os.getcwd() + '/output'
#     models = {
#         'product_ner': spacy.load(output_path+'/model-last')
#     }
#     return models

query_counts = {}

@app.post("/query")
async def query(query_type:str):
    global query_counts
    if query_type in query_counts:
        query_counts[query_type] += 1
    else:
        query_counts[query_type] = 1
    
    return {"message": f"{query_type} query received"}

@app.get("/counts")
async def get_counts():
    global query_counts
    return {"query_counts": query_counts}

# @app.middleware("http")
# async def log_requests(request: Request, call_next,connection=get_connection()):
#     response = await call_next(request)
#     # logger.info(f'QUERY: {query}')
#     # data_dict = {k:v for k,v in data.items()}
#     if request.method == 'POST':
#         method = request.method
#         path = request.url.path
#         body = await request.body()
#         body_str = body.decode('utf-8')
#         status_code = response.status_code
        

#         cursor = connection.cursor(buffered=True)
#         cursor.execute("INSERT INTO rankidb.request_logs (method, path, status_code, body) VALUES (%s, %s, %s,%s)", (method, path, status_code,body_str))
#         connection.commit()
#     return response

# @app.get("/blackwidow/common_requests")
# async def get_common_requests(connection=Depends(get_connection)):
#     cursor = connection.cursor(buffered=True)
#     cursor.execute("SELECT method, path, COUNT(*) as count FROM rankidb.request_logs GROUP BY method, path ORDER BY count DESC LIMIT 10")
#     rows = cursor.fetchall()
#     result = [{"method": row[0], "path": row[1], "count": row[2]} for row in rows]
#     return result


# output_path = os.getcwd() + '/output'

# nlp = spacy.load(output_path+'/model-last')
 

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

@app.post('/')
def home():
    return 'hello'

# @app.get('/blackwidow/{entity}')
# async def get_entity(entity: str,connection=Depends(get_connection)):
#     cursor = connection.cursor(buffered=True)
#     cursor.execute(f"""SELECT * FROM product WHERE entity = '{entity}';""")
#     data = cursor.fetchall()
#     return {'data': data}

# @app.get('/blackwidow/products/{product}')
# async def get_products(product: str, connection=Depends(get_connection)):
#     cursor = connection.cursor(buffered=True)
#     cursor.execute(f"""SELECT entity, product_img FROM product WHERE entity LIKE '%{product}%';""")
#     connection.commit()
#     data = cursor.fetchall()
#     return data


@app.get('/blackwidow/products/{id}')
async def get_products(id: int, connection=Depends(get_connection)):
    cursor = connection.cursor(buffered=True)
    cursor.execute(f"""SELECT * FROM product WHERE id={id};""")
    data = cursor.fetchone()
    if data is not None:
        cursor.execute(f"""UPDATE rankidb.product SET request_count = request_count + 1 WHERE id = {id};""")
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
    else:
        return "Product not available"


@app.get("/blackwidow/trending/products/")
async def get_trending_products(connection=Depends(get_connection)):
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM rankidb.product ORDER BY request_count DESC")
    data = cursor.fetchall()
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

@app.get("/blackwidow/trending/searches/")
async def get_trending_products(connection=Depends(get_connection)):
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM rankidb.query ORDER BY request_count DESC")
    data = cursor.fetchall()
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



@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}


@app.post('/blackwidow')
async def blackwidow(query_input: QueryInput, connection=Depends(get_connection)):
    cursor = connection.cursor(buffered=True)
    # return returner

    import re

    query = query_input.query
    orig_input = query
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
        query = 'best+' + query + '+2023'
    elif match is None:
        query = query + '+2023'
    elif 'best' not in query.lower():
        query = 'best+' + query
    else:
        pass
    domain =  "http://google.com/search?q="
    css_identifier_search_correction = '.p64x9c'
    session = HTMLSession()
    response = session.get(domain+query)
    correction_p_tag = response.html.find(css_identifier_search_correction, first=True)
    if correction_p_tag is not None:
        corrections = correction_p_tag.find('a.gL9Hy b')
        correction_text = " ".join([tag.text for tag in corrections])
        query = query.replace(orig_input,correction_text)
        print("Original Input:", orig_input)
        print("Correct Input:", correction_text)

        
   
        
    cursor.execute(f"""SELECT * FROM rankidb.query WHERE query = '{query}';""")
    query_data = cursor.fetchone()
    if query_data is not None:
        cursor.execute(f"""UPDATE rankidb.query SET request_count = request_count + 1 WHERE query = '{query}' """)
        connection.commit()
        cursor.close()
        return {
                "query": query_data[1],
                "links": json.loads(query_data[2]),
                "cards": json.loads(query_data[3])      
            }
        
    else:
        result_of_query = {
            'query' : query,
            'links' : {
                'affiliate': [],
                'reddit': [],
                'youtube': [],
            },
            'cards': [],
        }

  
        remove = re.sub('(\A|[^0-9])([0-9]{4,6})([^0-9]|$)', '', query)
        domain = "http://google.com/search?q="
        google_query = query
        reddit_query = (remove + '+reddit')
        youtube_query = (query + '+youtube') 
        queries = [google_query, reddit_query, youtube_query]
        urls = [domain + query for query in queries]
        serp_links = []
        for url in urls:
            try:
                session = HTMLSession()
                response = session.get(url)
                # print(url, response.status_code)

                
                css_identifier_result = ".tF2Cxc"
                css_identifier_result_youtube = ".dFd2Tb"
                css_identifier_result = ".tF2Cxc"
                css_identifier_title = "h3"
                css_identifier_link = ".yuRUbf a"
                css_identifier_link_youtube = '.DhN8Cf a'
                css_identifier_text = ".VwiC3b"
                css_favicon = '.eqA2re img'

                results = response.html.find(css_identifier_result)
                youtube_results = response.html.find(css_identifier_result_youtube)

                
                if results: 
                    for result in results[:3]:
                        serp_link = result.find(css_identifier_link, first=True).attrs['href'] 
                        serp_title = result.find(css_identifier_title, first=True).text
                        if result.find(css_favicon):
                            serp_favicon = result.find(css_favicon, first=True).attrs['src']
                        else:
                            serp_favicon = ' -- '
                        serp_links.append({'link':serp_link,'title':serp_title,'favicon':serp_favicon})
                else:
                    for youtube_result in youtube_results[:1]:
                        serp_link = youtube_result.find(css_identifier_link_youtube, first=True).attrs['href']
                        serp_title = result.find(css_identifier_title, first=True).text
                        serp_links.append({'link':serp_link,'title':serp_title})

            except requests.exceptions.RequestException as e:
                print(e)

        # print(serp_links)

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
                        mod = modified_string[:modified_string.lower().index(disclaimer)]
                    except:
                        mod = modified_string
                    
                    serp_link['text'] = mod.lower()

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
                        post_comments.append(comment.body.replace('\n', '').replace('\r', '').lower())
                serp_link['comments'] = post_comments
                result_of_query['links']['reddit'].append(serp_link)
                # print(post_comments)

            else:
                headers = {
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                            "Accept-Language": "en",
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                } 
                r = requests.get(serp_link['link'], headers=headers)
                soup = BeautifulSoup(r.text, 'html.parser')
                affiliate_content = []
                best = 'best'
                for heading in soup.find_all(["h2", "h3"]):
                    extract = heading.text.strip()
                    if len(extract) > 10 and len(extract) < 200 and extract[-1] != '?' and best not in extract.lower():
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
                serp_link['text'] = final_content.lower()
                result_of_query['links']['affiliate'].append(serp_link)
        

        # final_text = []
        # sources = list(result_of_query['links'].keys())
        # for source in sources:
        #     if source == 'reddit':
        #         for link in result_of_query['links'][source]:
        #             for comment in link['comments']:
        #                 final_text.append(comment)
        #     else:
        #         for link in result_of_query['links'][source]:
        #             final_text.append(link['text'])
                    
        # model_text = " ".join(final_text).lower()
        # return model_text
        # json_object = json.dumps(model_text)
        # return json_object
      

        # model = get_models()['product_ner']
        # doc = model(json_object)
        # entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
     
        # items = [x.text for x in doc.ents]
        # # print(items)
        # ello = Counter(items).most_common(10)
        # ellos = []
        # for k,v in ello:
        #     # print(k,v)
        #     ellos.append(k)
        
        # print(ellos)

        # docs = []
        # docs.append(doc)
        # entities = [entity for entity in ellos]
    
        # # all_ents = [entity for entity in items]
        # #
        entities = ['jabra elite 45h','apple airpods max', 'bose quietcomfort','susvara.5. ksc75','sony wh-1000xm5','sennheiser hd800 s']
        domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
        entity_links = [domain + entity.replace(' ', '+') for entity in entities]
        final_card_links = []
        for url in entity_links:
            # print(url)
            try: 
                session = HTMLSession()
                response = session.get(url)
                # print(url, response.status_code)
                css_identifier_results = ".i0X6df"
                css_identifier_link = "span a"
                css_identifier_test_2 = ".Ldx8hd a span"
                css_product_reviews = ".QIrs8"
                product_results = response.html.find(css_identifier_results)
                output = []
                link_count = 0
                ### For Loop Below loops through queries to find Shopping Link and Integer Representing Amounnt of Stores that are linked to that product ###
                for product_result in product_results:
                    product_link = 'https://www.google.com' + product_result.find(css_identifier_link, first=True).attrs['href']
                    product_compare = product_result.find(css_identifier_test_2, first=True)
                    product_review_count = product_result.find(css_product_reviews, first=True).text
        
                    if product_compare:
                        product_compare = product_compare.text

                        if product_compare.endswith('+'):
                            product_compare = product_compare[:-1]  

                            if len(product_review_count.split()) > 3:
                                review_num = int(product_review_count.split()[5].replace(',',''))
                            else:
                                review_num = False

                            if link_count < 3 and review_num:
                                cards = {
                                'Data' : product_link, 
                                'Count' : int(product_compare),
                                'Review Count' : review_num,
                                'entity': entities[entity_links.index(url)]
                                }
                                output.append(cards)
                                link_count += 1

                counts = []
                for out in output:
                    data = [out['Count'], out['Review Count']]
                    counts.append(data) 
                # print(counts)

                count_list = []
                for c in counts:
                    count_list.append(c[0])
            
                max_count = max(count_list,default=0)
                max_indexes = [i for i in range(len(count_list)) if count_list[i] == max_count]         
                index_len = len(max_indexes)
                if index_len == 1:
                    max_index = max_indexes[0]

                max_review_count = []
                if index_len > 1:
                    for max_index in max_indexes:
                        max_review_count.append(counts[max_index][1])
                    max_review = max(max_review_count)
                    max_review_index = max_review_count.index(max_review)

                    for count in counts:
                        if max_review in count:
                            max_card = count     
                else:
                    max_card = counts[max_index]

                indexer = counts.index(max_card)
                final_card = output[indexer]
                final_card_links.append(final_card)

            except requests.exceptions.RequestException as e:
                    print(e)



        card_urls = [[card['Data'],card['entity']] for card in final_card_links]
        # print(card_urls)
        buying_links = []
        review_links = []
        for url in card_urls:
            try:
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
                        'product_url': url[0],
                        'entity': url[1],
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

            
      
        for card in result_of_query['cards']:
            reddit_mentions = [{'link':item['link']} for item in result_of_query['links']['reddit'] if any(card['entity'] in comment for comment in item['comments'])]
            affiliate_mentions = [{'link':item['link']} for item in result_of_query['links']['affiliate'] if card['entity'] in item['text']]
            youtube_mentions = [{'link':item['link']} for item in result_of_query['links']['youtube'] if card['entity'] in item['text']]
            card['mentions']['reddit'] = reddit_mentions
            card['mentions']['affiliate'] = affiliate_mentions
            card['mentions']['youtube'] = youtube_mentions
      



        # buying_links = ['https://google.com/shopping/product/6222956906177139429/offers?hl=en&q=bose+quietcomfort+45&prds=eto:3668158928628930488_0,pid:3011142393657177064,rsk:PC_6093883722684573590,scoring:p&sa=X&ved=0ahUKEwjw2p6YsaD-AhWIFlkFHcQDCqkQtKsGCHQ', 'https://google.com/shopping/product/127770160929837065/offers?hl=en&q=apple+airpods+max&prds=eto:487205171537148384_0,pid:1942015860405678420,rsk:PC_7827190084446473420,scoring:p&sa=X&ved=0ahUKEwi1htCYsaD-AhWHGVkFHWXtARsQtKsGCGw']

        for url in buying_links:
            try:
                session = HTMLSession()
                response = session.get(url)
                # print(url, response.status_code)

                css_identifier_result = ".sg-product__dpdp-c"
                result = response.html.find(css_identifier_result,first=True)
                table = result.find("#sh-osd__online-sellers-cont",first=True)
                rows = table.find("tr div.kPMwsc a")
                buying_options = list(set([a_tag.attrs['href'].replace('/url?q=','') for a_tag in rows]))
                # for card in result_of_query['cards']:
                #     if card['product_purchasing'] == url:
                #         print(card['product_purchasing'])
                #         print(url)
                #         card['buying_options'] = buying_options
                #     else:
                #         continue
            
                # print(buying_options[:5])

                hello = []
                for test in buying_options:            
                    if test[0:5] == 'https':
                        hello.append(test)
                    else:
                        continue
#
                resers = []
                for urler in hello:
                    res = get_tld(urler,as_object=True)
                    reser = res.fld
                    resers.append(reser)

                i=0
                newy = []
                iland = []
                for re in resers:
                    if re not in newy:
                        newy.append(re)
                        iland.append(hello[i])
                    else:
                        continue
                    i +=1

                for card in result_of_query['cards']:
                    if card['product_purchasing'] == url:
                        card['buying_options'] = iland
                    else:
                        continue

            except requests.exceptions.RequestException as e:
                    print(e)



        # review_links = ['https://www.google.com/shopping/product/6222956906177139429/reviews?hl=en&q=bose+quietcomfort+45&prds=eto:3668158928628930488_0,pid:3011142393657177064,rate:5,rnum:10,rsk:PC_6093883722684573590&sa=X&ved=0ahUKEwiGjJrjr6D-AhWRFlkFHZ9SCFEQn08IWCgA', 'https://www.google.com/shopping/product/127770160929837065/reviews?hl=en&q=apple+airpods+max&prds=eto:487205171537148384_0,pid:1942015860405678420,rate:5,rnum:10,rsk:PC_7827190084446473420&sa=X&ved=0ahUKEwiUtcXjr6D-AhWSMlkFHeU-DzIQn08ITSgA']
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
                # reviews_link = 'https://google.com' + result.find(css_all_reviews_link, first=True).attrs['href']  
                # title = result.find('.P3O8Ne', first=True).text
                date = result.find('.ff3bE', first=True).text
                if result.find('.g1lvWe div:nth-of-type(2)', first=True):
                    content = result.find('.g1lvWe div:nth-of-type(2)', first=True).text.replace('\xa0Less', '')
                else:
                    content = 'No review found'
                if result.find('.P3O8Ne', first=True) is not None:
                    title = result.find('.P3O8Ne', first=True).text
                else:
                    title = ' ----- '

                if result.find('.UzThIf'):
                    rating = result.find('.UzThIf', first=True).attrs['aria-label']
                else:
                    rating = 0
                
                if result.find('.sPPcBf'):
                    source = result.find('.sPPcBf span')[1].text
                else:
                    source = ' ----- '
                
                output = {
                        # 'review_count' : result.find(css_product_review_count, first=True).text,
                        'review_link': response.url,
                        'title' : title,
                        'rating' : rating,
                        'date' : date,
                        'content' : content[:200],
                        'source' : source,
                } 
                metrics['reviews'].append(output)
            
            css_identifier_result_two = '.aALHge'
            result_two = response.html.find(css_identifier_result_two)
            i = 5
            outerput = []
            for result in result_two:
                if result.find('.vL3wxf'):
                    rating_count = result.find('.vL3wxf', first=True).text
                    # print(rating_count, i)
                    iver = i
                    outerput.append(rating_count)

                    i = i - 1
                else:
                    rating_count = 'None'
            # print("OUTERPUT", outerput)
            for i in range(len(outerput)):
                rating = f'{len(outerput) - i} stars' if len(outerput) - i > 1 else  f'{len(outerput) - i} star'
                review_count = int(outerput[i].replace(',','').replace(' reviews',''))
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
            # print("SENTIMENTER", sentimenter)
            # reviews.append(sentimenter)

            # print(reviews)
            for card in result_of_query['cards']:
                if card['all_reviews_link'] == url:
                    card['review_data'] = metrics
                else:
                    continue
        except requests.exceptions.RequestException as e:
                        print(e)

####
 
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

    scraped_data_insert_query = """
                                    INSERT INTO rankidb.query (query,links,cards,request_count) 
                                    VALUES (%s,%s,%s,%s);
                                """
    values = (result_of_query['query'],json.dumps(result_of_query['links']),json.dumps(result_of_query['cards']),1)
    cursor.execute(scraped_data_insert_query,values)
    connection.commit()
    cursor.close()
    return result_of_query






# # # if 'youtube.com' in serp_link['link']:
# # #     # print('Youtube Link')
# # #     id = serp_link['link'].replace('https://www.youtube.com/watch?v=', '')
# # #     try:
# # #         transcript = YouTubeTranscriptApi.get_transcript(id)
# # #     except:
# # #         continue
# # #     text = ''
# # #     for i in transcript:
# # #         text = text + i['text'] + ' '
# # #     transcript = text
# # #     serp_link['text'] = transcript
