from requests_html import HTMLSession
import requests

# entities = ['uniqlo airism ultra']
entities = ['nike dri-fit reluxe boxer briefs', 'everlane boxer brief.', 'exofficio', 'hanes comfortflex waistband boxer brief', 'uniqlo airism ultra', 'j.crew stretch boxer briefs.', 'tommy john second skin relaxed fit boxer', 'calvin klein microfiber stretch boxer briefs', 'ralph lauren classic-fit boxer', 'saxx relaxed-fit boxer briefs']
domain = 'https://www.google.com/search?tbm=shop&hl=en&q='
entity_links = [(domain + entity.replace(' ', '+'),entity) for entity in entities]
final_card_links = []
for item in entity_links:
    # print(url)
    try: 
        url = item[0]
        entity = item[1]
        session = HTMLSession()
        response = session.get(url)
        print(url, response.status_code)
        css_identifier_results = ".i0X6df"
        css_identifier_link = "span a"
        css_identifier_test_2 = ".Ldx8hd a span"
        css_product_reviews = ".QIrs8"
        css_product_title = "span.C7Lkve div.EI11Pd h3.tAxDx"
        # product_results = [item for item in response.html.find(css_identifier_results) if (item.find(css_product_title, first=True) and all(elem in item.find(css_product_title, first=True).text.lower() for elem in entity.split()))] 
        product_results = response.html.find(css_identifier_results)

        # print(f'Product Results -----> {product_results}')
        output = []
        link_count = 0
        ### For Loop Below loops through queries to find Shopping Link and Integer Representing Amounnt of Stores that are linked to that product ###
        for product_result in product_results[:5]:
            print(product_result)
            product_link = 'https://www.google.com' + product_result.find(css_identifier_link, first=True).attrs['href']
            product_compare = product_result.find(css_identifier_test_2, first=True)
            product_review_count = product_result.find(css_product_reviews, first=True).text

            if product_compare:
                product_compare = product_compare.text
                # print(product_compare)

                if product_compare.endswith('+'):
                    product_compare = product_compare[:-1]  
                    # print(product_compare)

                    if len(product_review_count.split()) > 3:
                        review_num = int(product_review_count.split()[5].replace(',',''))
                    else:
                        review_num = False

                    if link_count < 3 and review_num:
                        cards = {
                        'Data' : product_link, 
                        'Count' : int(product_compare),
                        'Review Count' : review_num,
                        'entity': entity
                        }
                        output.append(cards)
                        link_count += 1
            else:
                continue

        if not output:
            final_card_links.append(product_results[0])
        else:
            counts = []
            for out in output:
                data = [out['Count'], out['Review Count']]
                counts.append(data) 
            print(counts)

            count_list = []
            for c in counts:
                count_list.append(c[0])
        
            max_count = max(count_list,default=0)
            max_indexes = [i for i in range(len(count_list)) if count_list[i] == max_count]         
            index_len = len(max_indexes)
            if index_len == 1:
                max_index = max_indexes[0]
            print('Index Len -----> ', index_len)
            
            print(index_len)

            max_review_count = []
            if index_len > 1:
                for max_index in max_indexes:
                    max_review_count.append(counts[max_index][1])
                max_review = max(max_review_count)
                max_review_index = max_review_count.index(max_review)
                print(f'Max-Review-index -----> {max_review_index}')   

                for count in counts:
                    if max_review in count:
                        max_card = count  
                        print(f'Max-Card -----> {max_card}')   
            else:
                print("Count Max Index ----->", counts[max_index])
                print("Counts ----->", counts)
                max_card = counts[max_index]

            indexer = counts.index(max_card)
            final_card = output[indexer]
            final_card_links.append(final_card)

        print(final_card_links)
        
    except requests.exceptions.RequestException as e:
            print(e)
    
               

