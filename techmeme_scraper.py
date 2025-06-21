import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def generate_rss():
    try:
        url = 'https://www.techmeme.com/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        fg = FeedGenerator()
        fg.title('Techmeme Top News')
        fg.link(href=url, rel='alternate')
        fg.description('Techmeme.com Top News 自动更新')
        fg.language('en')

        # 定位Top News区域
        top_news_container = soup.find(id='topcol1')
        if not top_news_container:
            print("未找到Top News区域")
            return

        # 抓取每条新闻
        story_blocks = top_news_container.find_all('div', recursive=False)
        for item in story_blocks:
            title_block = item.find('div', class_='itit')
            if not title_block:
                continue
            link_tag = title_block.find('a')
            if not link_tag or not link_tag.has_attr('href'):
                continue
            link = link_tag['href']
            title_tag = title_block.find('strong')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            summary_block = title_block.find_next_sibling('div')
            summary = summary_block.get_text(strip=True) if summary_block else ''
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(summary)
            fe.id(link)

        fg.rss_file('rss.xml', pretty=True)
        print("RSS已生成：rss.xml")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    generate_rss()
