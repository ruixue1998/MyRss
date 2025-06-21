from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import sys

def generate_rss():
    fg = FeedGenerator()
    fg.title('Techmeme Top News')
    fg.link(href='https://www.techmeme.com/', rel='alternate')
    fg.description('The top news from Techmeme.com, updated automatically.')
    fg.language('en')

    try:
        with sync_playwright() as p:
            print("--- Launching browser to get real page content ---")
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto('https://www.techmeme.com/', wait_until='networkidle', timeout=60000)
            print("Page content fetched successfully.")
            html_content = page.content()
            browser.close()

        soup = BeautifulSoup(html_content, 'lxml')

        top_news_container = soup.find('div', id='topcol1')

        if not top_news_container:
            print("CRITICAL ERROR: Could not find id='topcol1'.")
            fg.rss_file('rss.xml', pretty=True)
            return

        print("Successfully found news container 'topcol1'. Parsing items...")
        
        item_count = 0
        # THIS IS THE FINAL, CORRECTED LOGIC BASED ON THE REAL HTML
        # Each story is now confirmed to be in a div with class 'clus'
        for story_cluster in top_news_container.find_all('div', class_='clus'):
            # The main link and title are in a nested structure
            title_tag = story_cluster.find('strong', class_='L1')
            if not title_tag:
                continue

            link_tag = title_tag.find('a', class_='ourh')
            if not (link_tag and link_tag.has_attr('href')):
                continue
            
            # The summary is the text immediately following the title's parent div
            summary_div = story_cluster.find('div', class_='ii')
            if not summary_div:
                continue
                
            # Extract text carefully, removing the title part from the summary
            full_text = summary_div.get_text(" ", strip=True)
            title_text = title_tag.get_text(" ", strip=True)
            summary_text = full_text.replace(title_text, '', 1).strip()
            # A common pattern is "— " starting the summary, let's clean that up
            if summary_text.startswith('—'):
                summary_text = summary_text[1:].strip()

            link = link_tag['href']
            
            fe = fg.add_entry()
            fe.title(title_text)
            fe.link(href=link)
            fe.description(summary_text)
            fe.id(link)
            item_count += 1

        print(f"--- SUCCESS ---")
        print(f"Processed and added {item_count} news items to the feed.")
        
        fg.rss_file('rss.xml', pretty=True)
        print("Final RSS feed 'rss.xml' has been generated.")

    except Exception as e:
        print(f"--- UNEXPECTED ERROR ---", file=sys.stderr)
        print(f"An error occurred: {e}", file=sys.stderr)
        fg.rss_file('rss.xml', pretty=True)

if __name__ == "__main__":
    generate_rss()
