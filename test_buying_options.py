from requests_html import HTMLSession
import requests
from tld import get_tld
from urllib.parse import urlparse

buying_links = ['https://google.com/shopping/product/6222956906177139429/offers?hl=en&q=bose+quietcomfort+45&prds=eto:3668158928628930488_0,pid:3011142393657177064,rsk:PC_6093883722684573590,scoring:p&sa=X&ved=0ahUKEwjw2p6YsaD-AhWIFlkFHcQDCqkQtKsGCHQ', 'https://google.com/shopping/product/127770160929837065/offers?hl=en&q=apple+airpods+max&prds=eto:487205171537148384_0,pid:1942015860405678420,rsk:PC_7827190084446473420,scoring:p&sa=X&ved=0ahUKEwi1htCYsaD-AhWHGVkFHWXtARsQtKsGCGw']

for url in buying_links[:1]:
    try:
        session = HTMLSession()
        response = session.get(url)
        # print(url, response.status_code)

        css_identifier_result = ".sg-product__dpdp-c"
        result = response.html.find(css_identifier_result,first=True)
        table = result.find("#sh-osd__online-sellers-cont",first=True)
        rows = table.find("tr div.kPMwsc a")
        
        # buying_options = list(set([a_tag.attrs['href'].replace('/url?q=','') for a_tag in rows]))
        if table.find("a.b5ycib, shntl"):
            sold_by = list(set([urlparse(distrib.attrs['href'].replace('/url?q=','')).netloc for distrib in table.find("a.b5ycib, shntl")]))
            
            
        # for card in result_of_query['cards']:
        #     if card['product_purchasing'] == url:
        #         print(card['product_purchasing'])
        #         print(url)
        #         card['buying_options'] = buying_options
        #     else:
        #         continue
    
        # print(buying_options[:5])

#         hello = []
#         for test in buying_options:            
#             if test[0:5] == 'https':
#                 hello.append(test)
#             else:
#                 continue
# #
#         resers = []
#         for urler in hello:
#             res = get_tld(urler,as_object=True)
#             reser = res.fld
#             resers.append(reser)

#         i=0
#         newy = []
#         iland = []
#         for re in resers:
#             if re not in newy:
#                 newy.append(re)
#                 iland.append(hello[i])
#             else:
#                 continue
#             i +=1

#         # for card in result_of_query['cards']:
#         #     if card['product_purchasing'] == url:
#         #         card['buying_options'] = iland
#         #     else:
#         #         continue
#         print(iland)

    except requests.exceptions.RequestException as e:
            print(e)