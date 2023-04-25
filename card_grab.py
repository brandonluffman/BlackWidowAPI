from requests_html import HTMLSession
import requests 
import re
import datetime


query = str(input("search: "))
orig_input = query
today = datetime.date.today()
year = today.year
match = re.search(f'{year}', query)

if 'best' not in query.lower() and match is None:
    query = 'best+' + query + '+2023'
elif match is None:
    query = query + '+2023'
elif 'best' not in query.lower():
    query = 'best+' + query
else:
    pass
domain =  "http://google.com/search?q="
# css_identifier_search_correction_div = 'DdVMXd'
css_identifier_search_correction = '.p64x9c'
session = HTMLSession()
response = session.get(domain+query)
correction_p_tag = response.html.find(css_identifier_search_correction, first=True)
corrections = correction_p_tag.find('a.gL9Hy b')
correction_text = " ".join([tag.text for tag in corrections])
query = query.replace(orig_input,correction_text)



entities = ['jabra elite 45h','apple airpods max', 'bose quietcomfort','ksc75','sony wh-1000xm5','sennheiser hd 800 s']
domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
entity_links = [(domain + entity.replace(' ', '+'),entity) for entity in entities]
final_card_links = []
entity_product_results = {}
for item in entity_links:
    # print(url)
    try: 
        url = item[0]
        entity = item[1]
        session = HTMLSession()
        response = session.get(url)
        # print(url, response.status_code)
        css_identifier_results = ".i0X6df"
        css_identifier_link = "span a"
        css_identifier_test_2 = ".Ldx8hd a span"
        css_product_reviews = ".QIrs8"
        css_product_title = "span.C7Lkve div.EI11Pd h3.tAxDx"
        # product_results = response.html.find(css_identifier_results)
        product_results = [item for item in response.html.find(css_identifier_results) if (item.find(css_product_title, first=True) and all(elem in item.find(css_product_title, first=True).text.lower() for elem in entity.split()))] #cards
        entity_product_results[entity] = [result.find(css_product_title,first=True).text for result in product_results if result.find(css_product_title,first=True)]
   

    except requests.exceptions.RequestException as e:
            print(e)

