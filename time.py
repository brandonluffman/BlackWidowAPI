import time
from timeit import default_timer as timer
import requests
from requests_html import HTMLSession

t16 = timer()

review_links = ['https://www.google.com/shopping/product/6222956906177139429/reviews?hl=en&q=bose+quietcomfort+45&prds=eto:3668158928628930488_0,pid:3011142393657177064,rate:5,rnum:10,rsk:PC_6093883722684573590&sa=X&ved=0ahUKEwiGjJrjr6D-AhWRFlkFHZ9SCFEQn08IWCgA', 'https://www.google.com/shopping/product/127770160929837065/reviews?hl=en&q=apple+airpods+max&prds=eto:487205171537148384_0,pid:1942015860405678420,rate:5,rnum:10,rsk:PC_7827190084446473420&sa=X&ved=0ahUKEwiUtcXjr6D-AhWSMlkFHeU-DzIQn08ITSgA']
for url in review_links:
    metrics = {
        'rating_count': {},
        'sentiment': [],
        'reviews': [],
    }
    try:
        import re
        session = HTMLSession()
        response = session.get(url)

        css_identifier_result = ".z6XoBf"
        results = response.html.find(css_identifier_result)
        reviews = []
        for result in results[:10]:    
            if result.find('.sPPcBf'):
                source = result.find('.sPPcBf span')[1].text
            else:
                source = ' ----- '
            
            output = {
                    'source' : source,
            } 
            metrics['reviews'].append(output)
        metrics['review_sources'] = list(set([item['source'] for item in metrics['reviews']]))
        css_identifier_result_two = '.aALHge'
        result_two = response.html.find(css_identifier_result_two)
        i = 5
        outerput = []
        for result in result_two:
            if result.find('.vL3wxf'):
                rating_count = result.find('.vL3wxf', first=True).text
                outerput.append(rating_count)

                i = i - 1
            else:
                rating_count = 'None'

        for i in range(len(outerput)):
            rating = f'{len(outerput) - i} stars' if len(outerput) - i > 1 else  f'{len(outerput) - i} star'
            review_count = int(outerput[i].replace(',','').replace(' reviews','').replace(' review', ''))
            metrics['rating_count'][rating] = review_count
        # reviews.append(outerput)

        sentimenter = []
        css_identifier_result_three = '.gKLqZc'
        result_three = response.html.find(css_identifier_result_three)
        count = 0
        for result in result_three[1:]:
            count+=1
            if result.find('.QIrs8'):
                start_word = 'about '
                end_word = '.'
                start = 'are '
                end = '.'
                sentiment_text = result.find('.QIrs8', first=True).text
                # print("TEXT", type(sentiment_text))
                pattern = r"\d+%|\d+"
                matches = re.findall(pattern, sentiment_text)
                start_index = sentiment_text.find(start_word)
                end_index = sentiment_text.find(end_word, start_index)
                result = sentiment_text[start_index+len(start_word):end_index]
                starter = sentiment_text.find(start)
                ender = sentiment_text.find(end, starter)
                resulter = sentiment_text[starter+len(start):ender]
                metrics['sentiment'].append({'favor_vote_count':matches[0], 'desc': result, 'favor_rating': matches[1]+' '+resulter})
                sentimenter.append([matches[0], result, matches[1]+' '+resulter])
            else:
                sentiment_text = 'None'
        
        print(sentimenter)

        # for card in result_of_query['cards']:
        #     if card['all_reviews_link'] == url:
        #         card['review_data'] = metrics
        #     else:
        #         continue
    except requests.exceptions.RequestException as e:
                    print(e)

t17 = timer()
print(f'REVIEWS -------> {t17 - t16}')