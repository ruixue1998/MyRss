import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import re

def generate_rss():
    try:
        # Techmeme URL
        url = 'https://www.techmeme.com/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch page content
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize RSS feed generator
        fg = FeedGenerator()
        fg.title('Techmeme Top News')
        fg.link(href=url, rel='alternate')
        fg.description('The top news from Techmeme.com, updated automatically.')
        fg.language('en')

        # Find the main content block for top news
        top_news_container = soup.find(id='topcol1')

        if not top_news_container:
            print("Error: Could not find the top news container (id='topcol1').")
            return

        # Find all story blocks.
        story_blocks = top_news_container.find_all('div', recursive=False)

        for item in story_blocks:
            # The title and main link are in a 'div' with class 'itit'
            title_block = item.find('div', class_='itit')
            if not title_block:
                continue
            
            # The main link is the first link in the title block
            link_tag = title_block.find('a')
            if not link_tag or not link_tag.has_attr('href'):
                continue
            
            link = link_tag['href']
            
            # The title is the bold text
            title_tag = title_block.find('strong')
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)

            # The summary/description follows the title block
            summary_block = title_block.find_next_sibling('div')
            summary = ''
            if summary_block:
                summary = summary_block.get_text(strip=True)

            # Add entry to the feed
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(summary)
            # Use link as a unique ID
            fe.id(link)

        # Generate RSS feed and save to a file
        fg.rss_file('rss.xml', pretty=True)
        print("RSS feed 'rss.xml' generated successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_rss()