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
import asyncio
from aiohttp import ClientSession
import aiohttp
# import requests_cache
from multiprocessing import Pool
from requests.exceptions import RequestException



### Affiliate ###
import concurrent.futures
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup

result_of_query = {
    'links': {
        'affiliate': [],
        'reddit': [],
        'youtube': []
    }
}
urls = ['https://google.com/search?q=best+ovens+2023', 'https://google.com/search?q=best+ovens+2023+youtube', 'https://google.com/search?q=best+ovens+2023+reddit']
serp_links = []

t0 = timer()

session = HTMLSession()
serp_links = []

for url in urls:
    try:
        response = session.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
        continue
    
    css_identifier_result = ".tF2Cxc"
    css_identifier_result_youtube = ".dFd2Tb"
    css_identifier_title = "h3"
    css_identifier_link = ".yuRUbf a"
    css_identifier_link_youtube = '.DhN8Cf a'
    css_identifier_text = ".VwiC3b"
    css_favicon = '.eqA2re img'

    results = response.html.find(css_identifier_result)
    youtube_results = response.html.find(css_identifier_result_youtube)

    if results: 
        serp_links += [{'link':result.find(css_identifier_link, first=True).attrs['href'],
                        'title':result.find(css_identifier_title, first=True).text,
                        'favicon':result.find(css_favicon, first=True).attrs['src'] if result.find(css_favicon) else 'NA'}
                       for result in results[:8]]
    else:
        serp_links += [{'link':youtube_result.find(css_identifier_link_youtube, first=True).attrs['href'],
                        'title':youtube_result.find(css_identifier_title, first=True).text}
                       for youtube_result in youtube_results[:3]]

session.close()

t1 = timer()
print(f'FINDING LINK TIME -------> {t1 - t0}')


youtube_serps = [serp_link for serp_link in serp_links if 'youtube.com' in serp_link['link']]
reddit_serps = [serp_link for serp_link in serp_links if 'reddit.com' in serp_link['link']]
affiliate_serps = [serp_link for serp_link in serp_links if ('reddit.com' not in serp_link['link']) and ('youtube.com' not in serp_link['link'])]


def add_youtube_data(serp_links):
    links = serp_links
    if len(serp_links) == 0:
        # print("YOUTUBE:", result_of_query['youtube'])
        pass
    else:
        serp_link_data = links[0]
        API_KEY = 'AIzaSyC3ElvfankD9Hf6ujrk3MUH1WIm_cu87XI'
        VIDEO_ID = serp_link_data['link'].replace('https://www.youtube.com/watch?v=', '')
        youtube = build('youtube', 'v3', developerKey=API_KEY)

        try:
            response = youtube.videos().list(
                part='snippet',
                id=VIDEO_ID
            ).execute()

            if response['items']:
                description = response['items'][0]['snippet']['description']
            else:
                description = 'Nothing found'

            disclaimer = 'disclaimer'
            desc = description.replace('\n', '. ')
            regex_pattern = r'http\S+|https\S+|#\w+|\d{1,2}:\d{2}|[^a-zA-Z0-9\s]+' # Matches timestamps, URLs, and hashtags
            new_string = re.sub(regex_pattern, '', desc)
            modified_string = re.sub(r'\s{2,}', '. ', new_string)
            try:
                mod = modified_string[:modified_string.index(disclaimer)]
            except:
                mod = modified_string
            
            serp_link_data['text'] = mod

        except HttpError as e:
            print('An error occurred: %s' % e)
        
        result_of_query['links']['youtube'].append(serp_link_data)
        return add_youtube_data(links[1:])

add_youtube_data(youtube_serps)

t2 = timer()
print(f'YOUTUBE RECURSIVE MOTHERFUCKERRRRRR -------> {t2 - t1}')

t3 = timer()

def add_reddit_data(serp_links):
    reddit_read_only = praw.Reddit(client_id="6ziqexypJDMGiHf8tYfERA",         # your client id
                        client_secret="gBa1uvr2syOEbjxKbD8yzPsPo_fAbA",      # your client secret
                        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") 
    
    for serp_link_data in serp_links:
        try:
            submission = reddit_read_only.submission(url=serp_link_data['link'])
        except:
            continue
        
        post_comments = []
        for comment in submission.comments:
            if isinstance(comment, MoreComments):
                continue
            if comment.body in ('[removed]', '[deleted]') or comment.body.startswith('Thanks'):
                continue
            post_comments.append(comment.body.replace('\n', '').replace('\r', ''))
            if len(post_comments) == 10:
                break
        
        serp_link_data['comments'] = post_comments
        # print(serp_link_data)
        result_of_query['links']['reddit'].append(serp_link_data)

add_reddit_data(reddit_serps)


# print("REDDIT", add_reddit_data(reddit_serps))

t4 = timer()
print(f'reddit RECURSIVE MOTHERFUCKERRRRRR -------> {t4 - t3}')


def add_affiliate_data(serp_links):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504 ])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    def process_link(serp_link):
        try:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            }
            r = session.get(serp_link['link'], headers=headers, timeout=1)
            r.raise_for_status()

            soup = BeautifulSoup(r.text, 'html.parser')
            affiliate_content = []
            best = 'best'
            for heading in soup.find_all(["h2", "h3"]):
                extract = heading.text.strip()
                if len(extract) > 10 and len(extract) < 200 and extract[-1] != '?' and best not in extract:
                    affiliate_content.append(heading.text.strip().replace('\n', ''))
                else:
                    pass

            lister = []

            for sentence in affiliate_content:
                if sentence[-1] != '.' and sentence[-1] != '!' and sentence[-1] != '?':
                    new_sentence = sentence + '.'
                    lister.append(new_sentence)
                else:
                    new_sentence = sentence
                    lister.append(new_sentence)

            final_content = " ".join(lister)
            serp_link['text'] = final_content
            # print(serp_link)
            result_of_query['links']['affiliate'].append(serp_link)

        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for serp_link in serp_links:
            futures.append(executor.submit(process_link, serp_link))
        concurrent.futures.wait(futures)

add_affiliate_data(affiliate_serps)


t5 = timer()
print(f'GOOGLE RECURSIVE FUNCTION -------> {t5 - t4}')
print(f'TOTAL TIME -------> {t5 - t0}')

# print(result_of_query['links'])
