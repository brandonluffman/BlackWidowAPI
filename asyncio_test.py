import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time

async def fetch_title(session, url):
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title').text
        return title

async def main():
    urls = ['https://example.com', 'https://google.com', 'https://github.com']
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_title(session, url) for url in urls]
        titles = await asyncio.gather(*tasks)
        print(titles)

if __name__ == '__main__':
    start_time = time.monotonic()
    asyncio.run(main())
    end_time = time.monotonic()
    print(f"Time elapsed: {end_time - start_time} seconds")