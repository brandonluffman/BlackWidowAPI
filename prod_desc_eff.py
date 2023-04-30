# import asyncio
# import aiohttp
# from lxml import html

# import asyncio
# import aiohttp

# loop = asyncio.get_event_loop()
# session = aiohttp.ClientSession()


# buying_links = []
# review_links = []
# results = []

# async def fetch(url, session):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
#     }
#     async with session.get(url, headers=headers) as response:
#         return await response.text()

# async def scrape_product(session, url):
#     product_url = url[0]
#     card_entity = url[1]
#     card_rank = url[2]

#     if product_url in buying_links or product_url in review_links:
#         return

#     response_text = await fetch(product_url, session)
#     tree = html.fromstring(response_text)
#     if tree.cssselect('div.k0e9E'):
#         # a_tag = tree.cssselect('div.k0e9E > a')[0]
#         print('got himmmmm')
#     else: 
#         print('STPUID AHHHHHH')


#     # all_reviews_link = tree.cssselect('.k0e9E a')
#     # all_reviews_link = tree.cssselect('.k0e9E a')[0].get('href')
#     # buying_link = tree.cssselect('.dOwBOc a')[0].get('href', '') if tree.cssselect('.dOwBOc a') else ''
#     # product_title = tree.cssselect('.YVQvvd .BvQan')[0].text.strip()
#     # product_description = tree.cssselect('.Zh8lCd p .sh-ds__full .sh-ds__full-txt')[0].text.strip()
#     # product_rating = tree.cssselect('.QKs7ff .uYNZm')[0].text.strip()
#     # review_count = int(tree.cssselect('.QKs7ff .qIEPib')[0].text.replace(',', '').replace(' reviews', ''))
#     # product_img = tree.cssselect('.wTvWSc img')[0].get('src', 'hello')

#     # specs_elements = tree.cssselect('.lW5xPd .crbkUb')
#     # product_specs = [
#     #     {spec.cssselect('td:nth-child(1)')[0].text.strip(): spec.cssselect('td:nth-child(2)')[0].text.strip()}
#     #     for spec in specs_elements
#     # ]

#     output = {
#         'id': 0,
#         'rank': card_rank,
#         'product_url': product_url,
#         'entity': card_entity,
#         # 'product_title': product_title,
#         # 'product_description': product_description,
#         # 'product_rating': product_rating,
#         # 'review_count': review_count,
#         # 'product_img': product_img,
#         # 'product_specs': product_specs,
#         # 'all_reviews_link': all_reviews_link,
#         # 'product_purchasing': buying_link,
#         'mentions': {}
#     }

#     # result_of_query['cards'].append(output)
#     results.append(output)
#     # if buying_link:
#     #     buying_links.append(buying_link)
#     # if all_reviews_link:
#     #     review_links.append(all_reviews_link)

# async def main():
#     urls = [
#         ('https://www.google.com/shopping/product/3102751619750334019?q=jabra+elite+75t&prds=epd:10805934194357556350,eto:10805934194357556350_0,pid:2555042619034193584,rsk:PC_17376202431123258754&sa=X&ved=0ahUKEwjhjNGyy8_-AhXeD1kFHQCzDvoQ9pwGCBs', 'entity1', 1),
#         ('https://www.google.com/shopping/product/5300893910801770327?q=sony+wh1000xm5&prds=epd:11719290707651363774,eto:11719290707651363774_0,pid:10962453275228175446,rsk:PC_11648784580466805463&sa=X&ved=0ahUKEwjA1OTAy8_-AhXuEFkFHf_CC_wQ9pwGCAo', 'entity2', 2),
#     ]

#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         for url in urls:
#             task = asyncio.ensure_future(scrape_product(session, url))
#             tasks.append(task)
#         await asyncio.gather(*tasks)

# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     print(results)
from requests_html import HTMLSession
import requests

result_of_query = {
    'cards': []
}


