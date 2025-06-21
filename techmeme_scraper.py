import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import re

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
        print(f"Page Title: {soup.title.string}")

        fg = FeedGenerator()
        fg.title('Techmeme Top News')
        fg.link(href=url, rel='alternate')
        fg.description('The top news from Techmeme.com, updated automatically.')
        fg.language('en')

        top_news_container = soup.find(id='topcol1')

        if not top_news_container:
            print("DEBUG: CRITICAL ERROR - Could not find the top news container with id='topcol1'. Website layout has likely changed.")
            # Even if we fail, write an empty file so the Action doesn't fail on the commit step
            fg.rss_file('rss.xml', pretty=True)
            return

        print("DEBUG: Successfully found news container with id='topcol1'.")
        
        story_blocks = top_news_container.find_all('div', recursive=False)
        print(f"DEBUG: Found {len(story_blocks)} potential story blocks directly inside the container.")

        if not story_blocks:
            print("DEBUG: WARNING - The container was found, but no direct 'div' children were found. The structure inside the container might have changed.")

        item_count = 0
        for i, item in enumerate(story_blocks):
            title_block = item.find('div', class_='itit')
            if not title_block:
                # This helps to see which blocks are not story blocks
                # print(f"DEBUG: Block {i} has no title_block (class='itit'), skipping.")
                continue
            
            link_tag = title_block.find('a')
            title_tag = title_block.find('strong')
            summary_block = title_block.find_next_sibling('div')

            if link_tag and title_tag and summary_block:
                link = link_tag['href']
                title = title_tag.get_text(strip=True)
                summary = summary_block.get_text(strip=True)

                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=link)
                fe.description(summary)
                fe.id(link)
                item_count += 1
            else:
                print(f"DEBUG: Block {i} was identified as a story but was missing elements (link, title, or summary).")

        print(f"DEBUG: Successfully processed and added {item_count} items to the feed.")

        fg.rss_file('rss.xml', pretty=True)
        print("RSS feed 'rss.xml' generated successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_rss()
