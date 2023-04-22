import json 
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from youtube_transcript_api import YouTubeTranscriptApi
import praw
from praw.models import MoreComments
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
    
    
# cats = ["Womens Bags", "Mens belts", "womens belts", "womens eyeglasses", "mens eyeglasses", "Mens sunglasses", "womens sunglasses", "beanies", "wallets", "mens hats", "womens hats", "womens necklaces", "mens chains", "mens bracelets", "womens bracelets", "womens earrings", "mens earrings", "mens rings", "womens rings", "Air Fryer", "Humidifier", "Comforter"]
# cats = ["Womens Bags"]
# cats = ["Over Ear Headphones", "Earbuds", "Smartphones", "Tablets", "Routers", "Cameras", "TV", "Laptop", "Bluetooth Speakers", "Smart Watches", "Home Security System", "Mens Jeans", "Womens Leggings", "Mens Cardigans", "Bras", "Womens Underwear", "Mens Underwear", "Mens Gym Shorts", "Mens gym shirts"]
cats = ["Blender", "Toaster", "Water Bottle", "Crock Pot", "Food Scale", "Skillet", "Grill", "Smoker", "Pellet Grills", "Food Storage Containers", "Beauty & Personal Care", "Sunscreen", "Body Lotion", "Face Lotion", "Deodorant", "Perfume", "Cologne", "Mens Razors", "Womens Razors", "Makeup Remover", "Mascara", "Lipstick", "Chapstick", "Nail Polish", "Blow Dryer", "Mens Electric Razor", "Exfoliator", "Men's Body Wash", "Women's Body Wash", "Womens Shampoo", "Men's Shampoo", "Womens Conditioner", "Mens Conditioner"]
queries = ['best+' + cat.replace(' ', '+') for cat in cats]

for query in queries:
    
    domain = "http://google.com/search?q="
    google_query = query
    reddit_query = (query + '+reddit').replace('+2023', '')
    youtube_query = (query + '+youtube')
    queries = [google_query, reddit_query, youtube_query]
    print(queries)
    urls = [domain + query for query in queries]
    serp_links = []
    final = []
    for url in urls:
        try:
            session = HTMLSession()
            response = session.get(url)
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
                "Accept-Language": "en-gb",
                "Accept-Encoding": "br,gzip,deflate",
                "Accept": "test/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            response.headers = headers       # <-- set default headers here

            print(url, response.status_code)

            css_identifier_result = ".tF2Cxc"
            css_identifier_result_youtube = ".dFd2Tb"
            css_identifier_link = ".yuRUbf a"
            css_identifier_link_youtube = '.DhN8Cf a'

            results = response.html.find(css_identifier_result)
            youtube_results = response.html.find(css_identifier_result_youtube)

            if results: 
                for result in results[:1]:
                    serp_link = result.find(css_identifier_link, first=True).attrs['href']
                    serp_links.append({'link':serp_link})
            else:
                for youtube_result in youtube_results[:1]:
                    serp_link = youtube_result.find(css_identifier_link_youtube, first=True).attrs['href']
                    serp_links.append({'link':serp_link})

        except requests.exceptions.RequestException as e:
            print(e)


    for serp_link in serp_links:
        if 'youtube.com' in serp_link['link']:
            API_KEY = 'AIzaSyC3ElvfankD9Hf6ujrk3MUH1WIm_cu87XI'
            VIDEO_ID = serp_link['link'].replace('https://www.youtube.com/watch?v=', '')
            youtube = build('youtube', 'v3', developerKey=API_KEY)

            desc_text = []
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
                    mod = modified_string[:modified_string.lower().index(disclaimer)]
                except:
                    mod = modified_string
                
                serp_link['text'] = mod
                         
                with open('annotation2.txt', "a") as f:
                    f.write(mod)
                    f.write('\n')
                    print('Done')

            except HttpError as e:
                mod = 'Error'
                print('An error occurred: %s' % e)   
            
            final.append(mod)
            print(f"Youtube -----> {mod}\n\n")


        elif 'reddit.com' in serp_link['link']:
            reddit_read_only = praw.Reddit(client_id="6ziqexypJDMGiHf8tYfERA",         # your client id
                    client_secret="gBa1uvr2syOEbjxKbD8yzPsPo_fAbA",      # your client secret
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36") 
            submission = reddit_read_only.submission(url=serp_link['link'])
                
            post_comments = []

            for comment in submission.comments[:5]:
                if type(comment) == MoreComments:
                    continue
                elif comment.body == '[removed]' or comment.body == '[deleted]' or comment.body[:6] == "Thanks":
                    pass
                else:
                    cbody = comment.body.replace('\n', '').replace('\r', '')
                    regex_pattern = r'http\S+|https\S+'
                    new_comment = re.sub(regex_pattern, '', cbody)
                    post_comments.append(new_comment)
                             
                    

            post = " ".join(post_comments)
            with open('annotation2.txt', "a") as f:
                        f.write(post)
                        f.write('\n')
                        print('Done')
            print(f"Reddit -----> {post}\n\n")
            final.append(post)

        else:
            headers = {
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            } 
            r = requests.get(serp_link['link'], headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            affiliate_content = []
            best = 'best'
            for heading in soup.find_all(["h2", "h3"]):
                extract = heading.text.strip()
                if len(extract) > 10 and len(extract) < 200 and extract[-1] != '?' and best not in extract.lower():
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
            with open('annotation2.txt', "a") as f:
                    f.write(final_content)
                    f.write('\n')
                    print('Done')
            final.append(final_content)
            print(f"Google -----> {final_content}\n\n")

    model = " ".join(final)
    # print(f"MODEL -----> \n {model}")
            
    # with open('annotation.txt', "a") as f:
    #     f.write(model)
    #     f.write('\n\n')
    #     print('Done')
        
