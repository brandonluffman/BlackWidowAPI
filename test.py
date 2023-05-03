import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup



headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}
domain = 'https://google.com'
entity = 'aston martin'
url = 'https://www.google.com/search?tbm=shop&hl=en&q='
# url = 'https://www.google.com/shopping/product/11415085711667766387?hl=en&q=apple+airpods+max&prds=eto:3963812343973418838_0;8191234564920633265_0;353421421838069624_0,pid:13998887421003899116,rsk:PC_7069147378898153804&sa=X&ved=0ahUKEwibv_jGx779AhUXEFkFHcCeBlkQ9pwGCBk'
response = requests.get(url+entity, headers=headers)
print(response, response.url, response.status_code)
soup = BeautifulSoup(response.text, 'html.parser')
cards = soup.find_all('div', class_='sh-dgr__gr-auto', limit=3)
links = [domain+card.find('a', class_='Lq5OHe').attrs['href'] for card in cards if card.find('a', class_='iXEZD') and card.find('a', class_='Lq5OHe')]  
card_link = links[0] if links else soup.find("a", class_="Lq5OHe").attrs['href'] if soup.find("a", class_="Lq5OHe") else ''
res = requests.get(card_link, headers=headers)
print(res.url, res.status_code)

soup = BeautifulSoup(res.text, 'html.parser')
# img_div = soup.find('div', class_='Xkiaqc') if soup.find('div', class_='Xkiaqc') else soup.find('div', class_='TiQ3Vc') if soup.find('div', class_='TiQ3Vc') else ''
img_div = soup.find('div', class_='HRKRR') 
print(img_div)

prod_imgs = img_div.find_all('img') if img_div != '' else ''
prod_img = prod_imgs[0].attrs['src'] if prod_imgs != '' else 'hello'
print(prod_img)
# prod_img = prod_img[0].attrs['src']
product_rating = soup.find('div', class_='uYNZm').text if soup.find('div', class_='uYNZm') else ''
product_title = soup.find('span', class_='BvQan').text if soup.find('span', class_='BvQan') else ''
review_count = soup.find('span', class_='HiT7Id').text.replace('(', '').replace(')', '') if soup.find('span', class_='HiT7Id') else ''
prod_desc = soup.find("span", class_="sh-ds__full-txt").text if soup.find("span", class_="sh-ds__full-txt") else ''
final_card = {
    'id': 0,
    # 'rank': card_rank,
    # 'entity': entity,
    'product_url': url,
    'product_title': product_title,
    'product_description': prod_desc,
    'product_rating': product_rating,
    'review_count': review_count,
    'product_img': prod_img,
    'all_reviews_link': '---',
    'product_purchasing': '---',
    'mentions': {}
} 
print(final_card)