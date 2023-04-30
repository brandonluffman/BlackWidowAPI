from requests_html import HTMLSession
from timeit import default_timer as timer
import requests

session = HTMLSession()

result_of_query = {
    'cards': []
}

domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
entities = ['Apple Airpods Max','Jabra Elite 45h']
entity_links = [(domain + entity.replace(' ', '+'),entity) for entity in entities]
    # print(entity_links)

    # session = HTMLSession()

buying_links = []
def generate_product_cards(entity_links,rank=1):
    local_entity_links = entity_links
    if len(local_entity_links) == 0:
        print("CARDS:",result_of_query['cards'])
        pass
    else:
        url = local_entity_links[0][0]
        entity = local_entity_links[0][1]
        response = session.get(url)
        card_link = 'https://www.google.com' + response.html.find(".C7Lkve a", first=True).attrs['href']
        card_rank = rank
        product_desc_response = session.get(card_link)
        css_identifier_result = ".sg-product__dpdp-c"
        css_product_img = ".wTvWSc img"
        css_product_title = ".YVQvvd .BvQan"
        css_product_description = ".Zh8lCd p .sh-ds__full .sh-ds__full-txt"
        css_product_rating = ".QKs7ff .uYNZm"
        css_all_reviews_link = ".k0e9E a"
        css_product_review_count = ".QKs7ff .qIEPib"
        css_buying_link = ".dOwBOc a"
        results = product_desc_response.html.find(css_identifier_result)
        def add_results(lis):
            # results_lis = lis
            print("RESULTS:", lis)
            if len(lis) == 0:
                pass
            else:
                result = lis[0]
                reviews_link = 'https://google.com' + result.find(css_all_reviews_link, first=True).attrs['href'] if result.find(css_all_reviews_link, first=True) else ' -- '
                buying_link = 'https://google.com' + result.find(css_buying_link, first=True).attrs['href'] if result.find(css_buying_link, first=True).attrs['href'] else ''
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
                    
                output = {
                    'id': 0,
                    'rank': card_rank,
                    'entity': entity,
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
                return add_results(lis[1:])
        add_results(results)
        return generate_product_cards(entity_links=local_entity_links[1:],rank=card_rank+1)
generate_product_cards(entity_links)





















# def add_product_card_links(entity_links):
#     final_card_links = []
#     for url, entity in entity_links:
#         response = session.get(url)
#         card_link = 'https://www.google.com' + response.html.find(".C7Lkve a", first=True).attrs['href']
#         final_card_links.append((card_link, entity))  
#     return final_card_links

# t9 = timer()
# print(f'SHOPPING CARD LOGIC v1 -------> {t9 - t8}')
# t10 = timer()

# buying_links = []
# review_links = []
# results = []
# def add_cards(card_links,rank=1):
#     try:
#         if len(card_links) == 0:
#             pass
#         else:
#             url = card_links[0][0]
#             entity = card_links[0][1]
#             card_rank = rank
#             response = session.get(url)
#             # print(url, response.status_code)
#             css_identifier_result = ".sg-product__dpdp-c"
#             css_product_img = ".wTvWSc img"
#             css_product_title = ".YVQvvd .BvQan"
#             css_product_description = ".Zh8lCd p .sh-ds__full .sh-ds__full-txt"
#             css_product_rating = ".QKs7ff .uYNZm"
#             css_all_reviews_link = ".k0e9E a"
#             css_product_review_count = ".QKs7ff .qIEPib"
#             css_buying_link = ".dOwBOc a"
#             results = response.html.find(css_identifier_result)

#             def add_results(lis):
#                 # results_lis = lis
#                 print("RESULTS:", lis)
#                 if len(lis) == 0:
#                     pass
#                 else:
#                     result = lis[0]
#                     reviews_link = 'https://google.com' + result.find(css_all_reviews_link, first=True).attrs['href'] if result.find(css_all_reviews_link, first=True) else ' -- '
#                     buying_link = 'https://google.com' + result.find(css_buying_link, first=True).attrs['href'] if result.find(css_buying_link, first=True).attrs['href'] else ''
#                     product_rating = result.find(css_product_rating, first=True).text if result.find(css_product_rating, first=True) else ''
#                     product_title = result.find(css_product_title, first=True).text if result.find(css_product_title, first=True) else ''
#                     review_count = int(result.find(css_product_review_count, first=True).text.replace(',','').replace(' reviews','').replace(' review', '')) if result.find(css_product_review_count, first=True) else ''

#                     buying_links.append(buying_link)
#                     review_links.append(reviews_link)
#                     if result.find(css_product_img, first=True):
#                         prod_img = result.find(css_product_img, first=True).attrs['src']
#                     else:
#                         prod_img = 'hello'
#                     if result.find(css_product_description, first=True):
#                         prod_desc = result.find(css_product_description, first=True).text
#                     else:
#                         prod_desc = ' ---- '
                        
#                     output = {
#                         'id': 0,
#                         'rank': card_rank,
#                         'entity': entity,
#                         'product_url': url,
#                         'product_title' : product_title,
#                         'product_description' : prod_desc,
#                         'product_rating' : product_rating,
#                         'review_count' : review_count,
#                         'product_img' : prod_img,
#                         # 'product_specs' : product_specifications_list,
#                         'all_reviews_link': reviews_link,
#                         'product_purchasing' : buying_link,
#                         'mentions': {}
#                     } 

#                     result_of_query['cards'].append(output)
#                     return add_results(lis[1:])
#             add_results(results)
#             return add_cards(card_links[1:],rank=card_rank+1)  
#     except requests.exceptions.RequestException as e:
#         print(e)
# add_cards(card_links=add_product_card_links(entity_links))