import asyncio
import aiohttp
from lxml import html

import asyncio
import aiohttp

loop = asyncio.get_event_loop()
session = aiohttp.ClientSession()


buying_links = []
review_links = []
results = []

async def fetch(url, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    }
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def scrape_product(session, url):
    product_url = url[0]
    card_entity = url[1]
    card_rank = url[2]

    if product_url in buying_links or product_url in review_links:
        return

    response_text = await fetch(product_url, session)
    tree = html.fromstring(response_text)
    if tree.cssselect('div.k0e9E'):
        # a_tag = tree.cssselect('div.k0e9E > a')[0]
        print('got himmmmm')
    else: 
        print('STPUID AHHHHHH')


    # all_reviews_link = tree.cssselect('.k0e9E a')
    # all_reviews_link = tree.cssselect('.k0e9E a')[0].get('href')
    # buying_link = tree.cssselect('.dOwBOc a')[0].get('href', '') if tree.cssselect('.dOwBOc a') else ''
    # product_title = tree.cssselect('.YVQvvd .BvQan')[0].text.strip()
    # product_description = tree.cssselect('.Zh8lCd p .sh-ds__full .sh-ds__full-txt')[0].text.strip()
    # product_rating = tree.cssselect('.QKs7ff .uYNZm')[0].text.strip()
    # review_count = int(tree.cssselect('.QKs7ff .qIEPib')[0].text.replace(',', '').replace(' reviews', ''))
    # product_img = tree.cssselect('.wTvWSc img')[0].get('src', 'hello')

    # specs_elements = tree.cssselect('.lW5xPd .crbkUb')
    # product_specs = [
    #     {spec.cssselect('td:nth-child(1)')[0].text.strip(): spec.cssselect('td:nth-child(2)')[0].text.strip()}
    #     for spec in specs_elements
    # ]

    output = {
        'id': 0,
        'rank': card_rank,
        'product_url': product_url,
        'entity': card_entity,
        # 'product_title': product_title,
        # 'product_description': product_description,
        # 'product_rating': product_rating,
        # 'review_count': review_count,
        # 'product_img': product_img,
        # 'product_specs': product_specs,
        # 'all_reviews_link': all_reviews_link,
        # 'product_purchasing': buying_link,
        'mentions': {}
    }

    # result_of_query['cards'].append(output)
    results.append(output)
    # if buying_link:
    #     buying_links.append(buying_link)
    # if all_reviews_link:
    #     review_links.append(all_reviews_link)

async def main():
    urls = [
        ('https://www.google.com/shopping/product/3102751619750334019?q=jabra+elite+75t&prds=epd:10805934194357556350,eto:10805934194357556350_0,pid:2555042619034193584,rsk:PC_17376202431123258754&sa=X&ved=0ahUKEwjhjNGyy8_-AhXeD1kFHQCzDvoQ9pwGCBs', 'entity1', 1),
        ('https://www.google.com/shopping/product/5300893910801770327?q=sony+wh1000xm5&prds=epd:11719290707651363774,eto:11719290707651363774_0,pid:10962453275228175446,rsk:PC_11648784580466805463&sa=X&ved=0ahUKEwjA1OTAy8_-AhXuEFkFHf_CC_wQ9pwGCAo', 'entity2', 2),
    ]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(scrape_product(session, url))
            tasks.append(task)
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print(results)





        