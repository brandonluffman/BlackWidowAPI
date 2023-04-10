import requests
from requests_html import HTMLSession
import re
import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import praw
from praw.models import MoreComments


# headers={
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
#     "Accept-Language": "en-gb",
#     "Accept-Encoding": "br,gzip,deflate",
#     "Accept": "test/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
# }

# query = 'headphones'

# today = datetime.date.today()
# year = today.year
# match = re.search(f'{year}', query)
# if 'best' not in query.lower() and match is None:
#     query = 'best+' + query + '+2023'
# elif match is None:
#     query = query + '+2023'
# elif 'best' not in query.lower():
#     query = 'best+' + query
# else:
#     pass
# print(query)

# remove = re.sub('(\A|[^0-9])([0-9]{4,6})([^0-9]|$)', '', query)
# domain = "http://google.com/search?q="
# google_query = query
# reddit_query = (remove + '+reddit')
# youtube_query = (query + '+youtube') 
# queries = [google_query, reddit_query, youtube_query]
# urls = [domain + query for query in queries]
# serp_links = []
# for url in urls:
#     try:
#         session = HTMLSession()
#         response = session.get(url)
#         print(url, response.status_code)

#         css_identifier_result = ".tF2Cxc"
#         css_identifier_result_youtube = ".dFd2Tb"
#         css_identifier_result = ".tF2Cxc"
#         css_identifier_title = "h3"
#         css_identifier_link = ".yuRUbf a"
#         css_identifier_link_youtube = '.DhN8Cf a'
#         css_identifier_text = ".VwiC3b"

#         results = response.html.find(css_identifier_result)
#         youtube_results = response.html.find(css_identifier_result_youtube)

        
#         if results: 
#             for result in results[:1]:
#                 serp_link = result.find(css_identifier_link, first=True).attrs['href']
#                 serp_links.append(serp_link)
#         else:
#             for youtube_result in youtube_results[:1]:
#                 serp_link = youtube_result.find(css_identifier_link_youtube, first=True).attrs['href']
#                 serp_links.append(serp_link)

#     except requests.exceptions.RequestException as e:
#         print(e)

# print(serp_links)

# for serp_link in serp_links:

#     if 'youtube.com' in serp_link:
#         print('Youtube Link')
#         id = serp_link.replace('https://www.youtube.com/watch?v=', '')
#         transcript = YouTubeTranscriptApi.get_transcript(id)
#         text = ''
#         for i in transcript:
#             text = text + i['text'] + ' '
#         transcript = text
#         # print(transcript[:100])

#     elif 'reddit.com' in serp_link:
#         reddit_read_only = praw.Reddit(client_id="6ziqexypJDMGiHf8tYfERA",         # your client id
#                 client_secret="gBa1uvr2syOEbjxKbD8yzPsPo_fAbA",      # your client secret
#                 user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") 
#         submission = reddit_read_only.submission(url=serp_link)
            
#         post_comments = []

#         for comment in submission.comments[:10]:
#             if type(comment) == MoreComments:
#                 continue
#             elif comment.body == '[removed]' or comment.body == '[deleted]' or comment.body[:6] == "Thanks":
#                 pass
#             else:
#                 post_comments.append(comment.body.replace('\n', '').replace('\r', ''))
#         # print(post_comments)

#     else:
#         print('Google Link')
#         headers = {
#                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#                     "Accept-Language": "en",
#                     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
#         } 
#         r = requests.get(serp_link, headers=headers)
#         soup = BeautifulSoup(r.text, 'html.parser')
#         affiliate_content = []
#         for heading in soup.find_all(["p"]):
#             if len(heading.text.strip()) > 20:
#                 affiliate_content.append(heading.text.strip())
#             else:
#                 pass

#         lister = []

#         for sentence in affiliate_content:
#             if sentence[-1] != '.' and sentence[-1] != '!' and sentence[-1] != '?':
#                 new_sentence = sentence + '.'
#                 lister.append(new_sentence)
#             else:
#                 new_sentence = sentence
#                 lister.append(new_sentence)

#         final_content = " ".join(lister)

        # print(final_content)


### Render all data, then pass to spaCy endpoint [Pass Entities]








