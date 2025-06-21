import requests
from bs4 import BeautifulSoup, Tag
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

def generate_verge_popular_atom():
    url = "https://www.theverge.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    fg = FeedGenerator()
    fg.id("https://www.theverge.com/rss/index.xml")
    fg.title("The Verge Most Popular")
    fg.subtitle("The Verge 首页 Most Popular 前5新闻")
    fg.link(href="https://www.theverge.com", rel="alternate")
    fg.link(href="https://www.theverge.com/rss/index.xml", rel="self")
    fg.language("en")
    fg.icon("https://platform.theverge.com/wp-content/uploads/sites/2/2025/01/verge-rss-large_80b47e.png?w=150&h=150&crop=1")
    fg.updated(datetime.now(timezone.utc))

    # 定位Most Popular区域
    most_popular = soup.find("h2", string=lambda s: 'Most Popular' in s if isinstance(s, str) else False)
    if not most_popular:
        print("未找到Most Popular区域")
        return

    # 获取5条新闻
    news_items = []
    for sib in most_popular.find_next_siblings():
        if isinstance(sib, Tag):
            if sib.name in ["ol", "ul"]:
                news_items = sib.find_all("li", limit=5)
                break
            elif sib.name == "div":
                news_items = sib.find_all("a", limit=5)
                break

    if not news_items:
        print("未找到Most Popular新闻条目")
        return

    for item in news_items:
        # 兼容li结构和a结构
        if isinstance(item, Tag) and item.name == "li":
            a = item.find("a")
        elif isinstance(item, Tag):
            a = item
        else:
            continue
        if not (isinstance(a, Tag) and a.has_attr("href")):
            continue
        link = a["href"]
        # 处理link为列表的情况
        if isinstance(link, list):
            link = link[0] if link else ""
        if not isinstance(link, str):
            continue
        if link.startswith("/"):
            link = "https://www.theverge.com" + link
        title = a.get_text(strip=True)
        # 尝试获取摘要
        desc = ""
        # 尝试获取作者和时间
        author = "The Verge"
        published = datetime.now(timezone.utc).isoformat()
        # 进入新闻详情页抓取摘要、作者、发布时间
        try:
            detail = requests.get(link, headers=headers, timeout=10)
            detail.raise_for_status()
            detail_soup = BeautifulSoup(detail.text, "html.parser")
            # 摘要
            desc_tag = detail_soup.find("meta", attrs={"name": "description"})
            if isinstance(desc_tag, Tag) and desc_tag.has_attr("content"):
                desc = desc_tag["content"]
            # 作者
            author_tag = detail_soup.find("meta", attrs={"name": "author"})
            if isinstance(author_tag, Tag) and author_tag.has_attr("content"):
                author = author_tag["content"]
            # 发布时间
            pub_tag = detail_soup.find("meta", attrs={"