final_card_links_dummy = ['https://www.google.com/shopping/product/8083131980696868154?hl=en&q=RayBan+Original+Wayfarer+Classic&prds=eto:4806729434153360062_0,pid:17359057298347881509,rsk:PC_14534134275487347451&sa=X&ved=0ahUKEwjCzLrfjND-AhUlmFYBHdzRAe4Q8wIIvw8', 'https://www.google.com/shopping/product/16592106228051659270?hl=en&q=RayBan&prds=eto:8602183769276415766_0,pid:11267882393373467809,rsk:PC_9139480799412115552&sa=X&ved=0ahUKEwj_2I_hjND-AhXFsFYBHeIuCPYQ8wIIlBQ', 'https://www.google.com/shopping/product/3351356171769233288?hl=en&q=RayBan+Classic+Aviator+Sunglasses&prds=eto:8541699967651588134_0,pid:7702670340246951163,rsk:PC_6337342835637812410&sa=X&ved=0ahUKEwjHro7jjND-AhVjsVYBHYE5CCQQ8wIImxI', 'https://www.google.com/shopping/product/3823701926778273554?hl=en&q=RayBan+Jackie+Ohh+Sunglasses&prds=eto:4346264655550129063_0,pid:17405822257623950985,rsk:PC_5911717723158202742&sa=X&ved=0ahUKEwixutHkjND-AhWZRTABHV9ECUUQ8wIItg4', 'https://www.google.com/shopping/product/3620267043176676049?hl=en&q=Rheos+Washouts&prds=eto:10295690693605961526_0,pid:2484879554801207273,rsk:PC_13885104486600695008&sa=X&ved=0ahUKEwj10r_mjND-AhUQglYBHWDsBU0Q8wIIhgw', 'https://www.google.com/shopping/product/1053809831131325891?hl=en&q=RayBan+Aviator+55&prds=eto:6188304368168503074_0,pid:5747887139861646679,rsk:PC_9216433481566426216&sa=X&ved=0ahUKEwjw97fojND-AhVulFYBHRiyA70Q8wIIwxE', 'https://www.google.com/shopping/product/3787808099611271272?hl=en&q=Maui+Jim+Violet+Lake+PolarizedPlus2+Lenses&prds=eto:5554323775077042089_0,pid:1343773781086894182,rsk:PC_7681141503455159664&sa=X&ved=0ahUKEwiTqK7qjND-AhVemlYBHZbGA44Q8wIIxgw', 'https://www.google.com/shopping/product/7688301254536839272?hl=en&q=Zenni+CatEye+Glasses&prds=eto:2883030027962739930_0,pid:12724538805284151767,rsk:PC_7030360374231601219&sa=X&ved=0ahUKEwi56sDrjND-AhU7TTABHbL-CQ4Q8wIIow4', 'https://www.google.com/shopping/product/13139135196343148846?hl=en&q=Dior+59mm+Gradient+Square+Sunglasses&prds=eto:12666222648578566947_0,pid:12289063102666605783,rsk:PC_15785339925938762305&sa=X&ved=0ahUKEwj9ko3tjND-AhXitTEKHV-4B3cQ8wII6g0', 'https://www.google.com/shopping/product/10093436003820434819?hl=en&q=Bottega+Veneta+Minimalist+53MM+Navigator+Sunglasses&prds=eto:6096202118169971997_0,pid:8346225395317538116&sa=X&ved=0ahUKEwjUrLTujND-AhU8mFYBHZXaBnwQ8wIItAs']

