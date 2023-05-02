import requests
from requests_html import HTMLSession
from timeit import default_timer as timer

running = True

while running:
    query = input(f'Search? \n')
    session = HTMLSession()
    if query == 'quit':
        running = False
    else:
        t1 = timer()
        domain = 'https://www.google.com/search?q='
        response = session.get(domain, params={'q': query})
        div_element = response.html.find('a.gL9Hy', first=True)
        header_tags = response.html.find('.O3S9Rb')
        first_header_tags = [tag.text for tag in header_tags[:3]]

        if div_element is not None:
            correct_query = div_element.text
            print(f'CORRECTED QUERY: {correct_query}')
            if 'Shopping' in first_header_tags:
                print("VALID QUERY")
            else:
                print("INVALID QUERY")

        else:
            if 'Shopping' in first_header_tags:
                print("VALID QUERY")
            else:
                print("INVALID QUERY")

        t4 = timer()
        ti = t4 - t1
        print(f'Time -> ::: {ti}')
