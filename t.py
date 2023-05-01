import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup
from timeit import default_timer as timer

entities = ['jabra elite 75t', 'apple airpods max', 'bose quietcomfort 45','jabra elite 75t', 'apple airpods max', 'bose quietcomfort 45','jabra elite 75t', 'apple airpods max', 'bose quietcomfort 45','jabra elite 85h']
# entities = ['jabra elite 75t']

headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
domain_trunc = 'https://www.google.com'

async def scrape(url):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            body = await resp.text()
            soup = BeautifulSoup(body, 'html.parser')
            card_link = soup.find("a", class_="Lq5OHe").attrs['href']
            # print(card_link)
            return card_link


async def scrape_product(url):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            body = await resp.text()
            # body = body.decode('utf-8')
            soup = BeautifulSoup(body, 'html.parser')
            # title = soup.title
            # print(title)
            # print(product_title)
            # result = soup.find('div', class_='sg-product__dpdp-c')
            prod_img = soup.find('img', class_='TL92Hc').attrs['src'] if soup.find('img', class_='TL92Hc') else 'hello'
            product_rating = soup.find('div', class_='UzThIf').attrs.get('aria-label') if soup.find('div', class_='UzThIf') else ''
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
            return final_card

async def main():
    print('Saving the output of extracted information')
    tasks = []
    for entity in entities:
        url = f'https://www.google.com/search?tbm=shop&hl=en&q={entity}'
        task = asyncio.create_task(scrape(url))
        tasks.append(task)
    card_links = await asyncio.gather(*tasks)
    print(card_links)
    taskers=[]
    shop_cards = [domain_trunc + card for card in card_links]
    print(shop_cards)
    for card in shop_cards:
        task = asyncio.create_task(scrape_product(card))
        taskers.append(task)
    final_cards = await asyncio.gather(*taskers)
    print(final_cards)
    print('done')

t0 = timer()
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
t1 = timer()
timer = t1 - t0
print(f"TIME ----> {timer}")



# print(product_title)
# result = soup.find('div', class_='sg-product__dpdp-c')
# prod_img = soup.find('img', class_='TL92Hc').attrs['src'] if soup.find('img', class_='TL92Hc') else 'hello'
# print(prod_img)

# product_rating = soup.find('div', class_='UzThIf').attrs.get('aria-label') if soup.find('div', class_='UzThIf') else ''
# product_title = soup.find('span', class_='BvQan').text if soup.find('span', class_='BvQan') else ''
# review_count = soup.find('span', class_='HiT7Id').text.replace('(', '').replace(')', '') if soup.find('span', class_='HiT7Id') else ''
# # print(title)
# final_card = {
#     'id': 0,
#     # 'rank': card_rank,
#     # 'entity': entity,
#     'product_url': url,
#     'product_title': product_title,
#     'product_description': prod_desc,
#     # 'product_rating': product_rating,
#     'review_count': review_count,
#     'product_img': prod_img,
#     'all_reviews_link': '---',
#     'product_purchasing': '---',
#     'mentions': {}
# }
# # print(title)   
# return final_card

