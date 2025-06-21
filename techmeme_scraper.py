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

        top_news_container = soup.find(id='topcol1')

        if not top_news_container:
            print("CRITICAL ERROR: Could not find the top news container with id='topcol1'.")
            fg.rss_file('rss.xml', pretty=True) # Write empty file to prevent Action failure
            return

        print("Successfully found news container with id='topcol1'.")
        
        # New Strategy: Find all title blocks directly, as they are the most reliable markers.
        title_blocks = top_news_container.find_all('div', class_='itit')
        print(f"Found {len(title_blocks)} title blocks (class='itit') using the new strategy.")

        if not title_blocks:
            print("CRITICAL ERROR: No title blocks were found. The site structure has likely changed significantly.")

        item_count = 0
        for title_block in title_blocks:
            # The title is in the <strong> tag inside the title block
            title_tag = title_block.find('strong')
            # The link is inside an <a> tag within the <strong> tag
            link_tag = title_tag.find('a') if title_tag else None
            
            # The summary/description is usually the next sibling div of the title_block
            summary_block = title_block.find_next_sibling('div')

            if link_tag and link_tag.has_attr('href') and summary_block:
                link = link_tag['href']
                title = title_tag.get_text(strip=True)
                summary = summary_block.get_text(strip=True)

                # Add entry to the feed
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=link)
                fe.description(summary)
                fe.id(link)
                item_count += 1

        print(f"Successfully processed and added {item_count} items to the feed.")

        fg.rss_file('rss.xml', pretty=True)
        print("RSS feed 'rss.xml' generated successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_rss()
