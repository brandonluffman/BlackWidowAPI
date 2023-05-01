from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup
import asyncio
import concurrent.futures
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from timeit import default_timer as timer
from requests_html import HTMLSession
from timeit import default_timer as timer

result_of_query = {
    'cards': []
}

# entities = ['jabra elite 75t', 'bose quietcomfort 45']
# domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
# css_selector_prod_desc =  ".C7Lkve a"
# # entity_links = [(domain + entity.replace(' ', '+'), entity,entities.index(entity)+1,'https://www.google.com' + HTMLSession().get(domain+entity.replace(' ','+')).html.find(css_selector_prod_desc,first=True)) for entity in entities]
# entity_links = [(domain + entity.replace(' ', '+'), entity,entities.index(entity)+1,'https://www.google.com' + HTMLSession().get(domain+entity.replace(' ','+')).html.find(css_selector_prod_desc,first=True).attrs['href']) for entity in entities]

# session_two = HTMLSession()

t10 = timer()

css_selector_prod_desc =  ".C7Lkve a"
domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
entity_links = [(domain + entity.replace(' ', '+'), entity,entities.index(entity)+1,'https://www.google.com' + HTMLSession().get(domain+entity.replace(' ','+')).html.find(css_selector_prod_desc,first=True).attrs['href']) for entity in entities]
# print(entity_links)
async def get_final_card(entity_links):
    url = entity_links[0]
    entity = entity_links[1]
    card_rank = entity_links[2]
    # session = entity_links[3]
    # entity_link_response = session
    # card_link = 'https://www.google.com' + entity_link_response.html.find(".C7Lkve a", first=True).attrs['href']
    try:
        product_desc_response = session.get(entity_links[3])
        
        result = product_desc_response.html.find(".sg-product__dpdp-c", first=True)
        product_rating = result.find(".QKs7ff .uYNZm", first=True).text if result.find(".QKs7ff .uYNZm", first=True) is not None else ''
        product_title = result.find(".YVQvvd .BvQan", first=True).text if result.find(".YVQvvd .BvQan", first=True) else ''
        review_count = int(result.find(".QKs7ff .qIEPib", first=True).text.replace(',','').replace(' reviews','').replace(' review', '')) if result.find(".QKs7ff .qIEPib", first=True) else ''
        prod_img = result.find(".wTvWSc img", first=True).attrs['src'] if result.find(".wTvWSc img", first=True) else 'hello'
        prod_desc = result.find(".Zh8lCd p .sh-ds__full .sh-ds__full-txt", first=True).text if result.find(".Zh8lCd p .sh-ds__full .sh-ds__full-txt", first=True) else ' ---- '
        final_card =  {
            'id': 0,
            'rank': card_rank,
            'entity': entity,
            'product_url': url,
            'product_title': product_title,
            'product_description': prod_desc,
            'product_rating': product_rating,
            'review_count': review_count,
            'product_img': prod_img,
            'all_reviews_link': ' --- ',
            'product_purchasing': '---',
            'mentions': {}
        }
        return final_card
    except:
        final_card = {
            'id': -1,
            'rank': '',
            'entity': '',
            'product_url': '',
            'product_title': '',
            'product_description': '',
            'product_rating': '',
            'review_count': '',
            'product_img': '',
            'all_reviews_link': ' --- ',
            'product_purchasing': '---',
            'mentions': {}
        }

        return final_card
async def get_final_cards(entity_links):
    inputs = entity_links
    tasks = [asyncio.create_task(get_final_card(input)) for input in inputs]
    results = await asyncio.gather(*tasks)
    result_of_query['cards'] = results

await get_final_cards(entity_links=entity_links)

t11 = timer()
print(f'PRODUCT DESCRIPTION -------> {t11 - t10}')

