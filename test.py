from requests_html import HTMLSession
import requests

review_links = ['https://www.google.com/shopping/product/6222956906177139429/reviews?hl=en&q=bose+quietcomfort+45&prds=eto:3668158928628930488_0,pid:3011142393657177064,rate:5,rnum:10,rsk:PC_6093883722684573590&sa=X&ved=0ahUKEwiGjJrjr6D-AhWRFlkFHZ9SCFEQn08IWCgA', 'https://www.google.com/shopping/product/127770160929837065/reviews?hl=en&q=apple+airpods+max&prds=eto:487205171537148384_0,pid:1942015860405678420,rate:5,rnum:10,rsk:PC_7827190084446473420&sa=X&ved=0ahUKEwiUtcXjr6D-AhWSMlkFHeU-DzIQn08ITSgA']
for url in review_links:
    try:
        session = HTMLSession()
        response = session.get(url)
        print(url, response.status_code)

        css_identifier_result = ".z6XoBf"
        css_identifier_result_two = '.aALHge'
        results = response.html.find(css_identifier_result)
        result_two = response.html.find(css_identifier_result_two)
        reviews = []
        for result in results[:2]:
            # reviews_link = 'https://google.com' + result.find(css_all_reviews_link, first=True).attrs['href']  
            # title = result.find('.P3O8Ne', first=True).text
            date = result.find('.ff3bE', first=True).text
            if result.find('.g1lvWe div:nth-of-type(2)', first=True):
                content = result.find('.g1lvWe div:nth-of-type(2)', first=True).text.replace('\xa0Less', '')
            else:
                content = 'No review found'
            if result.find('.P3O8Ne', first=True) is not None:
                title = result.find('.P3O8Ne', first=True).text
            else:
                title = ' ----- '

            if result.find('.UzThIf'):
                rating = result.find('.UzThIf', first=True).attrs['aria-label']
            else:
                rating = 0
            
            if result.find('.sPPcBf'):
                source = result.find('.sPPcBf span')[1].text
            else:
                source = ' ----- '
            
            output = {
                    # 'review_count' : result.find(css_product_review_count, first=True).text,
                    'review_link': response.url,
                    'title' : title,
                    'rating' : rating,
                    'date' : date,
                    'content' : content[:200],
                    'source' : source,
            } 
            reviews.append(output)
        for result in result_two:
            if result.find('.vL3wxf'):
                rating_count = result.find('.vL3wxf', first=True).text
                print(rating_count)
            else:
                 rating_count = 'Sike'

        print(reviews)
        # for card in result_of_query['cards']:
        #     if card['all_reviews_link'] == url:
        #         card['reviews'] = reviews
        #     else:
        #         continue
    except requests.exceptions.RequestException as e:
                    print(e)