# entities = ['apple airpods max', 'bose quietcomfort 45']
# domain = 'https://www.google.com/search?tbm=shop&hl=en&q='

# entity_links = [domain + entity.replace(' ', '+') for entity in entities]

# for url in entity_links:
#     try: 
#         session = HTMLSession()
#         response = session.get(url)
#         print(url, response.status_code)
#         css_identifier_results = ".i0X6df"
#         css_identifier_link = "span a"
#         css_identifier_test_2 = ".Ldx8hd a span"
#         css_product_reviews = ".QIrs8"
#         product_results = response.html.find(css_identifier_results)
#         output = []
#         link_count = 0
#         ### For Loop Below loops through queries to find Shopping Link and Integer Representing Amounnt of Stores that are linked to that product ###
#         for product_result in product_results:
#             product_link = 'https://www.google.com' + product_result.find(css_identifier_link, first=True).attrs['href']
#             product_compare = product_result.find(css_identifier_test_2, first=True)
#             product_review_count = product_result.find(css_product_reviews, first=True).text
     
#             if product_compare:
#                 product_compare = product_compare.text

#                 if product_compare.endswith('+'):
#                     product_compare = product_compare[:-1]   

#                 if link_count < 3:
#                     cards = {
#                     'Data' : product_link, 
#                     'Count' : int(product_compare),
#                     'Review Count' : int(product_review_count.split()[5].replace(',',''))
#                     }
#                     output.append(cards)
#                     link_count += 1

#         counts = []
#         for out in output:
#            data = [out['Count'], out['Review Count']]
#            counts.append(data) 
#         print(counts)

#         count_list = []
#         for c in counts:
#             count_list.append(c[0])
       
#         max_count = max(count_list)
#         max_indexes = [i for i in range(len(count_list)) if count_list[i] == max_count]         
#         index_len = len(max_indexes)
#         if index_len == 1:
#             max_index = max_indexes[0]

#         max_review_count = []
#         if index_len > 1:
#             for max_index in max_indexes:
#                 max_review_count.append(counts[max_index][1])
#             max_review = max(max_review_count)
#             max_review_index = max_review_count.index(max_review)

#             for count in counts:
#                if max_review in count:
#                    max_card = count     
#         else:
#             max_card = counts[max_index]

#         indexer = counts.index(max_card)
#         final_card = output[indexer]
#         print(final_card)
            


#     except requests.exceptions.RequestException as e:
#         print(e)


card_urls = ['https://www.google.com/shopping/product/6222956906177139429?hl=en&q=bose+quietcomfort+45&prds=eto:3668158928628930488_0,pid:3011142393657177064,rsk:PC_6093883722684573590&sa=X&ved=0ahUKEwiAjYmZ25_-AhVJEFkFHbLnA68Q8wII1ws', 'https://www.google.com/shopping/product/127770160929837065?hl=en&q=apple+airpods+max&prds=eto:487205171537148384_0,pid:1942015860405678420,rsk:PC_7827190084446473420&sa=X&ved=0ahUKEwj-4fyX25_-AhXVD1kFHbvUAYQQ8wIIuQ4']


for url in card_urls:
    try:
        session = HTMLSession()
        response = session.get(url)
        print(url, response.status_code)
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
        css_buying_links = ".dOwBOc a"


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

        if ',' in product_review_count:
            product_review_count = product_review_count.replace(',', '')
        else:
            pass

        for result in results:
            reviews_link = 'https://google.com' + result.find(css_all_reviews_link, first=True).attrs['href']
            buying_link = 'https://'
            product_title = result.find(css_product_title, first=True).text
            output = {
                'product_title' : result.find(css_product_title, first=True),
                'product_description' : result.find(css_product_description, first=True),
                'product_rating' : result.find(css_product_rating, first=True).text,
                'review_count' : result.find(css_product_review_count, first=True).text,
                'product_img' : result.find(css_product_img, first=True).attrs['src'],
                'product_specs' : product_specifications_list,
                'all_reviews_link': reviews_link,
                'product_purchasing' : purchase_links
            } 

            print(output)
        
    except requests.exceptions.RequestException as e:
            print(e)