buying_links = []
review_links = []
results = []
def add_cards(card_links,rank=1):
    try:
        links = card_links
        if len(links) == 0:
            print("CARDS:",result_of_query['cards'])
            pass
        else:
            url = links[0]
            card_rank = rank
            session = HTMLSession()
            response = session.get(url)
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
            product_purchasing = ".dOwBOc tbody"
            product_purchase = "a"
            product_desc = "td:nth-of-type(1)"
            product_spec = "td:nth-of-type(2)"
            results = response.html.find(css_identifier_result)
            purchasing = response.html.find(css_product_purchasing)
            specifications = response.html.find(css_product_specifications)
            purchase_links = []
            product_specifications_list = []
            def add_purchase_links(lis):
                purchasing_lis = lis
                if len(purchasing_lis) == 0:
                    pass
                else:
                    purchase = purchasing_lis[0]
                    link = (purchase.find(product_purchase, first=True).text).replace('Opens in a new window', '')
                    purchase_links.append(link)
                    return add_purchase_links(purchasing_lis[1:])
            add_purchase_links(purchasing)

            def add_results(lis):
                results_lis = lis
                if len(results_lis) == 0:
                    pass
                else:
                    result = results_lis[0]
                    reviews_link = 'https://google.com' + result.find(css_all_reviews_link, first=True).attrs['href'] if result.find(css_all_reviews_link, first=True) else ' -- '
                    buying_link = 'https://google.com' + result.find(css_buying_link, first=True).attrs['href'] if result.find(css_buying_link, first=True).attrs['href'] else ''
                    product_rating = result.find(css_product_rating, first=True).text if result.find(css_product_rating, first=True) else ''
                    product_title = result.find(css_product_title, first=True).text if result.find(css_product_title, first=True) else ''
                    review_count = int(result.find(css_product_review_count, first=True).text.replace(',','').replace(' reviews','')) if result.find(css_product_review_count, first=True) else ''

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
                        'rank': card_rank,
                        'product_url': url,
                        'product_title' : product_title,
                        'product_description' : prod_desc,
                        'product_rating' : product_rating,
                        'review_count' : review_count,
                        'product_img' : prod_img,
                        # 'product_specs' : product_specifications_list,
                        'all_reviews_link': reviews_link,
                        'product_purchasing' : buying_link,
                        'mentions': {}
                    } 

                    result_of_query['cards'].append(output)
                    return add_results(results_lis[1:])
            add_results(results)
            return add_cards(links[1:],rank=card_rank+1)  
    except requests.exceptions.RequestException as e:
        print(e)
add_cards(card_links=final_card_links_dummy)






"""
for url in final_card_links_dummy:
    try:
        product_url = url[0]
        card_entity = url[1]
        card_rank = url[2]
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
                'rank': card_rank,
                'product_url': product_url,
                'entity': card_entity,
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
"""
        

                    # def add_product_specifications(lis):
            #     prod_spec_lis = lis
            #     if len(prod_spec_lis) == 0:
            #         pass
            #     else:
            #         specification = prod_spec_lis[0]
            #         descs = specification.find(product_desc)[1:]
            #         specs = specification.find(product_spec)
            #         def add_spec_and_desc(descs_list_param,specs_list_param):
            #             local_descs = descs_list_param
            #             local_specs = specs_list_param
            #             print("GROUP:",end=' -->')
            #             print("LOCAL DESCS LENGTH:",len(local_descs), end='--> ')
            #             print("LOCAL SPECS LENGTH:",len(local_specs))
            #             if len(local_descs) == 0 and len(local_specs) == 0:
            #                 pass
            #             else:
            #                 desc = local_descs[0]
            #                 spec = local_specs[0]
            #                 # print("SPEC:",spec,end=' ---> ')
            #                 # print("DESC:",desc)
            #                 specs_object = {
            #                     desc.text : spec.text 
            #                 }
            #                 print("SPECS OBJECT:", specs_object)
            #                 # product_specifications_list.append(specs_object)
            #                 return add_spec_and_desc(descs_list_param=local_descs[1:],specs_list_param=local_specs[1:])
            #         add_spec_and_desc(descs_list_param=descs,specs_list_param=specs)
            #         return add_product_specifications(prod_spec_lis[1:])
            # # print("PROD SPEC LIST:", product_specifications_list)
            # add_product_specifications(specifications)