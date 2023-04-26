import json
from collections import Counter
import spacy
from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup
import re

# nlp = spacy.load('./output/model-last')

# queries = ['best headphones 2023']
# urls = ["http://google.com/search?q=" + query for query in queries]
# serp_links = []
# for url in urls:
#         try:
#             session = HTMLSession()
#             response = session.get(url)
#             headers={
#                 "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
#                 "Accept-Language": "en-gb",
#                 "Accept-Encoding": "br,gzip,deflate",
#                 "Accept": "test/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#             }
#             response.headers = headers

#             css_identifier_result = ".tF2Cxc"
#             css_identifier_link = ".yuRUbf a"

#             results = response.html.find(css_identifier_result)

#             if results: 
#                 for result in results[:10]:
#                     serp_link = result.find(css_identifier_link, first=True).attrs['href']
#                     serp_links.append({'link':serp_link})

#         except requests.exceptions.RequestException as e:
#             print(e)

# final = []
# for serp_link in serp_links:
#         headers = {
#                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#                     "Accept-Language": "en",
#                     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
#         } 
#         r = requests.get(serp_link['link'], headers=headers)
#         soup = BeautifulSoup(r.text, 'html.parser')
#         affiliate_content = []
#         best = 'best'
#         for heading in soup.find_all(["h2", "h3"]):
#             extract = heading.text.strip()
#             if len(extract) > 10 and len(extract) < 200 and extract[-1] != '?' and best not in extract.lower():
#                 affiliate_content.append(heading.text.strip().replace('\n', ''))
#             else:
#                 pass

#         lister = []
#         for sentence in affiliate_content:
#             if sentence[-1] != '.' and sentence[-1] != '!' and sentence[-1] != '?' and sentence[-1] != ':':
#                 new_sentence = sentence + '.'
#                 lister.append(new_sentence)
#             else:
#                 new_sentence = sentence
#                 lister.append(new_sentence)

#         final_content = " ".join(lister)
#         final.append(final_content)
#         print(f"Google -----> {final_content}\n\n")

# model = " ".join(final)

# model_text = model
# # print(model_text)
# json_object = json.dumps(model_text)
# doc = nlp(json_object)
# print("doc.ents -------->", doc.ents)
# product_entities = [ent.text for ent in doc.ents if ent.label_ == "PRODUCT"]
# brand_entities = [ent.text for ent in doc.ents if ent.label_ == "BRAND"]
# print("product ents -------->", product_entities)
# print("brand ents -------->", brand_entities)

