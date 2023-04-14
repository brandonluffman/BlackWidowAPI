from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json 
import spacy
import requests
from bs4 import BeautifulSoup
import re
import datetime
import requests
from requests_html import HTMLSession
from youtube_transcript_api import YouTubeTranscriptApi
import praw
from praw.models import MoreComments
from tld import get_tld
import time
from collections import Counter
from pydantic import BaseModel
from returner import returner
import mysql.connector.pooling

app = FastAPI()
dbconfig = {
    "host": "rankidb.c39jpvgy5agc.us-east-2.rds.amazonaws.com",
    "user": "admin",
    "password": "Phxntom10$!",
    "database": "rankidb"
}
connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_size=10, **dbconfig)

def get_connection():
    return connection_pool.get_connection()
# nlp = spacy.load('./output/model-last')
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

class ProductIdInput(BaseModel):
    id: int

@app.post('/')
def home():
    return 'hello'


@app.post('/blackwidow/product')
async def get_product(id: ProductIdInput, connection=Depends(get_connection)):
    cursor = connection.cursor(buffered=True)
    cursor.execute(f"""SELECT * FROM product WHERE {id};""")
    print(cursor)
    data = cursor.fetchone()
    print(data)
    if data is not None:
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
            "reviews": json.loads(data[12])
        }
    else:
        return "Product not available"



