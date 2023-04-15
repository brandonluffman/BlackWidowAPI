import requests
from requests_html import HTMLSession

domain = 'https://www.google.com/search?tbm=shop&hl=en&q='

entities = ['Cuisinart CPT-180P1 Metal Classic 4-Slice Toaster', 'BELLA 2 Slice Toaster']

entity_links = [domain + entity.replace(' ', '+') for entity in entities]
final_card_links = []
for url in entity_links:
    # print(url)
    try: 
        session = HTMLSession()
        response = session.get(url)
        print(url, response.status_code)
        css_identifier_results = ".i0X6df"
        css_identifier_link = "span a"
        css_identifier_test_2 = ".Ldx8hd a span"
        css_product_reviews = ".QIrs8"
        product_results = response.html.find(css_identifier_results)
        output = []
        link_count = 0
        ### For Loop Below loops through queries to find Shopping Link and Integer Representing Amounnt of Stores that are linked to that product ###
        for product_result in product_results:
            product_link = 'https://www.google.com' + product_result.find(css_identifier_link, first=True).attrs['href']
            product_compare = product_result.find(css_identifier_test_2, first=True)
            product_review_count = product_result.find(css_product_reviews, first=True).text

            if product_compare:
                product_compare = product_compare.text

                if product_compare.endswith('+'):
                    product_compare = product_compare[:-1]  

                    if len(product_review_count.split()) > 3:
                        review_num = int(product_review_count.split()[5].replace(',',''))
                    else:
                        review_num = False

                    if link_count < 3 and review_num:
                        cards = {
                        'Data' : product_link, 
                        'Count' : int(product_compare),
                        'Review Count' : review_num,
                        'entity': entities[entity_links.index(url)]
                        }
                        output.append(cards)
                        link_count += 1
                    else:
                        continue

        counts = []
        for out in output:
            data = [out['Count'], out['Review Count']]
            counts.append(data) 
        print(counts)

        count_list = []
        for c in counts:
            count_list.append(c[0])
    
        max_count = max(count_list)
        max_indexes = [i for i in range(len(count_list)) if count_list[i] == max_count]         
        index_len = len(max_indexes)
        if index_len == 1:
            max_index = max_indexes[0]

        max_review_count = []
        if index_len > 1:
            for max_index in max_indexes:
                max_review_count.append(counts[max_index][1])
            max_review = max(max_review_count)
            max_review_index = max_review_count.index(max_review)

            for count in counts:
                if max_review in count:
                    max_card = count     
        else:
            max_card = counts[max_index]

        indexer = counts.index(max_card)
        final_card = output[indexer]
        final_card_links.append(final_card)

        print(final_card_links)

    except requests.exceptions.RequestException as e:
            print(e)
