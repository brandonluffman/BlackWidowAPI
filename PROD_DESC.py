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
import aiohttp
import async_timeout
import functools

# result_of_query = {
#     'cards': []
# }
# t10 = timer()

# headers={
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
#     # "Accept-Language": "en-gb",
#     # "Accept-Encoding": "br,gzip,deflate",
#     # "Accept": "test/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
# }

# css_selector_prod_desc = ".C7Lkve a"
# domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
# entities = ['jabra elite 75t', 'apple airpods max', 'bose quietcomfort 45']
# entity_links = [(domain + entity.replace(' ', '+'), entity,entities.index(entity)+1) for entity in entities]
# # print(entity_links)


# async def get_shopping_card(session,entity_link):
#     css_selector_prod_desc = ".C7Lkve a"
#     session = session
#     response = session.get(entity_link[0])
#     url = response.html.find(css_selector_prod_desc,first=True).attrs['href'] if response.html.find(css_selector_prod_desc,first=True) else ''
#     return url



# async def fetch_url(session, url):
#     async with async_timeout.timeout(1):
#         async with session.get(url) as response:
#             return await response.text()

# async def get_final_card(session, entity_link):
#     url = entity_link[0]
#     entity = entity_link[1]
#     card_rank = entity_link[2]
#     try:
#         html = await fetch_url(session, entity_link[3])
#         soup = BeautifulSoup(html, 'html.parser')  # convert html to BeautifulSoup object
#         result = soup.find('div', class_='sg-product__dpdp-c')
#         prod_img = soup.find('img', class_='TL92Hc').attrs['src'] if soup.find('img', class_='TL92Hc') else 'hello'
#         prod_desc = result.find("span", class_="sh-ds__full-txt").text if result.find("span", class_="sh-ds__full-txt") else ''
#         product_rating = soup.find('div', class_='UzThIf').attrs.get('aria-label') if soup.find('div', class_='UzThIf') else ''
#         product_title = soup.find('span', class_='BvQan').text if soup.find('span', class_='BvQan') else ''
#         review_count = soup.find('span', class_='HiT7Id').text.replace('(', '').replace(')', '') if soup.find('span', class_='HiT7Id') else ''

#         final_card = {
#             'id': 0,
#             'rank': card_rank,
#             'entity': entity,
#             'product_url': url,
#             'product_title': product_title,
#             'product_description': prod_desc,
#             # 'product_rating': product_rating,
#             'review_count': review_count,
#             'product_img': prod_img,
#             'all_reviews_link': '---',
#             'product_purchasing': '---',
#             'mentions': {}
#         }
#         result_of_query['cards'].append(final_card)

#         # print(final_card)
#         return final_card

#     except Exception as e:
#         print(f"An error occurred while processing {entity_link[3]}: {e}")


# async def get_final_cards(entity_links):
#     #### GETTING SHOPPING CARDS
#     entity_links = entity_links

#     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), headers=headers) as session:
#         # Use a session object to avoid making multiple requests to the same domain
#         # Use a connection pool to reuse the existing TCP connections
#         fetch = functools.partial(fetch_url, session)
#         tasks = [asyncio.ensure_future(get_final_card(session, input)) for input in entity_links]
#         results = await asyncio.gather(*tasks, return_exceptions=True)
#         for result, input in zip(results, entity_links):
#             if isinstance(result, Exception):
#                 print(f"Failed to process {input[1]}: {result}")
#             else:
#                 print('Got Him')

# asyncio.run(get_final_cards(entity_links))
# print(f"Final Card ----> {result_of_query}")
# t11 = timer()
# print(f'PRODUCT DESCRIPTION -------> {t11 - t10}')




### Make request to Google for Entity and get Shopping card url

# result_of_query = {
#     'cards': []
# }
# t10 = timer()
# headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}

# domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
# entities = ['jabra elite 75t', 'apple airpods max', 'bose quietcomfort 45']
# entity_links = [domain+ entity for entity in entities]
# print(entity_links)
# print("LINKS ONLY:", entity_links)
# session = HTMLSession()
# card_links = []
# for link in entity_links:
#     try:
#         response = session.get(link)
#         html_content = response.html.html
#         soup = BeautifulSoup(html_content, 'html.parser')
#         card_link = soup.find("a", class_="Lq5OHe").attrs['href']
#         # print(card_link)
#         card_links.append(card_link)

#     except Exception as e:
#         print(e)

# final_card_links = [domain+card for card in card_links]
# t11 = timer()
# print(f'TIME -----> {t11-t10}')
# titles = []
# for card in final_card_links:
#     try:
#         print(card)
#         response = session.get(card)
#         html_content = response.html.html
#         soup = BeautifulSoup(html_content, 'html.parser')
#         title = soup.find('title').text
#         # print(title)
#         titles.append(title)

#     except Exception as e:
#         print(e)

# t12 = timer()

# print(f'TIME -----> {t12-t11}')
# print(f'Titles -----> {titles}')
# print(f'TOTAL TIME -----> {t12-t10}')
from multiprocessing.pool import ThreadPool

# t10 = timer()
# headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}

# domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
# entities = ['jabra elite 75t', 'apple airpods max', 'bose quietcomfort 45']
# entity_links = [domain+ entity for entity in entities]
# print(entity_links)
# print("LINKS ONLY:", entity_links)
# session = HTMLSession()
# card_links = []
# for link in entity_links:
#     try:
#         response = session.get(link)
#         html_content = response.html.html
#         soup = BeautifulSoup(html_content, 'html.parser')
#         card_link = soup.find("a", class_="Lq5OHe").attrs['href']
#         # print(card_link)
#         card_links.append(card_link)

#     except Exception as e:
#         print(e)


