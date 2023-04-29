from requests_html import HTMLSession
import re
import requests
from timeit import default_timer as timer
from youtube_transcript_api import YouTubeTranscriptApi
import praw
from praw.models import MoreComments
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

result_of_query = {
    'links': {
        'affiliate': [],
        'reddit': [],
        'youtube': []
    }
}
urls = ['https://google.com/search?q=best+headphones+2023', 'https://google.com/search?q=best+headphones+2023+youtube', 'https://google.com/search?q=best+headphones+reddit']
serp_links = []

# # google_links = []
# # reddit_links = []

# t0= timer()
for url in urls:
    try:
        session = HTMLSession()
        response = session.get(url)
        # print(url, response.status_code)
        css_identifier_result = ".tF2Cxc"
        css_identifier_result_youtube = ".dFd2Tb"
        css_identifier_result = ".tF2Cxc"
        css_identifier_title = "h3"
        css_identifier_link = ".yuRUbf a"
        css_identifier_link_youtube = '.DhN8Cf a'
        css_identifier_text = ".VwiC3b"
        css_favicon = '.eqA2re img'

        results = response.html.find(css_identifier_result)
        youtube_results = response.html.find(css_identifier_result_youtube)

        
        if results: 
            for result in results[:8]:
                serp_link = result.find(css_identifier_link, first=True).attrs['href'] 
                serp_title = result.find(css_identifier_title, first=True).text
                if result.find(css_favicon):
                    serp_favicon = result.find(css_favicon, first=True).attrs['src']
                else:
                    serp_favicon = 'NA'
                serp_links.append({'link':serp_link,'title':serp_title,'favicon':serp_favicon})
        else:
            for youtube_result in youtube_results[:3]:
                serp_link = youtube_result.find(css_identifier_link_youtube, first=True).attrs['href']
                serp_title = result.find(css_identifier_title, first=True).text
                serp_links.append({'link':serp_link,'title':serp_title})

    except requests.exceptions.RequestException as e:
        print(e)

# t2 = timer()

# # print(serp_links)

youtube_serps = [serp_link for serp_link in serp_links if 'youtube.com' in serp_link['link']]
reddit_serps = [serp_link for serp_link in serp_links if 'reddit.com' in serp_link['link']]
affiliate_serps = [serp_link for serp_link in serp_links if ('reddit.com' not in serp_link['link']) and ('youtube.com' not in serp_link['link'])]
# print("YOUTUBE: -----------> ", youtube_serps)
# print("REDDIT: -------->", reddit_serps)
# print("AFFILIATE: ---------->", affiliate_serps)


# def add_youtube_data(serp_links):
#     links = serp_links
#     if len(serp_links) == 0:
#         print("YOUTUBE:", result_of_query['youtube'])
#         pass
#     else:
#         serp_link_data = links[0]
#         API_KEY = 'AIzaSyC3ElvfankD9Hf6ujrk3MUH1WIm_cu87XI'
#         VIDEO_ID = serp_link_data['link'].replace('https://www.youtube.com/watch?v=', '')
#         youtube = build('youtube', 'v3', developerKey=API_KEY)

#         try:
#             response = youtube.videos().list(
#                 part='snippet',
#                 id=VIDEO_ID
#             ).execute()

#             if response['items']:
#                 description = response['items'][0]['snippet']['description']
#             else:
#                 description = 'Nothing found'

#             disclaimer = 'disclaimer'
#             desc = description.replace('\n', '. ')
#             regex_pattern = r'http\S+|https\S+|#\w+|\d{1,2}:\d{2}|[^a-zA-Z0-9\s]+' # Matches timestamps, URLs, and hashtags
#             new_string = re.sub(regex_pattern, '', desc)
#             modified_string = re.sub(r'\s{2,}', '. ', new_string)
#             try:
#                 mod = modified_string[:modified_string.index(disclaimer)]
#             except:
#                 mod = modified_string
            
#             serp_link_data['text'] = mod

#         except HttpError as e:
#             print('An error occurred: %s' % e)
        
#         result_of_query['links']['youtube'].append(serp_link_data)
#         return add_youtube_data(links[1:])

# add_youtube_data(youtube_serps)

