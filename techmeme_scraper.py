import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def generate_rss():
    try:
        url = 'https://www.techmeme.com/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("--- SCRIPT START ---")
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
            print("--- !!! CRITICAL ERROR !!! ---")
            print("Could not find the news container with id='topcol1'. The website layout has likely changed.")
            fg.rss_file('rss.xml', pretty=True)
            return

        print("Successfully found news container 'topcol1'.")
        
        item_count = 0
        
        title_blocks = top_news_container.find_all('div', class_='itit')
        print(f"Found {len(title_blocks)} potential story headlines (divs with class='itit'). Now checking each one...")
        
        for i, title_block in enumerate(title_blocks):
            print(f"\n--- Checking Item #{i+1} ---")
            
            strong_tag = title_block.find('strong')
            if not strong_tag:
                print(f"Result for Item #{i+1}: REJECTED. Reason: No <strong> tag was found inside the title block.")
                continue
            print(f"Result for Item #{i+1}: Found <strong> tag.")

            link_tag = strong_tag.find('a')
            if not (link_tag and link_tag.has_attr('href')):
                print(f"Result for Item #{i+1}: REJECTED. Reason: No <a> tag with an 'href' was found inside the <strong> tag.")
                continue
            print(f"Result for Item #{i+1}: Found <a> tag with href: {link_tag.get('href')}")

            # Using find_next which is more robust than find_next_sibling
            summary_block = title_block.find_next('div', class_='iblk')
            if not summary_block:
                print(f"Result for Item #{i+1}: REJECTED. Reason: Could not find the summary block (div with class='iblk') after the title block.")
                continue
            print(f"Result for Item #{i+1}: Found summary block.")

            link = link_tag['href']
            title = link_tag.get_text(strip=True)
            summary = summary_block.get_text(strip=True) # Simplify summary extraction
            
            print(f"Result for Item #{i+1}: SUCCESS. Adding item to feed.")
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(summary)
            fe.id(link)
            item_count += 1

        print(f"\n--- SCRIPT FINISH ---")
        print(f"Processing complete. Added a total of {item_count} news items to the feed.")

        fg.rss_file('rss.xml', pretty=True)
        print("RSS feed 'rss.xml' was generated successfully.")

    except Exception as e:
        print(f"--- !!! UNEXPECTED ERROR !!! ---")
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    generate_rss()
