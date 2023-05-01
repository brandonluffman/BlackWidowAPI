from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup

import concurrent.futures
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from timeit import default_timer as timer



from requests_html import HTMLSession
from timeit import default_timer as timer

entities = ['jabra elite 75t', 'bose quietcomfort 45']
domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
entity_links = [(domain + entity.replace(' ', '+'), entity) for entity in entities]

session = HTMLSession()

css_identifier_result = ".sg-product__dpdp-c"
css_product_img = ".wTvWSc img"
css_product_title = ".YVQvvd .BvQan"
css_product_description = ".Zh8lCd p .sh-ds__full .sh-ds__full-txt"
css_product_rating = ".QKs7ff .uYNZm"
css_all_reviews_link = ".k0e9E a"
css_product_review_count = ".QKs7ff .qIEPib"
css_buying_link = ".dOwBOc a"

def generate_product_card(url, entity, rank):
    response = session.get(url)
    card_link = 'https://www.google.com' + response.html.find(".C7Lkve a", first=True).attrs['href']
    product_desc_response = session.get(card_link)
    
    result = product_desc_response.html.find(css_identifier_result, first=True)
    if not result:
        return None
    
    reviews_link = 'https://google.com' + result.find(css_all_reviews_link, first=True).attrs['href'] if result.find(css_all_reviews_link, first=True) else ' -- '
    buying_link = 'https://google.com' + result.find(css_buying_link, first=True).attrs['href'] if result.find(css_buying_link, first=True) and 'http' in result.find(css_buying_link, first=True).attrs['href'] else ''
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

    return {
        'id': 0,
        'rank': rank,
        'entity': entity,
        'product_url': url,
        'product_title': product_title,
        'product_description': prod_desc,
        'product_rating': product_rating,
        'review_count': review_count,
        'product_img': prod_img,
        'all_reviews_link': reviews_link,
        'product_purchasing': buying_link,
        'mentions': {}
    }

def generate_product_cards(entity_links):
    local_entity_links = entity_links[:]
    rank = 1
    for url, entity in local_entity_links:
        card = generate_product_card(url, entity, rank)
        if card is not None:
            yield card
        rank += 1

t10 = timer()
buying_links = []
product_cards = list(generate_product_cards(entity_links))
t11 = timer()
print(f"Elapsed time: {t11 - t10}")