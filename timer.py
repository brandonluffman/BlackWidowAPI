from timeit import default_timer as timer
import requests
from requests_html import HTMLSession
from requests_html import HTMLSession
from youtube_transcript_api import YouTubeTranscriptApi
import praw
from praw.models import MoreComments
from bs4 import BeautifulSoup


t8 = timer()

entity_links = ['https://www.google.com/search?tbm=shop&hl=en&q=jabra+elite+45h']
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
    
    except requests.exceptions.RequestException as e:
            print(e)

t9 = timer()

print(f'SHOPPINIG CARD LOGIC -------> {t9 - t8}')

'''
def get_cards(links=entity_links,rank=1,entity):
    
'''
