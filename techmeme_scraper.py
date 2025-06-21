import httpx
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def generate_rss():
    url = 'https://www.techmeme.com/'
    # Use headers that mimic a real browser to avoid getting a blocked/simplified page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
    }

    try:
        # Use httpx which is more modern and can handle HTTP/2, similar to browsers
        with httpx.Client(http2=True, headers=headers, follow_redirects=True) as client:
            print(f"Fetching URL: {url}")
            response = client.get(url, timeout=30.0)
            # Raise an exception if we get an error status code (like 403 Forbidden or 503 Service Unavailable)
            response.raise_for_status()
            print("Successfully fetched the page.")

        soup = BeautifulSoup(response.text, 'html.parser')
        
        fg = FeedGenerator()
        fg.title('Techmeme Top News')
        fg.link(href=url, rel='alternate')
        fg.description('The top news from Techmeme.com, updated automatically.')
        fg.language('en')

        top_news_container = soup.find(id='topcol1')

        if not top_news_container:
            print("CRITICAL ERROR: Could not find the news container with id='topcol1'.")
            fg.rss_file('rss.xml', pretty=True)
            return

        print("Successfully found news container 'topcol1'.")
        
        item_count = 0
        # The most reliable pattern is that each story starts with a headline block (class 'itit')
        # and is followed by a story content block (class 'iblk')
        for title_block in top_news_container.find_all('div', class_='itit'):
            strong_tag = title_block.find('strong')
            if not strong_tag:
                continue

            link_tag = strong_tag.find('a')
            if not (link_tag and link_tag.has_attr('href')):
                continue

            # The summary is in the very next div, which should have the class 'iblk'
            summary_block = title_block.find_next_sibling('div', class_='iblk')
            if not summary_block:
                continue
            
            # The actual text is inside a span with class 'par'
            summary_span = summary_block.find('span', class_='par')
            if not summary_span:
                continue

            link = link_tag['href']
            title = link_tag.get_text(strip=True)
            summary = summary_span.get_text(strip=True)
            
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(summary)
            fe.id(link)
            item_count += 1

        print(f"Success! Processed and added {item_count} news items to the feed.")
        if item_count == 0:
            print("WARNING: 0 items were added. The site's HTML structure within 'topcol1' has likely changed.")

        fg.rss_file('rss.xml', pretty=True)
        print("RSS feed 'rss.xml' was generated successfully.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    generate_rss()
