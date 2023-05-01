from requests_html import AsyncHTMLSession
import asyncio
from timeit import default_timer as timer
from aiohttp import ClientSession
import aiohttp
# urls = ['https://www.google.com/', 'https://www.facebook.com/', 'https://www.twitter.com/']

# async def fetch(session, url):
#     async with session.get(url) as response:
#         return response

# async def fetch_all(urls):
#     async with AsyncHTMLSession() as session:
#         tasks = []
#         for url in urls:
#             tasks.append(asyncio.ensure_future(fetch(session, url)))
#         responses = await asyncio.gather(*tasks)
#         return responses
    
# loop = asyncio.get_event_loop()
# pages = loop.run_until_complete(fetch_all(urls))
# for page in pages:
#     print(page.url, len(page.text))

result_of_query = {
    'cards': []
}

entities = ['jabra elite 75t', 'bose quietcomfort 45']
domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
entity_links = [(domain + entity.replace(' ', '+'), entity,entities.index(entity)+1) for entity in entities]

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def get_final_card(entity_link, session):
    url = entity_link[0]
    entity = entity_link[1]
    card_rank = entity_link[2]
    
    async with session.get(url) as entity_link_response:
        card_link = 'https://www.google.com' + entity_link_response.html.find(".C7Lkve a", first=True).attrs['href']
    
    async with session.get(card_link) as product_desc_response:
        result = product_desc_response.html.find(".sg-product__dpdp-c", first=True)
        reviews_link = 'https://google.com' + result.find(".k0e9E a", first=True).attrs['href'] if result.find(".k0e9E a", first=True) else ' -- '
        product_rating = result.find(".QKs7ff .uYNZm", first=True).text if result.find(".QKs7ff .uYNZm", first=True) else ''
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
            'all_reviews_link': reviews_link,
            'product_purchasing': '---',
            'mentions': {}
        }
    return final_card

async def get_final_cards(entity_links):
    async with aiohttp.ClientSession() as session:
        inputs = entity_links
        tasks = [asyncio.create_task(get_final_card(input, session)) for input in inputs]
        results = await asyncio.gather(*tasks)
        result_of_query['cards'] = results

t10 = timer()
asyncio.run(get_final_cards(entity_links))
t11 = timer()

print("CARDS",result_of_query['cards'])
print(f"FINAL CARD TIME: {t11 - 10}")