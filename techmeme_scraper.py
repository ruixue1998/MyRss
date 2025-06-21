import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def generate_rss():
    try:
        url = 'https://www.techmeme.com/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("Successfully fetched the page.")

        soup = BeautifulSoup(response.text, 'html.parser')

        fg = FeedGenerator()
        fg.title('Techmeme Top News')
        fg.link(href=url, rel='alternate')
        fg.description('The top news from Techmeme.com, updated automatically.')
        fg.language('en')

        # Find the main container for the top news column
        top_news_container = soup.find(id='topcol1')

        if not top_news_container:
            print("CRITICAL ERROR: Could not find the news container with id='topcol1'. The website layout has likely changed.")
            # Still create an empty file to prevent the GitHub Action from failing on the commit step
            fg.rss_file('rss.xml', pretty=True)
            return

        print("Successfully found news container 'topcol1'.")
        
        # New robust strategy: Find each story by looking for the headline and summary blocks together.
        item_count = 0
        
        # Each main story headline is in a <div class="itit"> with a <strong> tag inside.
        for title_block in top_news_container.find_all('div', class_='itit'):
            strong_tag = title_block.find('strong')
            if not strong_tag:
                continue

            link_tag = strong_tag.find('a')
            if not (link_tag and link_tag.has_attr('href')):
                continue

            # The summary is in the next sibling div, which has a class of 'iblk'
            summary_block = title_block.find_next_sibling('div', class_='iblk')
            if not summary_block:
                continue

            link = link_tag['href']
            title = link_tag.get_text(strip=True)
            
            # The actual summary text is inside a span with class 'par'
            summary_span = summary_block.find('span', class_='par')
            summary = summary_span.get_text(strip=True) if summary_span else summary_block.get_text(strip=True)
            
            # If we found all parts, add the entry to the feed
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(summary)
            fe.id(link) # Use the link as a unique ID for the entry
            item_count += 1

        print(f"Success! Processed and added {item_count} news items to the feed.")

        # Generate the RSS feed file
        fg.rss_file('rss.xml', pretty=True)
        print("RSS feed 'rss.xml' was generated successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error during network request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    generate_rss()
