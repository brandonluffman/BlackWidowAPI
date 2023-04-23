import re
import datetime
from requests_html import HTMLSession


query = str(input("search: "))
orig_input = query
today = datetime.date.today()
year = today.year
match = re.search(f'{year}', query)

if 'best' not in query.lower() and match is None:
    query = 'best+' + query + '+2023'
elif match is None:
    query = query + '+2023'
elif 'best' not in query.lower():
    query = 'best+' + query
else:
    pass
domain =  "http://google.com/search?q="
# css_identifier_search_correction_div = 'DdVMXd'
css_identifier_search_correction = '.p64x9c'
session = HTMLSession()
response = session.get(domain+query)
correction_p_tag = response.html.find(css_identifier_search_correction, first=True)
print(correction_p_tag)
corrections = correction_p_tag.find('a.gL9Hy b')
correction_text = " ".join([tag.text for tag in corrections])
print("Original Search:", orig_input)
print("Correct Search:", correction_text)
query = query.replace(orig_input,correction_text)
print("SHOWING RESULTS FOR:", query)
# print("Correction:", correction)
# if correction is None:
#     print('correct')