@app.post('/blackwidow')
async def blackwidow(query_input: QueryInput, connection=Depends(get_connection)):
    cursor = connection.cursor(buffered=True)
    # return returner

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
        query = 'best ' + query + ' 2023'
    elif match is None:
        query = query + ' 2023'
    elif 'best' not in query.lower():
        query = 'best ' + query
    else:
        pass
    
    cursor.execute(f"""SELECT * FROM rankidb.query WHERE query = '{query}';""")
    query_data = cursor.fetchone()
    if query_data is not None:
        cursor.close()
        return {
                "query": query_data[1],
                "links": json.loads(query_data[2]),
                "cards": query_data[3]           
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

                results = response.html.find(css_identifier_result)
                youtube_results = response.html.find(css_identifier_result_youtube)

                
                if results: 
                    for result in results[:1]:
                        serp_link = result.find(css_identifier_link, first=True).attrs['href']
                        serp_links.append(serp_link)
                else:
                    for youtube_result in youtube_results[:1]:
                        serp_link = youtube_result.find(css_identifier_link_youtube, first=True).attrs['href']
                        serp_links.append(serp_link)

            except requests.exceptions.RequestException as e:
                print(e)

        # print(serp_links)

        for serp_link in serp_links:

            if 'youtube.com' in serp_link:
                # print('Youtube Link')
                id = serp_link.replace('https://www.youtube.com/watch?v=', '')
                transcript = YouTubeTranscriptApi.get_transcript(id)
                text = ''
                for i in transcript:
                    text = text + i['text'] + ' '
                transcript = text
                result_of_query['links']['youtube'].append({'link': serp_link,'text': transcript})
                # print(transcript[:100])

            elif 'reddit.com' in serp_link:
                reddit_read_only = praw.Reddit(client_id="6ziqexypJDMGiHf8tYfERA",         # your client id
                        client_secret="gBa1uvr2syOEbjxKbD8yzPsPo_fAbA",      # your client secret
                        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") 
                submission = reddit_read_only.submission(url=serp_link)
                    
                post_comments = []

                for comment in submission.comments[:10]:
                    if type(comment) == MoreComments:
                        continue
                    elif comment.body == '[removed]' or comment.body == '[deleted]' or comment.body[:6] == "Thanks":
                        pass
                    else:
                        post_comments.append(comment.body.replace('\n', '').replace('\r', ''))
                result_of_query['links']['reddit'].append({'link':serp_link,'comments':post_comments})
                # print(post_comments)

            else:
                # print('Google Link')
                headers = {
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                            "Accept-Language": "en",
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                } 
                r = requests.get(serp_link, headers=headers)
                soup = BeautifulSoup(r.text, 'html.parser')
                affiliate_content = []
                for heading in soup.find_all(["p"]):
                    if len(heading.text.strip()) > 20:
                        affiliate_content.append(heading.text.strip())
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
                result_of_query['links']['affiliate'].append({'link':serp_link,'text':final_content})



        # model_text = " ".join(final_text)

        # json_object = json.dumps(model_text)
        # print(json_object)


        # doc = nlp(json_object)
        # entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        # items = [x.text for x in doc.ents]
        # Counter(items).most_common(10)
        # # docs = []
        # # docs.append(doc)

        # entities = [entity for entity in items]
        entities = ['apple airpods max', 'bose quietcomfort 45']
        domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
        # entity_links = [domain + entity.replace(' ', '+') for entity in entities[:4]]
        entity_links = [domain + entity.replace(' ', '+') for entity in entities]
        final_card_links = []
        for url in entity_links:
            print(url)
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

                            # print(int(product_review_count.split()[5].replace(',','')))
                            # print(product_review_count.split())

                            if link_count < 3 and len(product_review_count) > 3:
                                cards = {
                                'Data' : product_link, 
                                'Count' : int(product_compare),
                                'Review Count' : int(product_review_count.split()[5].replace(',','')),
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
            
                max_count = max(count_list)
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
        print(card_urls)
        buying_links = []
        review_links = []
        card_counter = 0
        for url in card_urls:
            card_counter+=1
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
                    output = {
                        'id': card_counter,
                        'product_url': url[0],
                        'entity': url[1],
                        'product_title' : result.find(css_product_title, first=True).text,
                        # 'product_description' : result.find(css_product_description, first=True).text,
                        'product_rating' : result.find(css_product_rating, first=True).text,
                        'review_count' : result.find(css_product_review_count, first=True).text,
                        'product_img' : result.find(css_product_img, first=True).attrs['src'],
                        'product_specs' : product_specifications_list,
                        'all_reviews_link': reviews_link,
                        'product_purchasing' : buying_link
                    } 

                    result_of_query['cards'].append(output)
                
            except requests.exceptions.RequestException as e:
                    print(e)



        # buying_links = ['https://google.com/shopping/product/6222956906177139429/offers?hl=en&q=bose+quietcomfort+45&prds=eto:3668158928628930488_0,pid:3011142393657177064,rsk:PC_6093883722684573590,scoring:p&sa=X&ved=0ahUKEwjw2p6YsaD-AhWIFlkFHcQDCqkQtKsGCHQ', 'https://google.com/shopping/product/127770160929837065/offers?hl=en&q=apple+airpods+max&prds=eto:487205171537148384_0,pid:1942015860405678420,rsk:PC_7827190084446473420,scoring:p&sa=X&ved=0ahUKEwi1htCYsaD-AhWHGVkFHWXtARsQtKsGCGw']

        for url in buying_links:
            try:
                session = HTMLSession()
                response = session.get(url)
                print(url, response.status_code)

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
                    print(url)
                    print(card['product_purchasing'])
                    if card['product_purchasing'] == url:
                        card['buying_options'] = iland
                    else:
                        print('Nope')
                        continue

            

            except requests.exceptions.RequestException as e:
                    print(e)



        # review_links = ['https://www.google.com/shopping/product/6222956906177139429/reviews?hl=en&q=bose+quietcomfort+45&prds=eto:3668158928628930488_0,pid:3011142393657177064,rate:5,rnum:10,rsk:PC_6093883722684573590&sa=X&ved=0ahUKEwiGjJrjr6D-AhWRFlkFHZ9SCFEQn08IWCgA', 'https://www.google.com/shopping/product/127770160929837065/reviews?hl=en&q=apple+airpods+max&prds=eto:487205171537148384_0,pid:1942015860405678420,rate:5,rnum:10,rsk:PC_7827190084446473420&sa=X&ved=0ahUKEwiUtcXjr6D-AhWSMlkFHeU-DzIQn08ITSgA']
        for url in review_links:
            try:
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
                    # rating = int(result.find('.UzThIf::attr(aria-label)'))
                    content = result.find('.g1lvWe div:nth-of-type(2)', first=True).text.replace('\xa0Less', '')
                    # source = result.find('.sPPcBf').xpath('normalize-space()')
                    output = {
                            # 'review_count' : result.find(css_product_review_count, first=True).text,
                            'review_link': response.url,
                            # 'title' : title,
                            # 'rating' : rating,
                            'date' : date,
                            'content' : content[:200],
                            # 'source' : source,
                    } 
                    reviews.append(output)
                for card in result_of_query['cards']:
                    if card['all_reviews_link'] == url:
                        card['reviews'] = reviews
                    else:
                        continue

                # CODE BELOW IS FOR GRABBING ALL REVIEWS FOR A PRODUCT

                # next_page = response.css('.sh-fp__pagination-button::attr(data-url)').get()

                # if next_page is not None:
                #     # re-assigns requests.get url to a new page url
                #     next_page_url = 'https://www.google.com' + next_page
                #     yield response.follow(next_page_url, callback=self.parse_reviews)
            

            except requests.exceptions.RequestException as e:
                    print(e)

        for card in result_of_query['cards']:
            query ="""INSERT INTO rankidb.product
                        (
                            product_url,entity,product_title,product_description,
                            product_rating,review_count,product_img,product_specs,
                            all_reviews_link,product_purchasing,buying_options,reviews
                        ) 
                        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);    
                    """
            values = (
                        card['product_url'],
                        card['entity'],
                        card['product_title'],
                        '',
                        # card['product_description'],
                        card['product_rating'],
                        card['review_count'],
                        card['product_img'],
                        json.dumps(card['product_specs']),
                        card['all_reviews_link'],
                        card['product_purchasing'],
                        json.dumps(card['buying_options']),
                        json.dumps(card['reviews']),
                    )
            cursor.execute(query,values)
            connection.commit()
            card['id'] = cursor.lastrowid
    
        scraped_data_insert_query = """
                                            INSERT INTO rankidb.query (query,links,cards) 
                                            VALUES (%s,%s,%s);
                                        """
        values = (result_of_query['query'],json.dumps(result_of_query['links']),json.dumps(result_of_query['cards']))
        cursor.execute(scraped_data_insert_query,values)
        connection.commit()
        cursor.close()
        return result_of_query