# items = [ent.text for ent in doc.ents if ent.label_ == "PRODUCT"]
items = ['Sony WH-1000XM5 mic demo', 'Sennheiser MOMENTUM 4 Wireless.', 'Sennheiser MOMENTUM 4 Wireless microphone demo', 'Sennheiser MOMENTUM 4 Wireless microphone demo', 'Sennheiser MOMENTUM 4 Wireless microphone demo', 'Bose Noise Cancelling Headphones 700 microphone demo', 'Bose Noise Cancelling Headphones 700 microphone demo', 'Bose Noise Cancelling Headphones 700 microphone demo', 'Sennheiser HD 6XX.', 'Sony WH-1000XM4.', 'Sony WF-C700N.', 'Sennheiser Momentum 4 Wireless.', 'Cambridge Audio Melomania 1 Plus.', 'Sony WH-1000XM5.', 'Sony WF-1000XM4 Wireless Earbuds.', 'Apple AirPods Pro 2.', 'Samsung Galaxy Buds 2 Pro.', '1More Triple Driver In-Ear Headphone.', 'SoundMAGIC E11BT.', 'Lypertek PurePlay Z3 2.0.', 'Bose Noise Cancelling Headphones 700.', 'Bose QuietComfort Earbuds.', 'Jabra Elite 45h.', 'Sony WH-CH510.', 'Focal Stellia.', 'Apple AirPods Pro (2nd Generation).', 'Bose QuietComfort 45.', 'Bose QuietComfort Earbuds II.', 'Jabra Elite 45h.', 'Sony WH-1000XM5.', 'Anker Soundcore Space A40.', 'Urbanista Los Angeles.', 'JBL Reflect Aero.', 'Sennheiser Momentum True Wireless 3.', 'Apple AirPods Pro (2nd Generation)', 'Bose QuietComfort 45.', 'Bose QuietComfort Earbuds II.', 'Jabra Elite 45h.', 'Sony WH-1000XM5.', 'Anker Soundcore Space A40.', 'Urbanista Los Angeles.', 'JBL Reflect Aero.', 'Sennheiser Momentum True Wireless 3.', 'Recommended by Our Editors.', 'Sony WH-1000XM5.', 'Audio-Technica ATH-M20xBT.', 'Bose QuietComfort 45.', 'Bose QuietComfort 45.', 'Sennheiser Momentum 4.', 'Sennheiser Momentum 4.', 'Sony WH-1000XM5.', 'Sony WH-1000XM4.', 'Sony WF-C500.', 'Apple AirPods Max.', 'Sony WF-1000XM4.', 'Panasonic RZ-S500W. 9.', 'Bose QuietComfort Earbuds II.', 'Apple AirPods Pro 2.', 'Austrian Audio Hi-X15.', 'Sennheiser Momentum True Wireless 3.', 'Cambridge Audio Melomania 1 Plus.', 'Mark Levinson No.', 'Shure Aonic 3.', 'Austrian Audio Hi-X55.', 'Sennheiser HD 250BT.', 'Sony WH-1000XM5.', 'Premium build and sound.', 'Bose 700.', 'Bowers & Wilkins Px8.', 'Sennheiser Momentum 4 Wireless.', 'Apple AirPods Max.', 'Apple AirPods Pro 2.', 'Bose QuietComfort Earbuds 2.', 'Bose QuietComfort 45.', 'Bose QuietComfort 45(opens', 'Bose 700(opens in a', 'Beats Fit Pro(opens', 'Amazon Echo Buds(opens in a new tab)', 'Sennheiser IE 300(opens in a new tab)', 'Sony WH-1000XM5(opens in a', 'Bose QuietComfort 45(opens', 'Bose 700(opens in a', 'Beats Fit Pro(opens', 'Amazon Echo Buds(opens in a new tab)', 'Sennheiser IE 300(opens in a new tab)', 'Sony WH-1000XM5(opens in a', 'Sony WH-1000XM5.', 'Adidas RPT-01.', 'Sennheiser Momentum 4.', 'Bowers & Wilkins Px8.', 'Apple AirPods Max.', 'Sennheiser HD 660S2.', '1More SonoFlow.', 'PuroQuiet Active Noise Cancelling Headphones.', 'Bose QuietComfort 45.', 'SteelSeries Arctis Nova Pro.', 'Sony WH-1000XM5.', 'Apple AirPods Pro 2.', 'Earfun Air S. Value noise-canceling earbuds with good sound.', 'Bose QuietComfort Earbuds 2.', 'Sennheiser Momentum True Wireless 3.', 'Beats Fit Pro.', 'Samsung Galaxy Buds 2 Pro.', 'Sony WF-1000XM4.', 'Sennheiser Momentum 4 Wireless.', 'Sony LinkBuds S.', 'JBL Live Pro 2.', 'Google Pixel Buds Pro.', 'Jabra Elite 7 Pro.', 'Apple AirPods Max.', "Apple's", 'Grado SR225x Prestige Series.', 'V-Moda M-200.']
# print("items -------->", items)
cleaned_items = []
for item in items:
    # print(item.split())
    cleaner_item = re.sub(r'\s{2,}|[^\w&\s]', '', item)
    cleaned_item = cleaner_item.lower()
    cleaned_items.append(cleaned_item)
    # print(cleaned_item)
    # print(cleaned_item.split())


ello = Counter(cleaned_items).most_common(10)
print(ello)
ellos = []
i = 0
for k,v in ello:
    print(k,v)
    ellos.append(k)
    i = i + v

print(i)
print('ELLLOS --------->', ellos)

entities = [entity for entity in ellos]
print(entities)