# t1 = timer()
# print(f'FINDING LINK TIME -------> {t2 - t0}')
# print(f'RECURSIVE MOTHERFUCKERRRRRR -------> {t2 - t1}')
# print(f'TOTAL TIME -------> {t1 - t0}')


def add_reddit_data(serp_links):
    links = serp_links
    if len(links) == 0:
        print("REDDIT:", result_of_query['reddit'])
        pass
    else:
        serp_link_data = links[0]
        reddit_read_only = praw.Reddit(client_id="6ziqexypJDMGiHf8tYfERA",         # your client id
                            client_secret="gBa1uvr2syOEbjxKbD8yzPsPo_fAbA",      # your client secret
                            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") 
        try:
            submission = reddit_read_only.submission(url=serp_link_data['link'])
        except:
            return add_reddit_data(links[1:])
        post_comments = []
        # comments = submission.comments[:10]
        def parse_comments(comments):
            comments_list = comments
            if len(comments_list) == 0:
                pass
            else:
                comment = comments_list[0]
                if type(comment) == MoreComments:
                    return parse_comments([comments_list[1:]])
                elif comment.body == '[removed]' or comment.body == '[deleted]' or comment.body[:6] == "Thanks":
                    return parse_comments([comments_list[1:]])
                else:
                    post_comments.append(comment.body.replace('\n', '').replace('\r', ''))
        
        parse_comments(submission.comments[:10])
        serp_link_data['comments'] = post_comments
        result_of_query['links']['reddit'].append(serp_link_data)
        return add_reddit_data(links[1:])
# add_reddit_data(reddit_serps)


# reddit_read_only = praw.Reddit(client_id="6ziqexypJDMGiHf8tYfERA",         # your client id
#                     client_secret="gBa1uvr2syOEbjxKbD8yzPsPo_fAbA",      # your client secret
#                     user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") 
# try:
#     submission = reddit_read_only.submission(url='https://www.reddit.com/r/HeadphoneAdvice/comments/sbx8h6/best_headphones_per_price_bracket/')
# except:
#     print('No')
# post_comments = []

# for comment in submission.comments[:10]:
#     if type(comment) == MoreComments:
#         continue
#     elif comment.body == '[removed]' or comment.body == '[deleted]' or comment.body[:6] == "Thanks":
#         pass
#     else:
#         post_comments.append(comment.body.replace('\n', '').replace('\r', ''))


affiliate_content = []
lister = []

def append_affiliate_content(headings):
    headings_list = headings
    if len(headings_list) == 0:
        return affiliate_content
    else:
        best = 'best'
        heading = headings_list[0]
        extract = heading.text.strip()
        if len(extract) > 10 and len(extract) < 200 and extract[-1] != '?' and best not in extract:
            affiliate_content.append(heading.text.strip().replace('\n', ''))
            return append_affiliate_content(headings_list[1:])
        else:
            return append_affiliate_content(headings_list[1:])

def append_lister_content(affiliate_content):
    affiliate_content_list = affiliate_content
    if len(affiliate_content_list) == 0:
        return lister
    else:
        sentence = affiliate_content_list[0]
        if sentence[-1] != '.' and sentence[-1] != '!' and sentence[-1] != '?':
            new_sentence = sentence + '.'
            lister.append(new_sentence)
            return append_lister_content(affiliate_content_list[1:])
        else:
            new_sentence = sentence
            lister.append(new_sentence)
            return append_lister_content(affiliate_content_list[1:])


def add_affiliate_data(serp_links):
    links = serp_links
    if len(links) == 0:
        print('AFFILIATE LINKS',result_of_query['links']['affiliate'])
        pass
    else:
        serp_link_data = links[0]
        try:
            headers = {
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            } 
            r = requests.get(serp_link_data['link'], headers=headers, timeout=2)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            lister = append_lister_content(affiliate_content=append_affiliate_content(soup.find_all(['h2','h3'])))
            final_content = " ".join(lister)
            serp_link_data['text'] = final_content
            result_of_query['links']['affiliate'].append(serp_link_data)

        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        return add_affiliate_data(links[1:])
add_affiliate_data(affiliate_serps)










        # for comment in submission.comments[:10]:
        #     if type(comment) == MoreComments:
        #         continue
        #     elif comment.body == '[removed]' or comment.body == '[deleted]' or comment.body[:6] == "Thanks":
        #         pass
        #     else:
        #         post_comments.append(comment.body.replace('\n', '').replace('\r', ''))
        # serp_link['comments'] = post_comments
        # result_of_query['links']['reddit'].append(serp_link)






# t2 = timer()
# for serp_link in serp_links:

#     if 'youtube.com' in serp_link['link']:
#         API_KEY = 'AIzaSyC3ElvfankD9Hf6ujrk3MUH1WIm_cu87XI'
#         VIDEO_ID = serp_link['link'].replace('https://www.youtube.com/watch?v=', '')
#         youtube = build('youtube', 'v3', developerKey=API_KEY)

#         try:
#             response = youtube.videos().list(
#                 part='snippet',
#                 id=VIDEO_ID
#             ).execute()

#             if response['items']:
#                 description = response['items'][0]['snippet']['description']
#             else:
#                 description = 'Nothing found'

#             disclaimer = 'disclaimer'
#             desc = description.replace('\n', '. ')
#             regex_pattern = r'http\S+|https\S+|#\w+|\d{1,2}:\d{2}|[^a-zA-Z0-9\s]+' # Matches timestamps, URLs, and hashtags
#             new_string = re.sub(regex_pattern, '', desc)
#             modified_string = re.sub(r'\s{2,}', '. ', new_string)
#             try:
#                 mod = modified_string[:modified_string.index(disclaimer)]
#             except:
#                 mod = modified_string
            
#             serp_link['text'] = mod

#         except HttpError as e:
#             print('An error occurred: %s' % e)
        
#         result_of_query['links']['youtube'].append(serp_link)
#         # print(transcript[:100])

    # elif 'reddit.com' in serp_link['link']:
    #     reddit_read_only = praw.Reddit(client_id="6ziqexypJDMGiHf8tYfERA",         # your client id
    #             client_secret="gBa1uvr2syOEbjxKbD8yzPsPo_fAbA",      # your client secret
    #             user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") 
    #     try:
    #         submission = reddit_read_only.submission(url=serp_link['link'])
    #     except:
    #         continue
    #     post_comments = []

    #     for comment in submission.comments[:10]:
    #         if type(comment) == MoreComments:
    #             continue
    #         elif comment.body == '[removed]' or comment.body == '[deleted]' or comment.body[:6] == "Thanks":
    #             pass
    #         else:
    #             post_comments.append(comment.body.replace('\n', '').replace('\r', ''))
    #     serp_link['comments'] = post_comments
    #     result_of_query['links']['reddit'].append(serp_link)
        # print(post_comments)

#     else:
#         try:
#             headers = {
#                         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#                         "Accept-Language": "en",
#                         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
#             } 
#             r = requests.get(serp_link['link'], headers=headers, timeout=2)
#             r.raise_for_status()
            
#             soup = BeautifulSoup(r.text, 'html.parser')
#             affiliate_content = []
#             best = 'best'
#             for heading in soup.find_all(["h2", "h3"]):
#                 extract = heading.text.strip()
#                 if len(extract) > 10 and len(extract) < 200 and extract[-1] != '?' and best not in extract:
#                     affiliate_content.append(heading.text.strip().replace('\n', ''))
#                 else:
#                     pass

#             lister = []

#             for sentence in affiliate_content:
#                 if sentence[-1] != '.' and sentence[-1] != '!' and sentence[-1] != '?':
#                     new_sentence = sentence + '.'
#                     lister.append(new_sentence)
#                 else:
#                     new_sentence = sentence
#                     lister.append(new_sentence)

#             final_content = " ".join(lister)
#             serp_link['text'] = final_content
#             result_of_query['links']['affiliate'].append(serp_link)

#         except requests.exceptions.RequestException as err:
#             print ("OOps: Something Else",err)
#         except requests.exceptions.HTTPError as errh:
#             print ("Http Error:",errh)
#         except requests.exceptions.ConnectionError as errc:
#             print ("Error Connecting:",errc)
#         except requests.exceptions.Timeout as errt:
#             print ("Timeout Error:",errt)

# t3 = timer()