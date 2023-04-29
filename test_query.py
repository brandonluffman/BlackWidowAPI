# import re
# import datetime
from requests_html import HTMLSession
from tld import get_tld, get_fld
import requests




buying_links = ['https://google.com/shopping/product/6222956906177139429/offers?hl=en&q=bose+quietcomfort+45&prds=eto:3668158928628930488_0,pid:3011142393657177064,rsk:PC_6093883722684573590,scoring:p&sa=X&ved=0ahUKEwjw2p6YsaD-AhWIFlkFHcQDCqkQtKsGCHQ', 'https://google.com/shopping/product/127770160929837065/offers?hl=en&q=apple+airpods+max&prds=eto:487205171537148384_0,pid:1942015860405678420,rsk:PC_7827190084446473420,scoring:p&sa=X&ved=0ahUKEwi1htCYsaD-AhWHGVkFHWXtARsQtKsGCGw']

affiliate_domains = []
for url in buying_links:
    try:
        session = HTMLSession()
        response = session.get(url)
        # print(url, response.status_code)

        css_identifier_result = ".sg-product__dpdp-c"
        result = response.html.find(css_identifier_result,first=True)
        rows = result.find("div.kPMwsc a.b5ycib")

        for row in rows:
            tlder = row.attrs['href'][7:]
            if tlder[:1] == 'h':    
                res = get_fld(tlder)
                if res not in affiliate_domains:
                    affiliate_domains.append(res)
                else:
                    continue


    except requests.exceptions.RequestException as e:
            print(e)

print(affiliate_domains)


        # buying_options = list(set([a_tag.attrs['href'].replace('/url?q=','') for a_tag in rows]))
        # if table.find("a.b5ycib, shntl"):
        #     sold_by = list(set([urlparse(distrib.attrs['href'].replace('/url?q=','')).netloc for distrib in table.find("a.b5ycib, shntl")]))
        # else:
        #     sold_by = []
        # for card in result_of_query['cards']:
        #     if card['product_purchasing'] == url:
        #         card['buying_options'] = sold_by
        #     else:
        #         continue