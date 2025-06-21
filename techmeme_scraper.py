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

        # Initialize the feed generator, but we don't expect it to have items yet.
        fg = FeedGenerator()
        fg.title('Techmeme Top News')
        fg.link(href=url, rel='alternate')
        fg.description('The top news from Techmeme.com, updated automatically.')
        fg.language('en')

        top_news_container = soup.find(id='topcol1')

        if not top_news_container:
            print("CRITICAL ERROR: Could not find the top news container with id='topcol1'.")
            # If the container isn't found, print the start of the whole page for debugging.
            print("\n\n--- DEBUG: PRINTING ENTIRE PAGE HTML (up to 5000 chars) ---")
            print(response.text[:5000])
            print("--- END OF HTML DEBUGGING ---\n\n")
        else:
            print("Successfully found news container with id='topcol1'.")
            # THIS IS THE MOST IMPORTANT STEP: Print the exact HTML we are working with.
            print("\n\n--- DEBUG: PRINTING HTML OF 'topcol1' CONTAINER ---")
            print(top_news_container.prettify())
            print("--- END OF HTML DEBUGGING ---\n\n")

        # We will still run the old logic to see what it outputs, but the main goal is the HTML print above.
        title_blocks = top_news_container.find_all('div', class_='itit') if top_news_container else []
        print(f"Attempting to find items... Found {len(title_blocks)} potential items.")

        item_count = 0
        for title_block in title_blocks:
            title_tag = title_block.find('strong')
            link_tag = title_tag.find('a') if title_tag else None
            summary_block = title_block.find_next_sibling('div')

            if link_tag and link_tag.has_attr('href') and summary_block:
                item_count += 1
        
        print(f"Logic test complete. Found {item_count} valid items based on current logic.")

        # Always write an empty file for now. The goal is the log, not the rss.xml.
        fg.rss_file('rss.xml', pretty=True)
        print("Diagnostic run complete. Please check the logs.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_rss()
